import streamlit as st
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader, UnstructuredPowerPointLoader
from langchain_text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

load_dotenv()

# --- Config & Style ---
st.set_page_config(page_title="ExamMacha", page_icon="🎓", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #2563eb; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎓 ExamMacha")
st.subheader("Your Last-Minute Engineering Savior")

# --- Sidebar ---
with st.sidebar:
    st.header("📂 Study Materials")
    uploaded_files = st.file_uploader("Upload Notes (PDF/PPTX)", accept_multiple_files=True, type=['pdf', 'pptx'])
    st.info("Tip: Upload the syllabus and 2-3 PYQs for best results.")

# --- RAG Core ---
def process_docs(files):
    all_docs = []
    for f in files:
        temp_path = f"temp_{f.name}"
        with open(temp_path, "wb") as buffer:
            buffer.write(f.getbuffer())
        
        if f.name.endswith(".pdf"):
            loader = PyPDFLoader(temp_path)
        else:
            loader = UnstructuredPowerPointLoader(temp_path)
        
        all_docs.extend(loader.load())
        os.remove(temp_path) # cleanup
    return all_docs

if uploaded_files:
    with st.spinner("Macha is reading your notes..."):
        docs = process_docs(uploaded_files)
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = splitter.split_documents(docs)
        
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = FAISS.from_documents(chunks, embeddings)
        
        # --- Custom Macha Prompt ---
        template = """
        You are 'Macha', a senior who has cleared this subject with an S-grade. 
        A junior is panicking because the exam is tomorrow. 
        Answer the question using the context provided. 
        If the answer isn't in the context, use your general knowledge but mention it's outside the notes.
        Use bullet points, bold key terms, and keep it extremely easy to understand.

        Context: {context}
        Question: {question}
        
        Macha's Advice:"""
        
        PROMPT = PromptTemplate(template=template, input_variables=["context", "question"])
        
        llm = ChatGroq(model="llama-3.1-70b-versatile", groq_api_key=os.getenv("GROQ_API_KEY"))
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(),
            chain_type_kwargs={"prompt": PROMPT}
        )
        st.success("Notes Loaded! Ask away.")

    # --- Chat UI ---
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if query := st.chat_input("Ask: 'What is 2-phase locking?' or 'Summarize Unit 3'"):
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            resp = qa_chain.invoke(query)["result"]
            st.markdown(resp)
            st.session_state.messages.append({"role": "assistant", "content": resp})
else:
    st.warning("👈 Please upload some documents in the sidebar to begin.")