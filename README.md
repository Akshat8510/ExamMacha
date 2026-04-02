
# 🎓 ExamMacha: Prepgraph Studio  
**AI-Powered Examination Scaffolding & RAG-Based Learning Environment**

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Framework-Streamlit-FF4B4B.svg)
![LangChain](https://img.shields.io/badge/Orchestration-LangChain-green.svg)
![Groq](https://img.shields.io/badge/LLM-LLaMA--3.3--70B-orange.svg)

**ExamMacha** (Prepgraph Studio) is an advanced AI study companion that transforms static documents (PDFs, PPTXs) into an interactive, retrieval-augmented learning experience. Built for students who need more than just a chat-bot, it provides pedagogical scaffolding through adaptive flashcards, MCQ quizzes, and visual mind maps.

---

## 🚀 Key Features

### 🧠 1. RAG-Powered Study Chat
*   **Document Intelligence:** Ingests local notes and uses a FAISS vector store to provide context-aware answers.
*   **MacchaHelp Mode:** A specialized pedagogical persona that enforces a high-retention 5-part answer template:
    1.  **Definition:** Exam-quality one-sentence summary.
    2.  **Concept:** Simplified bullet points.
    3.  **Diagram:** ASCII or textual visual representations.
    4.  **Formula:** Mathematical notation.
    5.  **Exam Conclusion:** A memorable closing "hook."

### 🛠️ 2. The Studio Toolkit
*   **Adaptive Flashcards:** Generates 6 high-impact cards with "Reveal Answer" flip mechanics (Blue $\rightarrow$ Green).
*   **MCQ Quiz Engine:** Structured testing with a reworked v1.1 answer-review renderer for high-quality HTML feedback.
*   **Mermaid.js Mind Maps:** Dynamic visual concept mapping rendered via an interactive iframe.

### 🌐 3. Real-Time Knowledge Augmentation
*   **Tavily Web Search:** Optionally toggles a live web-search layer to verify facts or fetch information beyond your uploaded notes.

---

## 🛠️ Tech Stack

| Layer | Technology |
| :--- | :--- |
| **UI Framework** | Streamlit |
| **LLM Inference** | Groq (LLaMA-3.3-70B-Versatile) |
| **Orchestration** | LangChain |
| **Vector Database** | FAISS (CPU) |
| **Embeddings** | HuggingFace (`paraphrase-MiniLM-L3-v2`) |
| **Search API** | Tavily API |
| **Visualization** | Mermaid.js v10 |

---

## 🏗️ Technical Architecture

### Data Flow
1.  **Ingestion:** Files are loaded via `PyPDFLoader` or `UnstructuredPowerPointLoader`.
2.  **Processing:** Text is split using `RecursiveCharacterTextSplitter` (1,000 token chunks, 150 overlap).
3.  **Vectorization:** Chunks are embedded and stored in a local RAM-resident FAISS index.
4.  **Retrieval:** Top-4 similarity search results are injected into the LLM context window.
5.  **Execution:** Studio tools (`toolkit.py`) use targeted prompts to synthesize structured study material.

### v1.1 Improvements
*   **Three-Column Layout Engine:** Switch between "Chat Focus," "Studio Focus," and "Dashboard" modes.
*   **Bug Fix:** Fully reworked the HTML-escape rendering bug in the quiz review module using a newline-free f-string injection.

---

## 📂 Project Structure

```text
├── app.py              # UI orchestration, layout engine, and Session State
├── engine.py           # RAG Backend: Ingestion, Embeddings, FAISS lifecycle
├── toolkit.py          # Studio Tools: Flashcards, MCQs, Mermaid Mindmaps
├── search.py           # Web Search integration via Tavily API
├── .env                # API Keys (Groq, Tavily)
└── requirements.txt    # Project dependencies
```

---

## ⚙️ Setup & Installation

### 1. Prerequisites
*   Python 3.10+
*   Groq API Key (Sign up at [Groq Console](https://console.groq.com/))
*   Tavily API Key (Optional, for web search)

### 2. Installation
```bash
git clone https://github.com/Akshat8510/ExamMacha.git
cd ExamMacha
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

### 4. Run the App
```bash
streamlit run app.py
```

---

## 📈 Roadmap & Limitations
*   **OCR Support:** Currently supports text-based PDFs only (no image-only OCR).
*   **Persistence:** FAISS index is held in RAM; browser refresh clears the current document context.
*   **Coming Soon:** Support for `.docx` and `.txt` files, and local FAISS index persistence.

---

## 🤝 Contributing
Contributions are welcome! Please open an issue or submit a pull request for any architectural improvements or new Studio tools.

**Developed by [Akshat Kumar](https://github.com/Akshat8510)**
