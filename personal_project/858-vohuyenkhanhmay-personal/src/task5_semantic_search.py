"""
Task 5 — Semantic Search Module (dense retrieval trên Qdrant).

Embed query bằng cùng model bge-m3 (Task 4) → query_points trên collection
DrugLawDocs → trả list {content, score, metadata} sorted by score DESC.

Chạy thử:
    python -m src.task5_semantic_search
"""

from .task4_chunking_indexing import COLLECTION_NAME, QDRANT_PATH, get_model

_client = None


def _get_client():
    """QdrantClient embedded (singleton) — giữ 1 kết nối, tránh tranh lock thư mục."""
    global _client
    if _client is None:
        from qdrant_client import QdrantClient
        _client = QdrantClient(path=QDRANT_PATH)
    return _client


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Tìm kiếm ngữ nghĩa bằng vector similarity (cosine).

    Returns:
        List of {'content': str, 'score': float, 'metadata': dict}
        sorted by score descending. score = cosine similarity ∈ [-1, 1].
    """
    # Embed query cùng model + normalize như khi index (Task 4).
    query_vec = get_model().encode(query, normalize_embeddings=True).tolist()

    response = _get_client().query_points(
        collection_name=COLLECTION_NAME,
        query=query_vec,
        limit=top_k,
        with_payload=True,
    )

    results = []
    for point in response.points:  # Qdrant đã sort theo score DESC
        payload = point.payload or {}
        results.append({
            "content": payload.get("content", ""),
            "score": float(point.score),
            "metadata": {
                "source": payload.get("source"),
                "type": payload.get("type"),
                "chunk_index": payload.get("chunk_index"),
            },
        })
    return results


if __name__ == "__main__":
    for q in [
        "hình phạt tàng trữ trái phép chất ma túy",
        "nghệ sĩ bị bắt vì sử dụng ma túy",
    ]:
        print(f"\nQuery: {q}\n" + "-" * 60)
        for r in semantic_search(q, top_k=3):
            print(f"[{r['score']:.3f}] ({r['metadata']['source']}) {r['content'][:90].strip()}...")
