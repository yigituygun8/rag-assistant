"""Document ingestion pipeline for local PDF knowledge sources.

Reads PDFs from backend/data/docs, extracts text, splits it into chunks,
embeds each chunk with Foundry Local, and stores the result in SQLite.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from typing import Iterable

from pypdf import PdfReader

from db import delete_chunks_for_document, get_document, init_db, insert_chunk, upsert_document
from llm import embed_text


BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "data" / "docs"

MAX_CHUNK_CHARACTERS = 1200
MIN_CHUNK_CHARACTERS = 200


def _file_hash(path: Path) -> str:
	hasher = hashlib.sha256()
	with path.open("rb") as file_handle:
		for block in iter(lambda: file_handle.read(1024 * 1024), b""):
			hasher.update(block)
	return hasher.hexdigest()


def _extract_pdf_text(path: Path) -> list[str]:
	reader = PdfReader(str(path))
	pages: list[str] = []

	for page in reader.pages:
		text = page.extract_text() or ""
		cleaned = "\n".join(line.rstrip() for line in text.splitlines()).strip()
		if cleaned:
			pages.append(cleaned)

	return pages


def _split_text_into_chunks(text: str) -> list[str]:
	paragraphs = [paragraph.strip() for paragraph in text.split("\n\n") if paragraph.strip()]
	if not paragraphs:
		return []

	chunks: list[str] = []
	current_chunk: list[str] = []
	current_length = 0

	def flush():
		if current_chunk:
			chunks.append("\n\n".join(current_chunk).strip())

	for paragraph in paragraphs:
		# hard-split any paragraph that alone exceeds the max
		if len(paragraph) > MAX_CHUNK_CHARACTERS:
			flush()
			current_chunk, current_length = [], 0
			for start in range(0, len(paragraph), MAX_CHUNK_CHARACTERS):
				chunks.append(paragraph[start:start + MAX_CHUNK_CHARACTERS])
			continue

		if current_chunk and current_length + len(paragraph) + 2 > MAX_CHUNK_CHARACTERS:
			flush()
			current_chunk, current_length = [], 0

		current_chunk.append(paragraph)
		current_length += len(paragraph) + 2

	flush()
	return [c for c in chunks if len(c) >= MIN_CHUNK_CHARACTERS]


def _chunk_document(pages: Iterable[str]) -> list[str]:
	chunks: list[str] = []
	for page_text in pages:
		chunks.extend(_split_text_into_chunks(page_text))
	return chunks


def ingest_pdf(path: Path) -> int:
	content_hash = _file_hash(path)
	existing = get_document(path.name)

	if existing and existing[1] == content_hash:
		print(f"skipping {path.name}: already ingested")
		return 0

	pages = _extract_pdf_text(path)
	chunks = _chunk_document(pages)

	if not chunks:
		print(f"warning: no text extracted from {path.name}")
		return 0

	embedded_chunks = [(chunk_text, embed_text(chunk_text)) for chunk_text in chunks]

	document_id = upsert_document(path.name, content_hash)
	delete_chunks_for_document(document_id)

	for chunk_index, (chunk_text, embedding) in enumerate(embedded_chunks):
		insert_chunk(document_id, chunk_index, chunk_text, embedding)

	print(f"ingested {path.name}: {len(chunks)} chunks")
	return len(chunks)


def ingest_all_documents() -> int:
	init_db()

	if not DOCS_DIR.exists():
		raise FileNotFoundError(f"Document folder not found: {DOCS_DIR}")

	pdf_files = sorted(DOCS_DIR.glob("*.pdf"))
	if not pdf_files:
		print(f"no PDF files found in {DOCS_DIR}")
		return 0

	total_chunks = 0
	for pdf_path in pdf_files:
		total_chunks += ingest_pdf(pdf_path)

	print(f"done: processed {len(pdf_files)} PDFs and stored {total_chunks} chunks")
	return total_chunks


def main() -> None:
	parser = argparse.ArgumentParser(description="Ingest PDF documents into the local RAG database.")
	parser.parse_args()
	ingest_all_documents()


if __name__ == "__main__":
	main()