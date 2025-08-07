import sys
import os
import streamlit as st
from datetime import datetime
import json

# Ensure backend path is available
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.chat.rag_chat import chat_with_repo

# Page settings
st.set_page_config(page_title="GitHub Chatbot", layout="wide")

# --- Custom CSS ---
st.markdown("""
<style>
body {
    background-color: #f8f9fa;
    font-family: 'Segoe UI', sans-serif;
}
.stApp {
    padding: 1.5rem;
}
.title {
    font-size: 1.8rem;
    font-weight: 700;
    color: #212529;
    text-align: center;
    margin-bottom: 1.5rem;
}
.question {
    background-color: #e9f5ff;
    color: #1c1c1c;
    padding: 1rem;
    border-radius: 8px;
    border-left: 6px solid #339af0;
    font-weight: 500;
}
.answer {
    background-color: #1e1e1e;
    color: #d4d4d4;
    padding: 1rem;
    border-radius: 8px;
    border-left: 6px solid #569cd6;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
    font-family: Consolas, monospace;
}
.footer {
    margin-top: 2rem;
    font-size: 0.9rem;
    color: #6c757d;
    text-align: center;
}
@media (prefers-color-scheme: dark) {
    body {
        background-color: #1e1e1e;
        color: #d4d4d4;
    }
    .question {
        background-color: #2d333b;
        border-left-color: #3b82f6;
        color: #ffffff;
    }
    .answer {
        background-color: #252526;
        color: #dcdcdc;
        border-left-color: #569cd6;
    }
    .footer {
        color: #aaaaaa;
    }
}
</style>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown('<div class="title">💬 GitHub Chatbot (Local LLM via Ollama)</div>', unsafe_allow_html=True)

# --- Model Selector ---
model = st.selectbox("Choose Ollama model:", [
    "mistral:latest",
    "llama3:latest",
    "openchat:latest",
    "codellama:70b-instruct",
    "deepseek-coder:base",
    "qwen2.5-coder:7b-instruct-q6_K"
])

# --- Session State ---
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

# --- Input Box ---
query = st.text_input("Ask something about your GitHub repositories:")

# --- Run Query ---
if query:
    with st.spinner("Thinking..."):
        os.environ["LLM_MODEL"] = model
        try:
            answer = chat_with_repo(query, model=model)
        except Exception as e:
            answer = f"Error: {e}"
        st.session_state.chat_log.append({
            "time": datetime.now().strftime("%H:%M"),
            "query": query,
            "answer": answer
        })

# --- Display Chat ---
for entry in reversed(st.session_state.chat_log):
    st.markdown(f"<div class='question'><strong>You:</strong><br>{entry['query']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='answer'><strong>Bot:</strong><br>{entry['answer']}</div>", unsafe_allow_html=True)

# --- Download Button ---
if st.session_state.chat_log:
    history_json = json.dumps(st.session_state.chat_log, indent=2)
    st.download_button("📎 Download Chat History", data=history_json,
                       file_name="chat_history.json", mime="application/json")

# --- Footer ---
st.markdown("<div class='footer'>ChatBot - GitHub Repositories Locally.</div>", unsafe_allow_html=True)