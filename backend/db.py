import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "rag.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            content TEXT,
            embedding TEXT
        )
    """)
    conn.commit()
    conn.close()


def insert_chunk(source, content, embedding):
    conn = get_connection()
    conn.execute(
        "INSERT INTO chunks (source, content, embedding) VALUES (?, ?, ?)",
        (source, content, json.dumps(embedding))
    )
    conn.commit()
    conn.close()


def get_all_chunks():
    conn = get_connection()
    rows = conn.execute("SELECT id, source, content, embedding FROM chunks").fetchall()
    conn.close()
    return [
        {"id": r[0], "source": r[1], "content": r[2], "embedding": json.loads(r[3])}
        for r in rows
    ]
