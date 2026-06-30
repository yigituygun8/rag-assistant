# Document ingestion pipeline.
#
# TODO: implement once llm.embed_text() is working.
# This script should:
#   1. Read documents from data/docs/
#   2. Split each document into chunks (e.g. by paragraph)
#   3. Call llm.embed_text() on each chunk
#   4. Store (source, content, embedding) in SQLite via db.insert_chunk()
#
# Run as: python ingest.py