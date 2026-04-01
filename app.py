import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
import os
import engine, toolkit, search

load_dotenv()

# --- 1. CONFIG & STYLE ---
st.set_page_config(page_title="ExamMacha Studio", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #0f1115; color: #e2e8f0; }
    [data-testid="stSidebar"] { background-color: #1a1d23; border-right: 1px solid #334155; }
    .chat-container { border: 1px solid #334155; border-radius: 15px; padding: 20px; background-color: #161b22; }
    .stButton>button { width: 100%; border-radius: 8px; height: 50px; background-color: #1e293b; color: white; border: 1px solid #334155; font-weight: bold; }
    .stButton>button:hover { background-color: #2563eb; border-color: #3b82f6; }
    h1, h2, h3 { color: #f8fafc; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MERMAID HELPER ---
def render_mermaid(code):
    components.html(
        f"""
        <div class="mermaid" style="background-color: white; padding: 20px; display: flex; justify-content: center;">
            {code}
        </div>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
        </script>
        """,
        height=600,
        scrolling=True
    )

# --- 3. SIDEBAR (SOURCES & VIEW) ---
with st.sidebar:
    st.title("📂 View Settings")
    view_mode = st.radio("Focus Mode", ["Dashboard (3-Col)", "Chat Focus", "Studio Focus"])
    
    st.markdown("---")
    st.title("📚 Sources")
    uploaded_files = st.file_uploader("Add study material", accept_multiple_files=True, type=['pdf', 'pptx'])
    
    st.markdown("---")
    st.title("🛠️ Intelligence")
    web_enabled = st.toggle("🌐 Fast Research (Web Search)")
    help_me = st.toggle("🆘 HELP ME Mode")
    
    if st.button("🗑️ Reset Application"):
        st.session_state.clear()
        st.rerun()

# --- 4. DYNAMIC LAYOUT LOGIC ---
if view_mode == "Dashboard (3-Col)":
    chat_width, studio_width = [2, 1.2]
elif view_mode == "Chat Focus":
    chat_width, studio_width = [4, 0.01]
else:
    chat_width, studio_width = [0.01, 4]

chat_col, studio_col = st.columns([chat_width, studio_width], gap="large")

# --- 5. CENTER: CHAT INTERFACE ---
with chat_col:
    if view_mode != "Studio Focus":
        st.title("🎓 ExamMacha Chat")
        
        if uploaded_files:
            if "vectorstore" not in st.session_state:
                with st.spinner("Macha is scanning your notes..."):
                    st.session_state.vectorstore = engine.process_documents(uploaded_files)
            
            rag_chain = engine.get_rag_chain(st.session_state.vectorstore, os.getenv("GROQ_API_KEY"), help_me_mode=help_me)

            chat_placeholder = st.container(height=600)
            if "messages" not in st.session_state: st.session_state.messages = []
            
            with chat_placeholder:
                for m in st.session_state.messages:
                    with st.chat_message(m["role"]):
                        # Make user queries BIG and BOLD
                        st.markdown(f"### {m['content']}" if m["role"] == "user" else m["content"])

            if query := st.chat_input("Ask anything..."):
                st.session_state.messages.append({"role": "user", "content": query})
                with chat_placeholder:
                    with st.chat_message("user"): st.markdown(f"### {query}")
                    with st.chat_message("assistant"):
                        with st.spinner("Checking sources..."):
                            final_input = query
                            if web_enabled:
                                st.caption("🌐 Searching the internet...")
                                web_context = search.perform_web_search(query)
                                final_input = f"--- WEB SEARCH CONTEXT ---\n{web_context}\n\n--- USER QUESTION ---\n{query}"
                            
                            response = rag_chain.invoke({"input": final_input})
                            st.markdown(response["answer"])
                            st.session_state.messages.append({"role": "assistant", "content": response["answer"]})
        else:
            st.info("👈 Macha is ready! Upload your notes in the sidebar to start.")

# --- 6. RIGHT: STUDIO TOOLS ---
with studio_col:
    if view_mode != "Chat Focus":
        st.title("🎨 Studio")
        
        if uploaded_files and "vectorstore" in st.session_state:
            # FLASHCARDS
            if st.button("🗂️ Flashcards"):
                st.session_state.flash_raw = toolkit.generate_flashcards(rag_chain)
            if "flash_raw" in st.session_state:
                with st.expander("REVISION CARDS", expanded=True):
                    toolkit.display_flashcards(st.session_state.flash_raw)

            # QUIZ
            if st.button("📝 Quick Quiz"):
                st.session_state.quiz_raw = toolkit.generate_quiz(rag_chain)
            if "quiz_raw" in st.session_state:
                with st.expander("PRACTICE QUIZ", expanded=True):
                    st.markdown(st.session_state.quiz_raw)

            # MIND MAP
            if st.button("🧠 Render Mind Map"):
                st.session_state.map_raw = toolkit.generate_mindmap(rag_chain)
            if "map_raw" in st.session_state:
                with st.expander("VISUAL CONCEPT MAP", expanded=True):
                    mm_code = st.session_state.map_raw
                    # Robust cleaning of LLM text
                    if "```mermaid" in mm_code: mm_code = mm_code.split("```mermaid")[1].split("```")[0]
                    elif "```" in mm_code: mm_code = mm_code.split("```")[1].split("```")[0]
                    render_mermaid(mm_code.strip())
        else:
            st.caption("Upload sources to unlock tools.")