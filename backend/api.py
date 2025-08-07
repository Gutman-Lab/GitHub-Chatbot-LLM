<<<<<<< HEAD
from fastapi import FastAPI
from pydantic import BaseModel
from backend.chat.rag_chat import chat_with_repo

app = FastAPI()

=======
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from backend.chat.rag_chat import chat_with_repo
import logging
import traceback

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Secure this later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chat-api")

>>>>>>> 034e242 (Initial commit: uploading WSI DL pipeline)
class Query(BaseModel):
    question: str
    model: str = "mistral:latest"

@app.post("/chat")
<<<<<<< HEAD
def ask_question(query: Query):
    response = chat_with_repo(query.question, model=query.model)
    return {"response": response}
=======
async def ask_question(query: Query):
    logger.info(f"Received question: {query.question} | model: {query.model}")
    try:
        answer = chat_with_repo(query.question, model=query.model)
        logger.info("Returning successful response.")
        return {"response": answer}
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"Exception: {e}\nTraceback:\n{tb}")
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "trace": tb.splitlines()[-3:]  # last few lines of the error
            }
        )
>>>>>>> 034e242 (Initial commit: uploading WSI DL pipeline)
