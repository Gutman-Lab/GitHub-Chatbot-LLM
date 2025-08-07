import os
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM
from langchain_huggingface import HuggingFaceEmbeddings
<<<<<<< HEAD
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from backend.chat.history_utils import save_chat
from backend.logging_config import logger

QA_PROMPT = PromptTemplate.from_template("""
You are a helpful assistant trained to explain GitHub codebases. Format your response in Markdown with bullet points, code blocks, and helpful tips.

Context:
{context}

Question:
{question}

Answer (Markdown):
""")

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

def chat_with_repo(query: str, model: str = "mistral:latest") -> str:
    logger.info(f"User query: {query}")

    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-large-en",
        model_kwargs={"device": "cpu"}
    )
    db = FAISS.load_local("vectorstore", embeddings, allow_dangerous_deserialization=True)
    retriever = db.as_retriever(search_kwargs={"k": 3})

    llm = OllamaLLM(model=model, temperature=0.2)

    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": QA_PROMPT},
        return_source_documents=False
    )

    memory_vars = memory.load_memory_variables({})
    inputs = {"question": query, "chat_history": memory_vars.get("chat_history", [])}
    result = qa_chain.invoke(inputs)["answer"]
    logger.info(f"LLM response: {result[:100]}...")
    save_chat(query, result, model=model)
    return result
=======
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from backend.chat.history_utils import save_chat
from backend.logging_config import logger

# ----------------------------
# Models too large for Tesla P100 16GB
# ----------------------------
MODEL_BLACKLIST = [
    "codellama:70b", "codellama:70b-instruct",
    "qwen2.5-coder:32b", "qwen2.5-coder:14b",
]

# ----------------------------
# Default fallback model
# ----------------------------
FALLBACK_MODEL = "deepseek-coder:6.7b"

# ----------------------------
# Embeddings & Vectorstore (load once)
# ----------------------------
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

vectorstore_path = "backend/vectorstore"
if not os.path.exists(vectorstore_path):
    # Backward compatibility if run from project root
    alt = "vectorstore"
    if os.path.exists(alt):
        vectorstore_path = alt
    else:
        raise FileNotFoundError("Vectorstore not found. Run store_embeddings.py first.")

vectorstore = FAISS.load_local(
    vectorstore_path,
    embeddings,
    allow_dangerous_deserialization=True,
)

# Use MMR for diverse, smaller retrieval (faster prompting)
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 2,         # fewer final chunks
        "fetch_k": 10,  # fetch more candidates then select 2
        "lambda_mult": 0.5,
    },
)

# ----------------------------
# Formatting-first prompt (concise, GitHub-style)
# ----------------------------
FORMAT_GUIDE = """You are a technical assistant.
Format answers as a clean, professional guide using GitHub-flavored Markdown:

• Use short sections with emoji headings (e.g., 📌 Prerequisites, 🧱 Steps, ⚙️ Configure, 🧪 Test, ✅ Checklist, 🐞 Troubleshooting).
• Put commands in fenced code blocks with language tags (```bash, ```python, etc.).
• Prefer numbered steps for procedures.
• Keep answers concise; avoid unnecessary prose.
• When relevant, add a short final checklist with ✅.
• If config/files are needed, show minimal, correct examples.

Be accurate and practical. If something is uncertain, say so briefly.
"""

STUFF_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=(
        f"{FORMAT_GUIDE}\n\n"
        "Context from the project:\n"
        "-------------------------\n"
        "{context}\n\n"
        "User question:\n"
        "--------------\n"
        "{question}\n\n"
        "Answer:\n"
    ),
)

def _safe_model(model: str) -> str:
    if model in MODEL_BLACKLIST:
        logger.warning(
            f"Model '{model}' too large for GPU. Using fallback '{FALLBACK_MODEL}'."
        )
        return FALLBACK_MODEL
    return model

def chat_with_repo(query: str, model: str = FALLBACK_MODEL) -> str:
    """Answer a user query using RAG over the local FAISS store with fast, formatted outputs."""
    try:
        if not query or not str(query).strip():
            return "Please enter a question."

        model = _safe_model(model)
        logger.info(f"🔍 Query: {query} | Model: {model}")

        # Decode settings tuned for speed + determinism on Ollama
        llm = OllamaLLM(
            model=model,
            temperature=0.2,
            top_p=0.9,
            num_ctx=2048,       # keep KV smaller
            num_predict=512,    # cap generation length
            repeat_penalty=1.1,
            mirostat=0,
        )

        # Concise answers reduce tokens -> faster
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            chain_type="stuff",
            chain_type_kwargs={"prompt": STUFF_PROMPT},
            return_source_documents=False,
        )

        result = qa_chain.run(query)
        logger.info(f"Response: {result[:200]}...")
        save_chat(query, result, model=model)
        return result

    except AssertionError as ae:
        logger.error(f"AssertionError: {ae}")
        return f"Error: AssertionError - {ae}"

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        logger.error(f"\n--- RAG CHAT ERROR ---\n{tb}\n")
        return f"Error: {repr(e)}"
>>>>>>> 034e242 (Initial commit: uploading WSI DL pipeline)
