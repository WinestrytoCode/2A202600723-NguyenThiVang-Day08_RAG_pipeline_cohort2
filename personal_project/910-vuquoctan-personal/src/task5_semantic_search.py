"""
Task 5 — Semantic Search Module.

Viết module tìm kiếm ngữ nghĩa (dense retrieval) trên vector store.

Yêu cầu:
    - Input: query string + top_k
    - Output: danh sách chunks có score, sorted descending
    - Phải tương thích với embedding model và vector store ở Task 4
"""


import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

PROJECT_DIR = Path(__file__).parent.parent
INDEX_PATH = PROJECT_DIR / "data" / "index" / "chunks.json"
MODEL_NAME = "BAAI/bge-m3"

_model = None
_chunks = None

def _load_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def _load_chunks():
    global _chunks
    if _chunks is None:
        _chunks = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    return _chunks

def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    model = _load_model()
    chunks = _load_chunks()

    query_emb = model.encode([query], normalize_embeddings=True)[0]

    results = []
    for chunk in chunks:
        emb = np.array(chunk["embedding"])
        score = float(np.dot(query_emb, emb))

        results.append({
            "content": chunk["content"],
            "score": score,
            "metadata": chunk.get("metadata", {})
        })

    results = sorted(results, key=lambda x: x["score"], reverse=True)
    return results[:top_k]