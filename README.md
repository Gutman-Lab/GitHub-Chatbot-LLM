# 🤖 GitHub Chatbot LLM

A fully local, GPU-accelerated chatbot that allows you to ask natural language questions about GitHub repositories using **LangChain**, **Ollama**, and **FAISS**. Built with a modern **React frontend** and **FastAPI backend**, it supports models like `mistral`, `deepseek-coder`, `llama3`, and more.
---

##  Features

- **Runs Locally** — No OpenAI/API keys required
- **Ollama LLM Support** — `mistral`, `deepseek-coder`, `llama3`, etc.
- **RAG with FAISS** — Embeds and retrieves relevant code/doc snippets
- **ChatGPT-style React Frontend** — With markdown, history, dark mode
- **GPU Acceleration** — Torch + CUDA 11.8 enabled (e.g. Tesla P100)
- **Multi-repo Cloning & Indexing** — Supports multiple GitHub repos

---

## Architecture

React Frontend (ChatGPT-style)
|
FastAPI Backend (/chat)
|
LangChain → FAISS Vectorstore
|
HuggingFace Embeddings
|
Ollama LLM (local inference)

---

## 🔧 Installation

### 1. Clone the repository

git clone https://github.com/Gutman-Lab/GitHub-Chatbot-LLM.git
cd GitHub-Chatbot-LLM
2. Setup Python environment
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cu118
✅ torch==2.2.2+cu118 for GPU support

3. Start Ollama with desired model(s)
ollama run mistral
Or preload models:

ollama pull mistral
ollama pull deepseek-coder:6.7b
4. Embed GitHub Repositories
python backend/github_scraper.py       # Clones digital pathology repos
python backend/store_embeddings.py     # Embeds all text/code into FAISS

Run the Chatbot
Start Backend (FastAPI)
cd backend
uvicorn backend.api:app --host 0.0.0.0 --port 8000
Start Frontend (React + Vite)
cd frontend
npm install
npm run dev
Open your browser at http://localhost:5173

Example Queries
How to install HistomicsUI?

What is Digital Slide Archive?

How does girder-client-mount work?

Models Supported
Model Name	Capability
mistral	General Q&A
deepseek-coder	Code understanding
llama3	Reasoning & Logic
openchat	Conversational
qwen2.5-coder	Coding-focused

Models are loaded via Ollama, running locally.

Notes
Default GitHub repos:

digital_slide_archive

HistomicsUI

HistomicsTK

FAISS vectorstore is saved to /vectorstore/

License
Department of Pathology & Laboratory Medicine License. © Gutman Lab, Emory University.