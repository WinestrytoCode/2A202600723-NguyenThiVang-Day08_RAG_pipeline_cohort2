"""
Task 9 — Retrieval Pipeline Hoàn Chỉnh.

    Query
      ├→ semantic_search (T5) ─┐
      ├→ lexical_search  (T6) ─┤ RRF merge (T7) → source="hybrid"
      │                         → rerank Jina (T7) → điểm 0..1
      └→ nếu best_score < threshold → fallback pageindex_search (T8)

LƯU Ý: threshold (0.3) áp lên điểm SAU rerank của Jina (0..1), KHÔNG áp lên
điểm RRF (~0.03) — nên fallback theo threshold chỉ bật khi use_reranking=True.
"""

from .task5_semantic_search import semantic_search
from .task6_lexical_search import lexical_search
from .task7_reranking import rerank, rerank_rrf
from .task8_pageindex_vectorless import pageindex_search


# =============================================================================
# CONFIGURATION
# =============================================================================

SCORE_THRESHOLD = 0.3
DEFAULT_TOP_K = 5
RERANK_METHOD = "cross_encoder"


def retrieve(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    score_threshold: float = SCORE_THRESHOLD,
    use_reranking: bool = True,
) -> list[dict]:
    """
    Retrieval pipeline hybrid + fallback.

    Returns:
        List of {'content', 'score', 'metadata', 'source': 'hybrid'|'pageindex'}.
    """
    # 1) Dense + sparse (lấy dư top_k*2 để rerank chọn lại).
    dense = semantic_search(query, top_k=top_k * 2)
    sparse = lexical_search(query, top_k=top_k * 2)

    # 2) Merge bằng RRF → đánh dấu nguồn hybrid.
    merged = rerank_rrf([dense, sparse], top_k=top_k * 2)
    for item in merged:
        item["source"] = "hybrid"

    # 3) Rerank cross-encoder (điểm 0..1). Lỗi Jina → giữ kết quả RRF.
    if use_reranking and merged:
        try:
            final = rerank(query, merged, top_k=top_k, method=RERANK_METHOD)
            for item in final:
                item["source"] = "hybrid"
        except Exception as e:
            print(f"  ⚠ Rerank lỗi ({e}); dùng kết quả RRF.")
            final = merged[:top_k]
    else:
        final = merged[:top_k]

    # 4) Fallback PageIndex khi hybrid rỗng, hoặc điểm rerank dưới ngưỡng.
    weak = use_reranking and final and final[0]["score"] < score_threshold
    if not final or weak:
        try:
            fallback = pageindex_search(query, top_k=top_k)
        except Exception as e:
            print(f"  ⚠ PageIndex fallback lỗi ({e}).")
            fallback = []
        if fallback:
            return fallback[:top_k]

    return final[:top_k]


if __name__ == "__main__":
    test_queries = [
        "Hình phạt cho tội tàng trữ trái phép chất ma túy",
        "Nghệ sĩ nào bị bắt vì sử dụng ma túy",
        "Quy trình cai nghiện ma túy bắt buộc",
    ]
    for q in test_queries:
        print(f"\nQuery: {q}\n" + "-" * 60)
        for i, r in enumerate(retrieve(q, top_k=3), 1):
            src_file = (r["metadata"].get("source") or r["metadata"].get("title") or "?")
            print(f"  {i}. [{r['score']:.3f}] [{r['source']}] ({src_file}) {r['content'][:65].strip()}...")
