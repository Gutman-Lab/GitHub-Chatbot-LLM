<<<<<<< HEAD
import json
from datetime import datetime

HISTORY_FILE = "chat_history.jsonl"

def save_chat(question, answer, model="unknown"):
=======
import os
import json
from datetime import datetime

def save_chat(question, answer, model="mistral:latest", file="data/chat_history.json"):
    os.makedirs(os.path.dirname(file), exist_ok=True)
>>>>>>> 034e242 (Initial commit: uploading WSI DL pipeline)
    record = {
        "timestamp": datetime.now().isoformat(),
        "model": model,
        "question": question,
<<<<<<< HEAD
        "answer": answer
    }
    with open(HISTORY_FILE, "a") as f:
        f.write(json.dumps(record) + "\n")
=======
        "answer": answer,
    }
    try:
        with open(file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"Error saving chat: {e}")
>>>>>>> 034e242 (Initial commit: uploading WSI DL pipeline)
