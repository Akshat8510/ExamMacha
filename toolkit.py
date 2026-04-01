import streamlit as st

def generate_flashcards(chain):
    res = chain.invoke({"input": "Identify 4 key technical terms from these notes and create flashcards. Format: Term | Definition"})
    return res["answer"]

def generate_quiz(chain):
    res = chain.invoke({"input": "Generate 2 Multiple Choice Questions based on the notes. Provide options A, B, C, D and the correct answer."})
    return res["answer"]

def generate_mindmap(chain):
    res = chain.invoke({"input": "Generate Mermaid.js code for a concept map of these notes. Start with 'graph TD'. Output ONLY the code block."})
    return res["answer"]

def display_flashcards(raw_text):
    cards = raw_text.split("\n")
    for card in cards:
        if "|" in card:
            term, definition = card.split("|")
            st.markdown(f"""
                <div style="background-color: #1e293b; padding: 15px; border-radius: 10px; border-left: 5px solid #3b82f6; margin-bottom: 10px;">
                    <strong style="color: #3b82f6;">{term.strip()}</strong><br>
                    <small style="color: #cbd5e1;">{definition.strip()}</small>
                </div>
            """, unsafe_allow_html=True)