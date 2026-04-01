import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader, UnstructuredPowerPointLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain


def process_documents(uploaded_files):
    all_docs = []
    failed_files = []

    for f in uploaded_files:
        temp_path = f"temp_{f.name}"
        try:
            with open(temp_path, "wb") as buffer:
                buffer.write(f.getbuffer())

            docs = []

            if f.name.lower().endswith(".pdf"):
                # Primary: PyPDFLoader
                try:
                    loader = PyPDFLoader(temp_path)
                    docs = loader.load()
                except Exception as e:
                    st.warning(f"⚠️ Primary loader failed for {f.name}: {e}")

                # Fallback: UnstructuredPDFLoader if primary got nothing
                if not docs or all(not d.page_content.strip() for d in docs):
                    try:
                        from langchain_community.document_loaders import UnstructuredPDFLoader
                        loader2 = UnstructuredPDFLoader(temp_path, mode="elements")
                        docs = loader2.load()
                        if docs:
                            st.info(f"ℹ️ Used fallback text extractor for {f.name}")
                    except Exception as e2:
                        st.warning(f"⚠️ Fallback loader also failed for {f.name}: {e2}")

            elif f.name.lower().endswith((".pptx", ".ppt")):
                try:
                    loader = UnstructuredPowerPointLoader(temp_path)
                    docs = loader.load()
                except Exception as e:
                    st.warning(f"⚠️ Could not load {f.name}: {e}")

            # Filter blank pages
            docs = [d for d in docs if d.page_content.strip()]

            if docs:
                all_docs.extend(docs)
            else:
                failed_files.append(f.name)
                st.error(
                    f"❌ **{f.name}** — no readable text found. "
                    "This looks like a scanned/image-based PDF. "
                    "Please export it as a text-based PDF, or paste your notes into a .txt file and rename it .pdf."
                )

        except Exception as e:
            st.error(f"❌ Unexpected error loading **{f.name}**: {e}")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    # Hard stop if nothing was extracted
    if not all_docs:
        raise ValueError(
            "No readable text could be extracted from any uploaded file.\n"
            "Tip: Make sure your PDF is not a scanned image. Try opening it, selecting text with Ctrl+A — if you can't select text, it's image-based."
        )

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(all_docs)

    if not chunks:
        raise ValueError(
            "Documents loaded but produced no usable chunks. "
            "The file may contain only images or negligible text."
        )

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return FAISS.from_documents(chunks, embeddings)


def get_doc_summary(vectorstore, api_key):
    """Generate a welcoming summary of the uploaded documents."""
    llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=api_key)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 6})
    docs = retriever.get_relevant_documents("main topics overview summary introduction")

    context = "\n\n".join([d.page_content for d in docs])
    prompt = f"""You are Macha, a friendly senior student helping juniors study.
A student just uploaded their notes. Based on the content below, write a SHORT, warm welcome message (3-5 sentences max).

Tell them:
1. What subject/topic the notes seem to be about
2. 3-4 key topics you spotted that they can ask about
3. Encourage them to ask anything!

Keep it friendly, concise, and use simple language. NO long paragraphs.

NOTES CONTENT:
{context}

Write the welcome message:"""

    response = llm.invoke(prompt)
    return response.content


def get_rag_chain(vectorstore, api_key, help_me_mode=False):
    llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=api_key)

    base_persona = (
        "You are 'Macha' — a brilliant, caring senior student helping juniors ace their exams. "
        "You speak simply, clearly, and always get to the point. "
        "You have access to TWO sources of information:\n"
        "  1. The student's uploaded NOTES (in {context})\n"
        "  2. Any WEB SEARCH results the student has enabled (passed in the human message)\n\n"
        "RULES:\n"
        "- If the answer is clearly in the NOTES, use that primarily.\n"
        "- If the human message contains '--- WEB SEARCH CONTEXT ---', use that web info to supplement your answer.\n"
        "- If neither has the answer, say: 'Macha couldn't find this in your notes or the web — try rephrasing!'\n"
        "- ALWAYS use bullet points, bold key terms, and keep answers structured.\n"
        "- NEVER give generic life advice. Always answer technically based on notes.\n"
        "- Be concise. No unnecessary filler. Get to what the student needs.\n"
    )

    maccha_help_addon = (
        "\n\n🆘 MACCHA HELP MODE IS ON — Use this EXACT format for EVERY answer:\n"
        "**1. First Understand (Buddy Logic)** — Explain in simple words what this topic means.\n"
        "**2. Definition** — One clear exam definition.\n"
        "**3. Concept Explanation** — 2-3 bullet points. Simple words only.\n"
        "**4. Formula** (if applicable) — Write clearly.\n"
        "**5. Example** — One simple example.\n"
            "**6. Exam Conclusion** — One line to memorize.\n\n"
        "⚡ BUDDY STYLE RULES:\n"
        "- First help student understand\n"
        "- Then move to exam answer\n"
        "- Keep friendly tone like a senior helping junior\n"
        "- No generic advice\n"
        "- Use only notes context\n"

    )

    if help_me_mode:
        system_content = base_persona + maccha_help_addon
    else:
        system_content = base_persona

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_content),
        ("human", "{input}")
    ])

    combine_docs_chain = create_stuff_documents_chain(llm, prompt)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    return create_retrieval_chain(retriever, combine_docs_chain)