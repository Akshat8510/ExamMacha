import streamlit as st
import streamlit.components.v1 as components
import re
import html as html_lib


# ─────────────────────────────────────────
# FLASHCARD GENERATION & DISPLAY
# ─────────────────────────────────────────

def generate_flashcards(chain):
    prompt = (
        "From the uploaded notes, extract exactly 6 important key terms or concepts. "
        "For each one, write a flashcard in this EXACT format (one per line):\n"
        "TERM | SIMPLE_DEFINITION | EXAM_TIP\n\n"
        "Rules:\n"
        "- TERM: The keyword or concept name only — plain text, no markdown\n"
        "- SIMPLE_DEFINITION: ONE plain-text sentence, no HTML, no special characters\n"
        "- EXAM_TIP: A one-line plain-text memory trick or exam hint\n"
        "Output ONLY the pipe-separated lines. No headers, no extra text, no markdown, no asterisks."
    )
    res = chain.invoke({"input": prompt})
    return res["answer"]


def display_flashcards(raw_text: str):
    # Strip markdown bold/italic before parsing
    clean = re.sub(r'\*+', '', raw_text)
    lines = [l.strip() for l in clean.strip().split("\n") if "|" in l]

    if not lines:
        st.warning("Could not parse flashcards. Try regenerating.")
        return

    if "flipped" not in st.session_state:
        st.session_state.flipped = {}

    for i, line in enumerate(lines):
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 2:
            continue

        # Escape to prevent HTML injection from LLM output
        term       = html_lib.escape(parts[0])
        definition = html_lib.escape(parts[1])
        tip        = html_lib.escape(parts[2]) if len(parts) > 2 else ""

        is_flipped  = st.session_state.flipped.get(i, False)
        flip_label  = "👁️ Hide Answer" if is_flipped else "👁️ Reveal Answer"
        card_bg     = "#0d3320" if is_flipped else "#0f2744"
        border_col  = "#22c55e" if is_flipped else "#3b82f6"
        badge_text  = "DEFINITION" if is_flipped else "TERM"
        badge_color = "#22c55e" if is_flipped else "#3b82f6"

        card_html = f"""
        <div style="background:{card_bg}; border:1.5px solid {border_col}; border-radius:12px;
                    padding:18px 20px; margin-bottom:6px;">
            <span style="background:{badge_color}; color:#fff; font-size:10px; font-weight:700;
                         padding:3px 10px; border-radius:20px; letter-spacing:1px; text-transform:uppercase;">
                {badge_text}
            </span>
            <div style="margin-top:12px; font-size:17px; font-weight:700; color:#f1f5f9; line-height:1.4;">
                {term}
            </div>"""

        if is_flipped:
            card_html += f"""
            <div style="margin-top:10px; font-size:14px; color:#cbd5e1; line-height:1.6;">
                {definition}
            </div>"""
            if tip:
                card_html += f"""
            <div style="margin-top:12px; background:#102010; border-left:3px solid #22c55e;
                         padding:9px 13px; border-radius:6px; font-size:12px; color:#86efac; line-height:1.5;">
                ⚡ <strong>Exam Tip:</strong> {tip}
            </div>"""

        card_html += "</div>"

        st.markdown(card_html, unsafe_allow_html=True)
        if st.button(flip_label, key=f"flip_{i}"):
            st.session_state.flipped[i] = not is_flipped
            st.rerun()
        st.markdown("<div style='margin-bottom:4px;'></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────
# QUIZ GENERATION & DISPLAY
# ─────────────────────────────────────────

def generate_quiz(chain):
    prompt = (
        "Create a 5-question Multiple Choice Quiz from the uploaded notes.\n"
        "Use this EXACT format for each question — no deviations:\n\n"
        "Q1. [Question text]\n"
        "A) [Option A]\n"
        "B) [Option B]\n"
        "C) [Option C]\n"
        "D) [Option D]\n"
        "ANSWER: [Single letter, e.g. B]\n"
        "EXPLANATION: [One plain sentence explaining why]\n\n"
        "Repeat for Q2, Q3, Q4, Q5.\n"
        "Rules: plain text only, no markdown, no bold, no asterisks. Output ONLY the quiz."
    )
    res = chain.invoke({"input": prompt})
    return res["answer"]


def _parse_quiz(raw_text: str):
    """Robustly parse quiz text into list of question dicts."""
    text = re.sub(r'\*+', '', raw_text)
    questions = []
    blocks = re.split(r'(?:^|\n)\s*Q(\d+)[.)]\s*', text.strip())
    # blocks alternates: ['preamble', '1', 'content', '2', 'content', ...]
    i = 1
    while i < len(blocks) - 1:
        content = blocks[i + 1].strip() if i + 1 < len(blocks) else ""
        lines = [l.strip() for l in content.split("\n") if l.strip()]
        if not lines:
            i += 2
            continue

        q_text = lines[0]
        options = {}
        answer = ""
        explanation = ""

        for line in lines[1:]:
            mo = re.match(r'^([A-D])[.)]\s*(.+)', line)
            if mo:
                options[mo.group(1)] = mo.group(2).strip()
            elif re.match(r'^ANSWER\s*:', line, re.IGNORECASE):
                raw_ans = re.sub(r'^ANSWER\s*:\s*', '', line, flags=re.IGNORECASE).strip()
                answer = raw_ans[0].upper() if raw_ans else ""
            elif re.match(r'^EXPLANATION\s*:', line, re.IGNORECASE):
                explanation = re.sub(r'^EXPLANATION\s*:\s*', '', line, flags=re.IGNORECASE).strip()

        if q_text and len(options) >= 2 and answer:
            questions.append({
                "question":    html_lib.escape(q_text),
                "options":     {k: html_lib.escape(v) for k, v in options.items()},
                "answer":      answer,
                "explanation": html_lib.escape(explanation),
            })
        i += 2

    return questions


def display_quiz(raw_text: str):
    if "quiz_answers" not in st.session_state:
        st.session_state.quiz_answers = {}
    if "quiz_submitted" not in st.session_state:
        st.session_state.quiz_submitted = False

    questions = _parse_quiz(raw_text)

    if not questions:
        st.warning("Could not parse quiz questions. Try regenerating.")
        with st.expander("Raw output (debug)"):
            st.code(raw_text)
        return

    total = len(questions)

    # ── Header ──
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0d1b35,#130d2e); border:1px solid #1e3a5f;
                border-radius:14px; padding:16px 20px; margin-bottom:16px;">
        <div style="font-size:17px; font-weight:800; color:#f8fafc; margin-bottom:3px;">📝 Practice Quiz</div>
        <div style="color:#8b949e; font-size:12px;">{total} questions · Select one answer per question · Submit when done</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Questions ──
    for idx, q in enumerate(questions):
        st.markdown(f"""
        <div style="background:#0d1117; border:1px solid #1e3a5f; border-left:3px solid #3b82f6;
                    border-radius:10px; padding:13px 16px; margin-bottom:4px;">
            <div style="color:#60a5fa; font-size:10px; font-weight:700; letter-spacing:1.5px; margin-bottom:5px;">
                QUESTION {idx+1} / {total}
            </div>
            <div style="color:#f1f5f9; font-size:14px; font-weight:600; line-height:1.5;">{q['question']}</div>
        </div>
        """, unsafe_allow_html=True)

        opts = [f"{k})  {v}" for k, v in q["options"].items()]
        st.radio(
            label=f"q{idx}",
            options=opts,
            key=f"quiz_q_{idx}",
            label_visibility="collapsed",
            disabled=st.session_state.quiz_submitted,
        )
        # Record answer from widget
        chosen = st.session_state.get(f"quiz_q_{idx}", "")
        if chosen:
            st.session_state.quiz_answers[idx] = chosen[0]

        st.markdown("<div style='margin-bottom:8px;'></div>", unsafe_allow_html=True)

    # ── Submit / Retake button ──
    answered = len([v for v in st.session_state.quiz_answers.values() if v])
    c1, _ = st.columns([1, 2])
    with c1:
        if not st.session_state.quiz_submitted:
            if st.button(f"✅ Submit  ({answered}/{total} answered)", use_container_width=True):
                st.session_state.quiz_submitted = True
                st.rerun()
        else:
            if st.button("🔄 Retake Quiz", use_container_width=True):
                st.session_state.quiz_submitted  = False
                st.session_state.quiz_answers    = {}
                st.rerun()

    # ── Results ──
    if st.session_state.quiz_submitted:
        score = sum(
            1 for idx, q in enumerate(questions)
            if st.session_state.quiz_answers.get(idx, "").upper() == q["answer"].upper()
        )
        pct = int(score / total * 100)

        if pct >= 70:
            grade_color, grade_msg, grade_icon = "#22c55e", "Excellent! Exam-ready! 🎉", "🏆"
        elif pct >= 40:
            grade_color, grade_msg, grade_icon = "#f59e0b", "Good effort! Review wrong answers 📖", "📚"
        else:
            grade_color, grade_msg, grade_icon = "#ef4444", "Keep going — you'll nail it! 💪", "💪"

        st.markdown(f"""
        <div style="background:#111827; border:2px solid {grade_color}; border-radius:14px;
                    padding:18px; text-align:center; margin:14px 0;">
            <div style="font-size:36px; margin-bottom:4px;">{grade_icon}</div>
            <div style="font-size:32px; font-weight:900; color:{grade_color}; line-height:1;">{score}/{total}</div>
            <div style="color:{grade_color}; font-weight:700; font-size:15px; margin-top:3px;">{pct}%</div>
            <div style="color:#94a3b8; margin-top:6px; font-size:12px;">{grade_msg}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**📋 Answer Review**")
        for idx, q in enumerate(questions):
            user_ans      = st.session_state.quiz_answers.get(idx, "")
            correct       = q["answer"].upper()
            is_ok         = user_ans.upper() == correct
            icon, color, bg = ("✅","#22c55e","#071a0f") if is_ok else ("❌","#ef4444","#1a0707")
            user_opt_text = q["options"].get(user_ans.upper(), "Not answered")
            corr_opt_text = q["options"].get(correct, correct)
            wrong_row = "" if is_ok else f"""
                <div style="color:#94a3b8; font-size:12px; margin-bottom:2px;">
                    Correct: <strong style="color:#22c55e;">{correct}) {corr_opt_text}</strong>
                </div>"""
            expl_row = f"""
                <div style="background:#0f1a0f; border-left:2px solid #22c55e55;
                             padding:5px 9px; border-radius:5px; color:#86efac; font-size:11px; margin-top:5px;">
                    💡 {q['explanation']}
                </div>""" if q["explanation"] else ""

            st.markdown(f"""
            <div style="background:{bg}; border:1px solid {color}44; border-radius:10px;
                        padding:12px 15px; margin-bottom:7px;">
                <div style="color:{color}; font-weight:700; font-size:13px; margin-bottom:5px;">
                    {icon} Q{idx+1}. {q['question']}
                </div>
                <div style="color:#cbd5e1; font-size:12px; margin-bottom:2px;">
                    Your answer: <strong style="color:{'#22c55e' if is_ok else '#f87171'};">
                        {user_ans or '–'}) {user_opt_text}
                    </strong>
                </div>
                {wrong_row}{expl_row}
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────
# MIND MAP GENERATION & RENDER
# ─────────────────────────────────────────

def generate_mindmap(chain):
    prompt = (
        "Generate a Mermaid.js mindmap for the key concepts in these notes.\n"
        "STRICT RULES:\n"
        "1. First line must be exactly: mindmap\n"
        "2. Second line must be: root((Topic Name)) — use actual subject name\n"
        "3. Use exactly 2-space indentation per level\n"
        "4. Add 4-5 main branches, each with 2-3 sub-items\n"
        "5. Node labels must be SHORT (1-5 words). No parentheses, brackets, quotes, colons, semicolons inside labels\n"
        "6. Output ONLY the raw mermaid code. No explanation, no backticks, no code fences.\n\n"
        "Correct example:\n"
        "mindmap\n"
        "  root((Machine Learning))\n"
        "    Supervised\n"
        "      Classification\n"
        "      Regression\n"
        "    Unsupervised\n"
        "      Clustering\n"
        "      Dimensionality Reduction\n"
        "    Evaluation\n"
        "      Accuracy\n"
        "      F1 Score\n"
    )
    res = chain.invoke({"input": prompt})
    raw = res["answer"]

    # Strip any code fences the model adds anyway
    if "```mermaid" in raw:
        raw = raw.split("```mermaid")[1].split("```")[0]
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0]

    return raw.strip()


def render_mindmap_fullscreen(code: str):
    """Render mermaid mindmap large and centered, with error display."""
    # Light sanitize: strip chars that break mermaid from node labels
    # but preserve root((...)) and indentation
    safe_lines = []
    for line in code.split("\n"):
        stripped = line.lstrip()
        indent   = line[: len(line) - len(stripped)]
        if stripped.startswith("mindmap") or stripped.startswith("root"):
            safe_lines.append(line)
        else:
            clean = re.sub(r'["\'\(\)\[\]\{\}:;]', '', stripped)
            safe_lines.append(indent + clean)
    safe_code = "\n".join(safe_lines)

    components.html(f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
      * {{ margin:0; padding:0; box-sizing:border-box; }}
      body {{
        background: #0d1117;
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 20px 16px;
        font-family: sans-serif;
      }}
      #wrap {{
        background: #ffffff;
        border-radius: 16px;
        padding: 24px 28px;
        width: 100%;
        overflow: auto;
        box-shadow: 0 0 50px rgba(59,130,246,0.15);
      }}
      #wrap svg {{
        width: 100% !important;
        height: auto !important;
        min-height: 420px;
      }}
      #err {{
        display: none;
        background: #2d0f0f;
        border: 1px solid #ef4444;
        border-radius: 10px;
        padding: 14px 18px;
        color: #fca5a5;
        font-family: monospace;
        font-size: 12px;
        width: 100%;
        margin-top: 12px;
        white-space: pre-wrap;
        word-break: break-all;
      }}
    </style>
    </head>
    <body>
      <div id="wrap">
        <pre class="mermaid">{safe_code}</pre>
      </div>
      <div id="err"></div>

      <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{
          startOnLoad: true,
          theme: 'default',
          securityLevel: 'loose',
          mindmap: {{ useMaxWidth: true, padding: 24 }},
        }});
        // catch render errors and show them
        window.addEventListener('error', function(e) {{
          const err = document.getElementById('err');
          err.style.display = 'block';
          err.textContent = 'Render error: ' + (e.message || e);
        }});
      </script>
    </body>
    </html>
    """, height=700, scrolling=True)