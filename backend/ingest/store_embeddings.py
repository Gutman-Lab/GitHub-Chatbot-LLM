import os
import sys
import mimetypes
from pathlib import Path
from tqdm import tqdm

from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
<<<<<<< HEAD
from langchain_huggingface import HuggingFaceEmbeddings 

VECTOR_DIR = "vectorstore"
EMBEDDING_MODEL = "BAAI/bge-large-en"

def is_text_file(path: Path) -> bool:
=======
from langchain_huggingface import HuggingFaceEmbeddings

# === CONFIG ===
VECTOR_DIR = "backend/vectorstore"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
ALLOWED_EXTENSIONS = {".py", ".md", ".txt", ".rst", ".json", ".yaml", ".yml", ".ipynb"}

# === HELPERS ===
def is_valid_text_file(path: Path) -> bool:
    ext = path.suffix.lower()
    if ext in ALLOWED_EXTENSIONS:
        return True
>>>>>>> 034e242 (Initial commit: uploading WSI DL pipeline)
    mime_type, _ = mimetypes.guess_type(str(path))
    return mime_type is not None and mime_type.startswith("text")

def collect_text_files(root: str):
<<<<<<< HEAD
    print(f"📂 Scanning directory: {root}")
    text_files = []
    for path in Path(root).rglob("*"):
        if path.is_file() and is_text_file(path):
            text_files.append(path)
    print(f"✅ Found {len(text_files)} text files")
    return text_files

def embed_repo(repo_dir="data"):
    file_paths = collect_text_files(repo_dir)

=======
    print(f"📁 Scanning: {root}")
    text_files = [p for p in Path(root).rglob("*") if p.is_file() and is_valid_text_file(p)]
    print(f"✅ {len(text_files)} files selected")
    return text_files

# === MAIN LOGIC ===
def embed_repo(repo_dir="data"):
    file_paths = collect_text_files(repo_dir)
>>>>>>> 034e242 (Initial commit: uploading WSI DL pipeline)
    if not file_paths:
        print("⚠️ No valid text files found.")
        sys.exit(1)

    documents = []
<<<<<<< HEAD
    for file_path in tqdm(file_paths, desc="📄 Loading files"):
        try:
            loader = TextLoader(str(file_path), autodetect_encoding=True)
            documents.extend(loader.load())
        except Exception as e:
            print(f"⚠️ Skipping {file_path}: {e}")

    if not documents:
        print("⚠️ No readable documents loaded.")
        sys.exit(1)

    print(f"✅ Successfully loaded {len(documents)} documents")

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_documents(documents)
    print(f"✅ Created {len(chunks)} text chunks")

    if not chunks:
        print("⚠️ No content to embed.")
        sys.exit(1)

    print("\n🔍 First chunk preview:")
    print(chunks[0].page_content[:500])

    print("\n🧠 Generating embeddings...")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"}
    )

    db = FAISS.from_documents(chunks, embeddings)
    db.save_local(VECTOR_DIR)
    print(f"✅ Embeddings saved to ./" + VECTOR_DIR)

    with open(os.path.join(VECTOR_DIR, "model.txt"), "w") as f:
        f.write(EMBEDDING_MODEL)


=======
    for path in tqdm(file_paths, desc="📄 Loading files"):
        try:
            loader = TextLoader(str(path), autodetect_encoding=True)
            docs = loader.load()
            documents.extend(docs)
        except Exception as e:
            print(f"⚠️ Skipping {path}: {e}")

    if not documents:
        print("❌ No documents loaded.")
        sys.exit(1)

    print(f"✅ Loaded {len(documents)} documents")

    # Slightly smaller chunks reduce prompt size -> faster
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=80,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    print(f"✅ Split into {len(chunks)} chunks")

    print("\n🔍 First chunk preview:\n" + chunks[0].page_content[:300])

    print("🧠 Embedding with:", EMBEDDING_MODEL)
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    db = FAISS.from_documents(chunks, embeddings)
    os.makedirs(VECTOR_DIR, exist_ok=True)
    db.save_local(VECTOR_DIR)
    print(f"✅ Vector DB saved to: ./{VECTOR_DIR}")

    with open(os.path.join(VECTOR_DIR, "model.txt"), "w", encoding="utf-8") as f:
        f.write(EMBEDDING_MODEL)

>>>>>>> 034e242 (Initial commit: uploading WSI DL pipeline)
if __name__ == "__main__":
    repo_path = sys.argv[1] if len(sys.argv) > 1 else "data"
    embed_repo(repo_path)
