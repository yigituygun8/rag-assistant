"""Foundry Local integration layer for embeddings and chat completions."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Any
import datetime


APP_NAME = os.getenv("FOUNDRY_LOCAL_APP_NAME", "rag_assistant")
CHAT_MODEL_NAME = os.getenv("FOUNDRY_LOCAL_CHAT_MODEL", "qwen2.5-1.5b")
EMBEDDING_MODEL_NAME = os.getenv("FOUNDRY_LOCAL_EMBEDDING_MODEL", "qwen3-embedding-0.6b")


def _load_sdk():
    try:
        from foundry_local_sdk import Configuration, FoundryLocalManager
    except ImportError as exc:  # pragma: no cover - dependency issue
        raise RuntimeError(
            "foundry-local-sdk-winml is not installed. Install backend/requirements.txt first."
        ) from exc

    return Configuration, FoundryLocalManager


@lru_cache(maxsize=1)
def _get_manager():
    configuration, manager_cls = _load_sdk()
    manager_cls.initialize(configuration(app_name=APP_NAME))
    return manager_cls.instance


_loaded_models: dict[str, Any] = {}

def _get_loaded_model(model_name: str):
    if model_name not in _loaded_models:
        manager = _get_manager()
        model = manager.catalog.get_model(model_name)
        model.download()
        model.load()
        _loaded_models[model_name] = model
    return _loaded_models[model_name]


def warm_up() -> None:
    """Force both models to download and load. Call this once at app startup,
    not lazily on the first request."""
    _get_loaded_model(CHAT_MODEL_NAME)
    _get_loaded_model(EMBEDDING_MODEL_NAME)


def shutdown() -> None:
    """Explicitly unload all models. Call this from FastAPI's lifespan
    shutdown phase so memory is actually freed on exit."""
    for model in _loaded_models.values():
        model.unload()
    _loaded_models.clear()

def _get_embedding_client():
    model = _get_loaded_model(EMBEDDING_MODEL_NAME)
    return model.get_embedding_client()


def _get_chat_client():
    model = _get_loaded_model(CHAT_MODEL_NAME)
    return model.get_chat_client()


def embed_text(text: str) -> list[float]:
    if not text or not text.strip():
        raise ValueError("text must be a non-empty string")

    client = _get_embedding_client()
    response = client.generate_embedding(text)
    return list(response.data[0].embedding)


def _format_context_chunks(context_chunks: list[dict[str, Any]]) -> str:
    if not context_chunks:
        return "No context chunks were retrieved."

    lines = []
    for index, chunk in enumerate(context_chunks, start=1):
        source = chunk.get("source", "unknown source")
        content = (chunk.get("content") or "").strip()
        lines.append(f"[{index}] Source: {source}\n{content}")
    return "\n\n".join(lines)

APP_IDENTITY = f"Local RAG Assistant, a document question-answering app running entirely on-device via Foundry Local, using {EMBEDDING_MODEL_NAME} for embeddings and {CHAT_MODEL_NAME} for chat completions."

GROUNDED_SYSTEM_PROMPT = (
    "You are a grounded document QA assistant. Answer only using the provided context. "
    "If the context does not contain the answer, say that you could not find it in the documents. "
    "When possible, mention the source names from the context."
)

def generate_answer(question: str, context_chunks: list[dict[str, Any]]) -> str:
    if not question or not question.strip():
        raise ValueError("question must be a non-empty string")

    if context_chunks:
        system_prompt = GROUNDED_SYSTEM_PROMPT
        context = _format_context_chunks(context_chunks)
        user_content = (
            f"Context:\n{context}\n\n"
            f"Question: {question}\n\n"
            "Write a concise answer based only on the context."
        )
    else:
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        system_prompt = (
            f"You are {APP_IDENTITY} "
            f"The current date and time is {current_datetime}. "
            "The user's message did not match any documents in the knowledge base, "
            "so just respond naturally and conversationally. If they ask what model "
            "you are, mention you are a local Qwen model running through Foundry Local. "
            "If they seem to be asking about their documents, gently suggest they "
            "upload or ingest relevant files first."
        )
        user_content = question

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]

    client = _get_chat_client()
    try:
        response = client.complete_chat(messages)
    except Exception as exc:
        raise RuntimeError(f"chat completion failed: {exc}") from exc

    if not response.choices:
        raise RuntimeError("chat completion returned no choices")

    return response.choices[0].message.content.strip()