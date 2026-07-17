import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "rag.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT UNIQUE NOT NULL,
            content_hash TEXT NOT NULL,
            last_ingested TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            chunk_index INTEGER NOT NULL,
            text TEXT NOT NULL,
            embedding TEXT NOT NULL,
            FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE);
    """)
    conn.commit()
    conn.close()


def get_document(filename):
    """Return (id, content_hash) for a filename, or None if not ingested yet."""
    conn = get_connection()
    row = conn.execute(
        "SELECT id, content_hash FROM documents WHERE filename = ?",
        (filename,)
    ).fetchone()
    conn.close()
    return row


def upsert_document(filename, content_hash):
    """Insert a new document, or update its hash if it already exists.
    Returns the document's id."""
    conn = get_connection()
    conn.execute("""
        INSERT INTO documents (filename, content_hash) VALUES (?, ?)
        ON CONFLICT(filename) DO UPDATE SET
            content_hash = excluded.content_hash,
            last_ingested = CURRENT_TIMESTAMP
    """, (filename, content_hash))
    conn.commit()
    doc_id = conn.execute(
        "SELECT id FROM documents WHERE filename = ?", (filename,)
    ).fetchone()[0]
    conn.close()
    return doc_id


def delete_chunks_for_document(document_id):
    conn = get_connection()
    conn.execute("DELETE FROM chunks WHERE document_id = ?", (document_id,))
    conn.commit()
    conn.close()


def insert_chunk(document_id, chunk_index, text, embedding):
    conn = get_connection()
    conn.execute(
        "INSERT INTO chunks (document_id, chunk_index, text, embedding) VALUES (?, ?, ?, ?)",
        (document_id, chunk_index, text, json.dumps(embedding))
    )
    conn.commit()
    conn.close()


def get_all_chunks():
    conn = get_connection()
    rows = conn.execute("""
        SELECT chunks.id, documents.filename, chunks.text, chunks.embedding
        FROM chunks
        JOIN documents ON chunks.document_id = documents.id
    """).fetchall()
    conn.close()
    return [
        {"id": r[0], "source": r[1], "content": r[2], "embedding": json.loads(r[3])}
        for r in rows
    ]