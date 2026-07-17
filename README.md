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
| Model | Foundry Local Catalog (model TBD based on hardware) |

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

### First-time startup flow

The ingestion step is separate from the app startup.

1. Put your source PDFs in `backend/data/docs/`.
2. Create the backend virtual environment once.
3. Activate that virtual environment in any terminal where you want to run backend commands.
4. Install backend dependencies once.
5. Run `python ingest.py` from `backend/` to build or refresh `backend/data/rag.db`.
6. Start the backend API with `uvicorn main:app --reload`.
7. Start the frontend with `npm run dev` from `frontend/`.

You only need to rerun `python ingest.py` when the documents in `backend/data/docs/` change.

What the venv does: it is a local Python environment for this project only. It keeps this app's packages separate from your system Python and from other projects, so installs do not clash.

### Backend setup

Create the venv once:

```bash
cd backend
python -m venv venv
source venv/bin/activate   # on Windows: venv\Scripts\activate
```

Install dependencies and build the document index once:

```bash
pip install -r requirements.txt
python ingest.py
```

### Backend run

Open a new terminal or reuse one, activate the venv again, then start the API:

```bash
cd backend
source venv/bin/activate   # on Windows: venv\Scripts\activate
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
- [x] Foundry Local installation and "hello model" verification
- [x] Embedding generation wired into `llm.py`
- [x] Document ingestion pipeline (`ingest.py`)
- [ ] Local LLM chat integration for answer generation
- [ ] Source citation in answers
- [ ] Testing with sample Q&A set
- [ ] Final documentation and demo

## Made By

- Osman Yiğit Uygun

## Acknowledgements

- Project plan based on the Microsoft Tech Community post [Building Your First Local RAG Application with Foundry Local](https://techcommunity.microsoft.com/blog/azuredevcommunityblog/building-your-first-local-rag-application-with-foundry-local/4501968)
- Built as part of the Microsoft AI Innovators Summer Program
