import math
from db import get_all_chunks


def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(y * y for y in b))
    return dot / (mag_a * mag_b)


def get_top_chunks(query_embedding, k=3):
    chunks = get_all_chunks()
    scored = [
        (cosine_similarity(query_embedding, c["embedding"]), c)
        for c in chunks
    ]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored[:k]]
