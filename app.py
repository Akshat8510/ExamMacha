import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
import os
import engine, toolkit, search

load_dotenv()

# ═══════════════════════════════════════════
# 1. PAGE CONFIG
# ═══════════════════════════════════════════
st.set_page_config(
    page_title="PrepGraph Studio",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════
# 2. GLOBAL CSS — Premium Dark Exam Studio
# ═══════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ── Root Variables ── */
:root {
    --bg-base:       #080c14;
    --bg-surface:    #0d1117;
    --bg-elevated:   #161b22;
    --bg-card:       #1c2230;
    --border:        #21262d;
    --border-focus:  #3b82f6;
    --text-primary:  #e6edf3;
    --text-secondary:#8b949e;
    --text-muted:    #484f58;
    --accent-blue:   #3b82f6;
    --accent-purple: #a78bfa;
    --accent-green:  #22c55e;
    --accent-amber:  #f59e0b;
    --accent-red:    #ef4444;
    --accent-cyan:   #06b6d4;
    --glow-blue:     rgba(59,130,246,0.15);
    --glow-purple:   rgba(167,139,250,0.12);
}

/* ── Base ── */
.stApp {
    background: var(--bg-base) !important;
    font-family: 'DM Sans', sans-serif !important;
    color: var(--text-primary) !important;
}

/* Subtle grid background */
.stApp::before {
    content: '';
    position: fixed; inset: 0;
    background-image:
        linear-gradient(rgba(59,130,246,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(59,130,246,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none; z-index: 0;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--bg-surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * {
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Typography ── */
h1, h2, h3, h4 {
    font-family: 'Syne', sans-serif !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.02em;
}

/* ── Buttons ── */
.stButton > button {
    background: var(--bg-elevated) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    letter-spacing: 0.02em !important;
    padding: 10px 18px !important;
    transition: all 0.2s ease !important;
    width: 100%;
}
.stButton > button:hover {
    background: var(--accent-blue) !important;
    border-color: var(--accent-blue) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px var(--glow-blue) !important;
}

/* ── Chat Input ── */
.stChatInput > div {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}
.stChatInput > div:focus-within {
    border-color: var(--accent-blue) !important;
    box-shadow: 0 0 0 3px var(--glow-blue) !important;
}
.stChatInput input {
    color: var(--text-primary) !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Chat Messages ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 4px 0 !important;
}

/* ── File Uploader ── */
[data-testid="stFileUploader"] {
    background: var(--bg-elevated) !important;
    border: 1px dashed var(--border-focus) !important;
    border-radius: 10px !important;
    padding: 10px !important;
}

/* ── Radio ── */
.stRadio [data-testid="stMarkdownContainer"] p {
    color: var(--text-secondary) !important;
    font-size: 13px !important;
}

/* ── Toggle ── */
.stToggle p { color: var(--text-secondary) !important; font-size: 13px !important; }

/* ── Expander ── */
[data-testid="stExpander"] {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}
[data-testid="stExpander"] summary {
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg-surface); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

/* ── Spinner ── */
.stSpinner > div { border-top-color: var(--accent-blue) !important; }

/* ── Info / Warning ── */
.stAlert { border-radius: 10px !important; }

/* ── Container ── */
[data-testid="stVerticalBlock"] { gap: 0.4rem; }

/* ── Sidebar logo area ── */
.sidebar-logo {
    text-align: center;
    padding: 20px 0 12px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 16px;
}
.sidebar-logo .logo-text {
    font-family: 'Syne', sans-serif;
    font-size: 22px;
    font-weight: 800;
    background: linear-gradient(135deg, #3b82f6, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.02em;
}
.sidebar-logo .logo-sub {
    font-size: 11px;
    color: var(--text-muted);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 2px;
}

/* ── Section label ── */
.section-label {
    font-family: 'Syne', sans-serif;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 8px;
    margin-top: 16px;
}

/* ── Welcome card ── */
.welcome-card {
    background: linear-gradient(135deg, #0d1b35, #130d2e);
    border: 1px solid #1e3a5f;
    border-radius: 14px;
    padding: 24px 28px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}
.welcome-card::before {
    content: '';
    position: absolute;
    top: -50%; right: -20%;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(59,130,246,0.08) 0%, transparent 70%);
    pointer-events: none;
}

/* ── Maccha Help badge ── */
.maccha-badge {
    display: inline-block;
    background: linear-gradient(90deg, #7c3aed, #a78bfa);
    color: white;
    font-family: 'Syne', sans-serif;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    padding: 4px 10px;
    border-radius: 20px;
    text-transform: uppercase;
    margin-bottom: 8px;
}

/* ── Studio header ── */
.studio-header {
    font-family: 'Syne', sans-serif;
    font-size: 22px;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.03em;
    margin-bottom: 16px;
}

/* ── Tool card ── */
.tool-description {
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 12px;
    color: var(--text-secondary);
    margin-top: -4px;
    margin-bottom: 12px;
    line-height: 1.5;
}

/* ── Status pill ── */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 12px;
    color: var(--text-secondary);
}
.status-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--accent-green);
    animation: pulse-dot 2s infinite;
}
@keyframes pulse-dot {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

/* Web search indicator */
.web-indicator {
    background: #0d1f35;
    border: 1px solid #1e3a5f;
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 12px;
    color: #60a5fa;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Hide streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════
# 3. MERMAID RENDERER
# ═══════════════════════════════════════════
def render_mermaid(code: str):
    components.html(f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{ margin: 0; background: #0d1117; display: flex; justify-content: center; align-items: flex-start; padding: 20px; }}
        .mermaid {{ background: white; border-radius: 12px; padding: 24px; max-width: 100%; }}
        .mermaid svg {{ max-width: 100% !important; height: auto !important; }}
    </style>
    </head>
    <body>
    <div class="mermaid">{code}</div>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'default',
            mindmap: {{ padding: 20 }},
            securityLevel: 'loose'
        }});
    </script>
    </body>
    </html>
    """, height=550, scrolling=True)


# ═══════════════════════════════════════════
# 4. SIDEBAR
# ═══════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div class="logo-text">PrepGraph</div>
        <div class="logo-sub">AI Study Studio</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">📐 Layout</div>', unsafe_allow_html=True)
    view_mode = st.radio(
        "View",
        ["Dashboard", "Chat Focus", "Studio Focus"],
        label_visibility="collapsed"
    )

    st.markdown('<div class="section-label">📚 Study Material</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Drop PDFs or slides here",
        accept_multiple_files=True,
        type=['pdf', 'pptx'],
        label_visibility="collapsed"
    )

    st.markdown('<div class="section-label">⚙️ Intelligence</div>', unsafe_allow_html=True)
    web_enabled = st.toggle("🌐 Web Search", help="Enable real-time web search to supplement your notes")
    help_me_mode = st.toggle("🆘 MacchaHelp Mode", help="Structured exam format: Definition → Concept → Diagram → Formula → Conclusion")

    if help_me_mode:
        st.markdown("""
        <div style="background:#1a0f35; border:1px solid #4c1d95; border-radius:8px;
                    padding:10px 12px; margin-top:6px; font-size:11px; color:#c4b5fd; line-height:1.6;">
            <strong>📌 MacchaHelp Format</strong><br>
            1️⃣ Definition &nbsp; 2️⃣ Concept<br>
            3️⃣ Diagram &nbsp; 4️⃣ Formula<br>
            5️⃣ Exam Conclusion
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑️ Reset Everything"):
        st.session_state.clear()
        st.rerun()

    # Status indicator
    if "vectorstore" in st.session_state:
        st.markdown("""
        <div style="margin-top:16px;">
            <div class="status-pill">
                <div class="status-dot"></div>
                Notes Loaded
            </div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════
# 5. LAYOUT COLUMNS
# ═══════════════════════════════════════════
if view_mode == "Dashboard":
    chat_w, studio_w = 2.2, 1.0
elif view_mode == "Chat Focus":
    chat_w, studio_w = 1, 0.001
else:
    chat_w, studio_w = 0.001, 1

chat_col, studio_col = st.columns([chat_w, studio_w], gap="large")


# ═══════════════════════════════════════════
# 6. CHAT COLUMN
# ═══════════════════════════════════════════
with chat_col:
    if view_mode != "Studio Focus":

        # Header
        st.markdown("""
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:20px; padding-bottom:16px;
                    border-bottom:1px solid #21262d;">
            <div style="width:42px; height:42px; background:linear-gradient(135deg,#3b82f6,#a78bfa);
                        border-radius:12px; display:flex; align-items:center; justify-content:center;
                        font-size:22px;">🎓</div>
            <div>
                <div style="font-family:'Syne',sans-serif; font-size:20px; font-weight:800;
                            color:#f8fafc; letter-spacing:-0.02em;">PrepGraph Chat</div>
                <div style="font-size:12px; color:#8b949e;">Your AI senior is ready to help</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if uploaded_files:
            # Process documents
            file_names = tuple(f.name for f in uploaded_files)
            if "vectorstore" not in st.session_state or st.session_state.get("loaded_files") != file_names:
                with st.spinner("📖 Macha is reading your notes..."):
                    try:
                        st.session_state.vectorstore = engine.process_documents(uploaded_files)
                        st.session_state.loaded_files = file_names
                        st.session_state.messages = []
                        st.session_state.doc_summary = None
                    except ValueError as ve:
                        st.error(f"📄 **Could not load your file:**\n\n{ve}")
                        st.session_state.pop("vectorstore", None)
                        st.session_state.pop("loaded_files", None)
                        st.stop()

            if "vectorstore" not in st.session_state:
                st.stop()

            rag_chain = engine.get_rag_chain(
                st.session_state.vectorstore,
                os.getenv("GROQ_API_KEY"),
                help_me_mode=help_me_mode
            )

            # Auto-generate welcome message
            if "doc_summary" not in st.session_state or st.session_state.doc_summary is None:
                with st.spinner("🔍 Generating document overview..."):
                    summary = engine.get_doc_summary(
                        st.session_state.vectorstore,
                        os.getenv("GROQ_API_KEY")
                    )
                    st.session_state.doc_summary = summary
                    welcome_msg = {
                        "role": "assistant",
                        "content": summary
                    }
                    if not st.session_state.get("messages"):
                        st.session_state.messages = [welcome_msg]
                    elif st.session_state.messages[0]["role"] != "assistant":
                        st.session_state.messages.insert(0, welcome_msg)

            # Chat container
            chat_container = st.container(height=520)

            if "messages" not in st.session_state:
                st.session_state.messages = []

            with chat_container:
                for msg in st.session_state.messages:
                    with st.chat_message(msg["role"]):
                        if msg["role"] == "user":
                            st.markdown(f"**{msg['content']}**")
                        else:
                            if msg.get("is_web"):
                                st.markdown("""
                                <div class="web-indicator">🌐 Answer includes real-time web data</div>
                                """, unsafe_allow_html=True)
                            st.markdown(msg["content"])

            # Chat input
            if query := st.chat_input("Ask Macha anything from your notes..."):
                st.session_state.messages.append({"role": "user", "content": query})

                with chat_container:
                    with st.chat_message("user"):
                        st.markdown(f"**{query}**")
                    with st.chat_message("assistant"):
                        is_web_response = False
                        if web_enabled:
                            st.markdown("""
                            <div class="web-indicator">🌐 Searching the web for extra context...</div>
                            """, unsafe_allow_html=True)
                            with st.spinner("Combining notes + web..."):
                                web_context = search.perform_web_search(query)
                                final_input = (
                                    f"--- WEB SEARCH CONTEXT ---\n{web_context}\n\n"
                                    f"--- STUDENT QUESTION ---\n{query}"
                                )
                                is_web_response = True
                        else:
                            with st.spinner("Checking your notes..."):
                                final_input = query

                        with st.spinner("Macha is thinking..."):
                            response = rag_chain.invoke({"input": final_input})
                            answer = response["answer"]

                        st.markdown(answer)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "is_web": is_web_response
                        })

        else:
            # Empty state
            st.markdown("""
            <div class="welcome-card">
                <div style="font-size:48px; margin-bottom:16px;">📚</div>
                <div style="font-family:'Syne',sans-serif; font-size:22px; font-weight:800;
                            color:#f8fafc; margin-bottom:10px;">Welcome to PrepGraph!</div>
                <div style="color:#8b949e; font-size:14px; line-height:1.7; margin-bottom:16px;">
                    Your personal AI study senior — designed for every student who wants to
                    actually <strong style="color:#60a5fa;">understand</strong>, not just memorize.
                </div>
                <div style="color:#8b949e; font-size:13px; line-height:2;">
                    ✅ &nbsp;Upload your <strong style="color:#f1f5f9;">PDF notes or PPT slides</strong> in the sidebar<br>
                    ✅ &nbsp;Get a <strong style="color:#f1f5f9;">smart summary</strong> of your material instantly<br>
                    ✅ &nbsp;Ask anything — chat, quiz, flashcards, mind maps<br>
                    ✅ &nbsp;Turn on <strong style="color:#a78bfa;">MacchaHelp</strong> for exam-ready structured answers
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Feature cards
            cols = st.columns(2)
            features = [
                ("🗂️", "Flashcards", "Flip-card revision with exam tips"),
                ("📝", "Live Quiz", "5 MCQs with instant scoring"),
                ("🧠", "Mind Map", "Visual concept diagram"),
                ("🌐", "Web Search", "Supplement notes with live data"),
            ]
            for i, (icon, title, desc) in enumerate(features):
                with cols[i % 2]:
                    st.markdown(f"""
                    <div style="background:var(--bg-elevated); border:1px solid var(--border);
                                border-radius:10px; padding:14px 16px; margin-bottom:10px;">
                        <div style="font-size:22px; margin-bottom:6px;">{icon}</div>
                        <div style="font-family:'Syne',sans-serif; font-weight:700; color:#f1f5f9; font-size:14px;">{title}</div>
                        <div style="color:#8b949e; font-size:12px; margin-top:3px;">{desc}</div>
                    </div>
                    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════
# 7. STUDIO COLUMN
# ═══════════════════════════════════════════
with studio_col:
    if view_mode != "Chat Focus":
        st.markdown('<div class="studio-header">🎨 Studio</div>', unsafe_allow_html=True)

        if uploaded_files and "vectorstore" in st.session_state:
            rag_chain = engine.get_rag_chain(
                st.session_state.vectorstore,
                os.getenv("GROQ_API_KEY"),
                help_me_mode=help_me_mode
            )

            # ── FLASHCARDS ──
            st.markdown('<div class="section-label">Flashcards</div>', unsafe_allow_html=True)
            st.markdown('<div class="tool-description">🗂️ Generate flip-cards for key terms with exam tips built in.</div>', unsafe_allow_html=True)
            if st.button("🗂️ Generate Flashcards"):
                with st.spinner("Creating revision cards..."):
                    st.session_state.flash_raw = toolkit.generate_flashcards(rag_chain)
                    st.session_state.flipped = {}

            if "flash_raw" in st.session_state:
                with st.expander("📖 Revision Cards", expanded=True):
                    toolkit.display_flashcards(st.session_state.flash_raw)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── QUIZ ──
            st.markdown('<div class="section-label">Practice Quiz</div>', unsafe_allow_html=True)
            st.markdown('<div class="tool-description">📝 5 exam-style MCQs with instant scoring and explanations.</div>', unsafe_allow_html=True)
            if st.button("📝 Generate Quiz"):
                with st.spinner("Setting the exam paper..."):
                    st.session_state.quiz_raw = toolkit.generate_quiz(rag_chain)
                    st.session_state.quiz_submitted = False
                    st.session_state.quiz_answers = {}

            if "quiz_raw" in st.session_state:
                with st.expander("📋 Practice Exam", expanded=True):
                    toolkit.display_quiz(st.session_state.quiz_raw)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── MIND MAP ──
            st.markdown('<div class="section-label">Mind Map</div>', unsafe_allow_html=True)
            st.markdown('<div class="tool-description">🧠 Visual concept map of your entire topic at a glance.</div>', unsafe_allow_html=True)
            if st.button("🧠 Render Mind Map"):
                with st.spinner("Mapping your concepts..."):
                    st.session_state.map_raw = toolkit.generate_mindmap(rag_chain)

            if "map_raw" in st.session_state:
                with st.expander("🗺️ Concept Map", expanded=True):
                    raw = st.session_state.map_raw
                    if raw.startswith("graph") or raw.startswith("flowchart"):
                        st.info("📊 Rendering as flowchart (mindmap syntax fallback)")
                    toolkit.render_mindmap_fullscreen(raw)
                    if st.checkbox("Show Mermaid Code", key="show_mm_code"):
                        st.code(raw, language="text")

        else:
            st.markdown("""
            <div style="background:var(--bg-elevated); border:1px dashed var(--border);
                        border-radius:12px; padding:30px 20px; text-align:center; margin-top:20px;">
                <div style="font-size:32px; margin-bottom:10px;">🛠️</div>
                <div style="font-family:'Syne',sans-serif; font-weight:700; color:#f1f5f9; margin-bottom:6px;">
                    Studio Tools
                </div>
                <div style="color:#8b949e; font-size:13px; line-height:1.6;">
                    Upload your study material<br>to unlock all studio tools
                </div>
            </div>
            """, unsafe_allow_html=True)