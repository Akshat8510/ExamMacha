import streamlit as st
from dotenv import load_dotenv
import os
import engine
import toolkit
import search

load_dotenv()

# --- 1. CONFIG ---
st.set_page_config(page_title="ExamMacha Studio", layout="wide")

# NotebookLM Styling
st.markdown("""
    <style>
    .stApp { background-color: #0f1115; color: #e2e8f0; }
    [data-testid="stSidebar"] { background-color: #1a1d23; border-right: 1px solid #334155; }
    .stButton>button { width: 100%; border-radius: 8px; height: 50px; background-color: #1e293b; color: white; border: 1px solid #334155; }
    .stButton>button:hover { background-color: #2563eb; border-color: #3b82f6; }
    </style>
    """, unsafe_allow_html=True)

api_key = os.getenv("GROQ_API_KEY")

# --- 2. LAYOUT ---
chat_col, studio_col = st.columns([2, 1], gap="large")

# LEFT: SIDEBAR (SOURCES)
with st.sidebar:
    st.title("📚 Sources")
    uploaded_files = st.file_uploader("Add study material", accept_multiple_files=True, type=['pdf', 'pptx'])
    st.markdown("---")
    web_enabled = st.toggle("🌐 Fast Research (Web)")
    help_me = st.toggle("🆘 HELP ME Mode")
    if st.button("🗑️ Clear Everything"):
        st.session_state.clear()
        st.rerun()

# CENTER: CHAT
with chat_col:
    st.title("🎓 ExamMacha Chat")
    if uploaded_files:
        if "vectorstore" not in st.session_state:
            with st.spinner("Indexing sources..."):
                st.session_state.vectorstore = engine.process_documents(uploaded_files)
        
        # Now passing help_me_mode correctly!
        rag_chain = engine.get_rag_chain(st.session_state.vectorstore, api_key, help_me_mode=help_me)

        chat_container = st.container(height=500)
        if "messages" not in st.session_state: st.session_state.messages = []
        
        with chat_container:
            for m in st.session_state.messages:
                with st.chat_message(m["role"]): st.markdown(m["content"])

        if query := st.chat_input("Ask about your notes..."):
            st.session_state.messages.append({"role": "user", "content": query})
            with chat_container:
                with st.chat_message("user"): st.markdown(query)
                with st.chat_message("assistant"):
                    final_input = query
                    if web_enabled:
                        web_context = search.perform_web_search(query)
                        final_input = f"Web Context: {web_context}\nQuestion: {query}"
                    
                    response = rag_chain.invoke({"input": final_input})
                    st.markdown(response["answer"])
                    st.session_state.messages.append({"role": "assistant", "content": response["answer"]})
    else:
        st.info("👈 Upload notes in the 'Sources' sidebar to start.")

# RIGHT: STUDIO
with studio_col:
    st.title("🎨 Studio")
    if uploaded_files and "vectorstore" in st.session_state:
        # TILE 1: FLASHCARDS
        if st.button("🗂️ Flashcards"):
            st.session_state.flash_raw = toolkit.generate_flashcards(rag_chain)
        if "flash_raw" in st.session_state:
            with st.expander("Flashcards", expanded=True):
                toolkit.display_flashcards(st.session_state.flash_raw)

        # TILE 2: QUIZ
        if st.button("📝 Practice Quiz"):
            st.session_state.quiz_raw = toolkit.generate_quiz(rag_chain)
        if "quiz_raw" in st.session_state:
            with st.expander("Quiz", expanded=True):
                st.markdown(st.session_state.quiz_raw)

        # TILE 3: MIND MAP
        if st.button("🧠 Mind Map"):
            st.session_state.map_raw = toolkit.generate_mindmap(rag_chain)
        if "map_raw" in st.session_state:
            with st.expander("Mind Map Code", expanded=True):
                mm = st.session_state.map_raw
                if "```mermaid" in mm: mm = mm.split("```mermaid")[1].split("```")[0]
                st.code(mm.strip(), language="mermaid")
    else:
        st.caption("Unlock studio tools by adding sources.")