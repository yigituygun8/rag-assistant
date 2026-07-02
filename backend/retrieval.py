import numpy as np
from db import get_all_chunks


def get_top_chunks(query_embedding, k=3, score_threshold=0.5):
    chunks = get_all_chunks()
    if not chunks:
        return []

    query_vec = np.array(query_embedding, dtype=np.float32)
    query_norm = np.linalg.norm(query_vec)

    if query_norm == 0:
        raise ValueError("query_embedding is a zero vector, cannot compute similarity")

    expected_dim = query_vec.shape[0]

    scored = []
    for chunk in chunks:
        chunk_vec = np.array(chunk["embedding"], dtype=np.float32)

        if chunk_vec.shape[0] != expected_dim:
            # don't silently truncate via mismatched dimensions, skip and warn instead
            print(
                f"skipping chunk with mismatched embedding dimension: "
                f"expected {expected_dim}, got {chunk_vec.shape[0]}, source={chunk.get('source')}"
            )
            continue

        chunk_norm = np.linalg.norm(chunk_vec)
        if chunk_norm == 0:
            continue  # zero-vector embedding, can't be meaningfully compared

        score = float(np.dot(query_vec, chunk_vec) / (query_norm * chunk_norm))
        scored.append((score, chunk))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [chunk for score, chunk in scored[:k] if score >= score_threshold]