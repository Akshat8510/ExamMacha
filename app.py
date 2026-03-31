import streamlit as st
import os
import numpy as np
from pypdf import PdfReader
from groq import Groq
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

# --- INITIALIZE ---
st.set_page_config(page_title="ExamMacha", page_icon="🎓")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
embed_model = SentenceTransformer('all-MiniLM-L6-v2')

st.title("🎓 ExamMacha (Lean Version)")

# --- 1. PDF EXTRACTION ---
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

# --- 2. CHUNKING & SEARCH ---
def create_chunks(text, chunk_size=1000):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def get_relevant_chunks(query, chunks, top_k=3):
    query_emb = embed_model.encode([query])
    chunk_embs = embed_model.encode(chunks)
    # Simple Cosine Similarity using Numpy
    similarities = np.dot(chunk_embs, query_emb.T).flatten()
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    return [chunks[i] for i in top_indices]

# --- UI SIDEBAR ---
with st.sidebar:
    st.header("📂 Notes")
    uploaded_files = st.file_uploader("Upload PDF", type="pdf", accept_multiple_files=True)
    if st.button("Reset Everything"):
        st.session_state.clear()
        st.rerun()

# --- MAIN LOGIC ---
if uploaded_files:
    if "chunks" not in st.session_state:
        with st.spinner("Macha is reading your PDFs..."):
            raw_text = get_pdf_text(uploaded_files)
            st.session_state.chunks = create_chunks(raw_text)
            st.success("Notes Loaded!")

    # --- CHAT UI ---
    if "messages" not in st.session_state: st.session_state.messages = []
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if query := st.chat_input("Ask Macha..."):
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"): st.markdown(query)

        with st.chat_message("assistant"):
            # RAG Search
            context_chunks = get_relevant_chunks(query, st.session_state.chunks)
            context = "\n".join(context_chunks)
            
            # Direct Groq Call (No LangChain!)
            response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": f"You are 'Macha', a helpful senior. Answer using this context: {context}"},
                    {"role": "user", "content": query}
                ]
            )
            ans = response.choices[0].message.content
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})

            # --- TOOLKIT (Simple Buttons) ---
            st.divider()
            if st.button("📝 Summarize these chunks"):
                summary = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[{"role": "user", "content": f"Summarize this for an exam: {context}"}]
                )
                st.info(summary.choices[0].message.content)

else:
    st.warning("👈 Upload a PDF to start.")