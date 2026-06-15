from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from db import init_db
# from retrieval import get_top_chunks
# from llm import embed_text, generate_answer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # vite default port
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()


class QuestionRequest(BaseModel):
    question: str


@app.post("/ask")
def ask(req: QuestionRequest):
    # query_embedding = embed_text(req.question)
    # chunks = get_top_chunks(query_embedding)
    # answer = generate_answer(req.question, chunks)
    return {"answer": "placeholder until Foundry Local is wired in"}


@app.get("/health")
def health():
    return {"status": "ok"}
