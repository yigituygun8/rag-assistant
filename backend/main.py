import logging
from contextlib import asynccontextmanager
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from db import init_db
from retrieval import get_top_chunks
from llm import embed_text, generate_answer, warm_up, shutdown

logger = logging.getLogger("rag_assistant")
logging.basicConfig(level=logging.INFO)

# tracks whether warm_up() succeeded, so /health can report real status
_models_ready = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _models_ready

    init_db()

    logger.info("Warming up models, this may take a while on first run...")
    try:
        warm_up()
        _models_ready = True
        logger.info("Models ready.")
    except Exception:
        # log full traceback so you can see exactly what failed
        # (bad catalog alias, service not running, etc.)
        logger.exception("warm_up() failed, server starting in degraded mode")
        _models_ready = False

    yield

    logger.info("Shutting down, unloading models...")
    shutdown()


app = FastAPI(lifespan=lifespan)

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    question: str


@app.post("/ask")
def ask(req: QuestionRequest):
    if not _models_ready:
        raise HTTPException(
            status_code=503,
            detail="Models are not loaded yet or failed to load. Check server logs.",
        )

    question = req.question
    if not question or not question.strip():
        raise HTTPException(status_code=400, detail="Question must be a non-empty string")

    try:
        question_embedding = embed_text(question)
        chunks = get_top_chunks(question_embedding)
        answer = generate_answer(question, chunks)
    except ValueError as exc:
        # bad input caught inside llm.py, e.g. empty question slipping through
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        # inference-level failure we deliberately wrapped in llm.py
        logger.exception("inference failed")
        raise HTTPException(status_code=502, detail=f"Model inference failed: {exc}") from exc

    return {
        "answer": answer,
        "sources": [
            {
                "id": i + 1,
                "source": c.get("source", "unknown"),
                "content": c.get("content", "")
            }
            for i, c in enumerate(chunks)
        ]
    }


@app.get("/health")
def health():
    return {"status": "ok" if _models_ready else "degraded", "models_ready": _models_ready}