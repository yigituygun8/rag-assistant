# Local RAG Assistant

A local document question-answering assistant built with **Microsoft Foundry Local** and a custom **RAG (Retrieval-Augmented Generation)** pipeline. Documents, embeddings, retrieval, and answer generation run on the local machine after the required models and packages have been installed.

This project was built as part of the Microsoft AI Innovators Summer Program.

> **Status:** Working prototype. The current application supports PDF ingestion from the local data directory, semantic retrieval, grounded answers with source citations, and a React chat interface.

## What it does

The application:

1. Reads PDF documents from `backend/data/docs/`.
2. Extracts text page by page with `pypdf`.
3. Splits each page into chunks of up to 1,200 characters and discards chunks shorter than 200 characters.
4. Generates an embedding for every chunk with the local `qwen3-embedding-0.6b` model.
5. Stores documents, chunks, page numbers, and JSON-serialized embeddings in `backend/data/rag.db`.
6. Embeds each question and ranks all stored chunks with cosine similarity.
7. Sends the top three chunks meeting the `0.45` similarity threshold to the local `qwen2.5-1.5b` chat model.
8. Displays the generated answer and clickable source citations in the web UI.

When relevant context is found, the model is instructed to answer only from that context and cite factual claims with chunk numbers such as `[1]`. When no chunk passes the threshold, the model receives no document context and responds conversationally.

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite 5 |
| Backend/API | Python, FastAPI, Uvicorn |
| Local model runtime | [Microsoft Foundry Local](https://github.com/microsoft/Foundry-Local) |
| Chat model | `qwen2.5-1.5b` by default |
| Embedding model | `qwen3-embedding-0.6b` by default |
| Document extraction | `pypdf` |
| Retrieval | NumPy cosine similarity |
| Storage | SQLite |

The model names can be changed with `FOUNDRY_LOCAL_CHAT_MODEL` and `FOUNDRY_LOCAL_EMBEDDING_MODEL`. The Foundry Local SDK application name can be changed with `FOUNDRY_LOCAL_APP_NAME`.

## Architecture

```text
React/Vite frontend
        │ POST /ask
        ▼
FastAPI backend
   ┌────┼───────────────┐
   │    │               │
   │    ▼               ▼
   │  llm.py       retrieval.py
   │    │               │
   │    ▼               ▼
   │ Foundry Local   SQLite chunks
   │ (chat + embed)  + embeddings
   │
   └── ingest.py ── PDFs in backend/data/docs/
```

The API warms up both models during startup. If model loading fails, the server still starts in degraded mode and `/health` reports `models_ready: false`; `/ask` returns HTTP 503 until the models are ready.

## Project structure

```text
rag-assistant/
├── backend/
│   ├── main.py          # FastAPI application, lifecycle, and API routes
│   ├── ingest.py        # PDF extraction, chunking, hashing, and indexing CLI
│   ├── retrieval.py     # In-memory cosine-similarity retrieval
│   ├── llm.py           # Foundry Local model loading, embeddings, and chat
│   ├── db.py            # SQLite schema and data-access helpers
│   ├── requirements.txt
│   └── data/
│       ├── docs/        # Local PDF sources (ignored by git)
│       └── rag.db       # Generated SQLite database (ignored by git)
├── frontend/
│   ├── src/App.jsx      # Chat UI and citation rendering
│   ├── src/chatApi.js   # Backend client and timeout handling
│   └── .env.example     # Optional API URL configuration
├── architecture_analysis.md
└── RAG_NOTES.md
```

## Setup

### Prerequisites

- Windows with [Microsoft Foundry Local](https://github.com/microsoft/Foundry-Local) installed and usable.
- Python 3.10 or newer.
- Node.js 18 or newer.
- Enough local disk space and memory for the selected Foundry Local models.

The first model download requires connectivity. After the packages and models are available locally, inference does not require a cloud API, API key, or application network connection.

### Backend setup

From PowerShell:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell prevents script activation, use `.\venv\Scripts\python.exe` directly or enable the script policy for your user account according to your organization’s policy.

### Add documents and build the index

Place PDF files in `backend/data/docs/`, then run:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python ingest.py
```

Ingestion is hash-aware: unchanged PDFs are skipped. To force re-ingestion:

```powershell
python ingest.py --force
```

Run ingestion again whenever the source PDFs change. There is currently no runtime upload endpoint in the application.

### Start the backend

```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload
```

The API runs at `http://localhost:8000`.

- Interactive API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`
- Question endpoint: `POST http://localhost:8000/ask`

Optional environment variables:

```text
FOUNDRY_LOCAL_APP_NAME=rag_assistant
FOUNDRY_LOCAL_CHAT_MODEL=qwen2.5-1.5b
FOUNDRY_LOCAL_EMBEDDING_MODEL=qwen3-embedding-0.6b
ALLOWED_ORIGINS=http://localhost:5173
```

### Start the frontend

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

The Vite development server normally runs at `http://localhost:5173`. To use another backend URL, copy `.env.example` to `.env` and set `VITE_API_BASE_URL`.

If the backend is unreachable or a request times out, the frontend deliberately shows a clearly marked mock fallback response so the UI remains usable. This fallback is not a RAG answer and does not contain document sources.

## API example

Request:

```http
POST /ask
Content-Type: application/json

{"question":"What is Scrum?"}
```

Successful responses contain an `answer` string and a `sources` array. Each source includes an `id`, source filename, page number, and retrieved chunk content.

## Current limitations

- Retrieval loads every chunk and computes cosine similarity in memory, so the current approach is intended for small document collections.
- Embeddings are stored as JSON text rather than a vector index or binary vector format.
- Only PDF files in the local ingestion directory are supported.
- There is no authentication, multi-user session storage, or runtime document-management UI.
- Foundry Local model loading is coupled to the Windows SDK dependency, which makes isolated CI testing harder.
- The frontend fallback is useful for development feedback but must not be mistaken for a grounded answer.

## Roadmap

- [x] FastAPI backend and React frontend
- [x] SQLite schema for documents, chunks, page numbers, and embeddings
- [x] PDF ingestion with content-hash based skip logic
- [x] Foundry Local embedding and chat integration
- [x] Startup model warm-up and health reporting
- [x] Cosine-similarity retrieval with a relevance threshold
- [x] Grounded answers with source citations
- [x] Clickable citation badges in the frontend
- [ ] Runtime PDF upload and ingestion
- [ ] Scalable vector indexing
- [ ] Automated backend and frontend test coverage

## Made by

- Osman Yiğit Uygun

## Acknowledgements

- Project plan based on the Microsoft Tech Community post [Building Your First Local RAG Application with Foundry Local](https://techcommunity.microsoft.com/blog/azuredevcommunityblog/building-your-first-local-rag-application-with-foundry-local/4501968).
- Built as part of the Microsoft AI Innovators Summer Program.
