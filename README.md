# Local RAG Assistant

A fully offline document Q&A assistant built with **Microsoft Foundry Local** for on-device LLM inference and a custom **RAG (Retrieval-Augmented Generation)** pipeline. No cloud APIs, no API keys, no internet connection required after setup.

This project was built as part of the Microsoft AI Innovators Summer Program.

> **Status:** Work in progress. See [Roadmap](#roadmap) below for current progress.

## What it does

You give it a small collection of documents (course notes, FAQs, manuals, etc.). It:

1. Splits the documents into chunks
2. Generates an embedding (a numeric vector representing meaning) for each chunk using a local embedding model
3. Stores chunks + embeddings in a local SQLite database
4. When you ask a question, embeds your question and finds the most semantically similar chunks via cosine similarity
5. Feeds those chunks as context to a local LLM (via Foundry Local) to generate a grounded answer
6. If the answer isn't in the documents, the assistant says so instead of making something up

All of this runs entirely on-device.

## Tech stack

| Layer | Tech |
|---|---|
| Frontend | React (Vite) |
| Backend / API | Python, FastAPI |
| Local LLM runtime | [Microsoft Foundry Local](https://github.com/microsoft/Foundry-Local) |
| Embedding + chat model | Foundry Local catalog (model TBD based on hardware) |
| Storage | SQLite |

## Architecture

```
React frontend  --HTTP-->  FastAPI backend  --Foundry Local SDK-->  Local LLM
                                  |
                                  v
                            SQLite (chunks + embeddings)
```

## Project structure

```
rag-assistant/
├── backend/
│   ├── main.py          # FastAPI app and routes
│   ├── ingest.py         # document chunking + embedding pipeline
│   ├── retrieval.py      # similarity search (get_top_chunks)
│   ├── llm.py             # Foundry Local wrapper (embeddings + chat)
│   ├── db.py               # SQLite setup and helpers
│   ├── requirements.txt
│   └── data/
│       ├── docs/          # source documents
│       └── rag.db          # generated SQLite database
└── frontend/
    └── ...                  # Vite + React app
```

## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- [Foundry Local](https://github.com/microsoft/Foundry-Local) installed

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # on Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

API runs at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App runs at `http://localhost:5173`.

## Roadmap

- [x] Project skeleton (FastAPI backend + React frontend, connected)
- [x] SQLite schema for storing chunks and embeddings
- [x] Cosine similarity retrieval function
- [ ] Foundry Local installation and "hello model" verification
- [ ] Embedding generation wired into `llm.py`
- [ ] Document ingestion pipeline (`ingest.py`)
- [ ] Local LLM chat integration for answer generation
- [ ] Source citation in answers
- [ ] Testing with sample Q&A set
- [ ] Final documentation and demo

## Team

- Yiğit Uygun
- (add teammates here)

## Acknowledgements

- Project plan based on the Microsoft Tech Community post [Building Your First Local RAG Application with Foundry Local](https://techcommunity.microsoft.com/blog/azuredevcommunityblog/building-your-first-local-rag-application-with-foundry-local/4501968)
- Built as part of the Microsoft AI Innovators Summer Program
