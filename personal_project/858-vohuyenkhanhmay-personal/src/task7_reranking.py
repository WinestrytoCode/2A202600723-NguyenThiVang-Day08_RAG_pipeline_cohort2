"""
Task 7 — Reranking Module.

3 cơ chế:
    - rerank_cross_encoder: cross-encoder LOCAL (BAAI/bge-reranker-v2-m3) — đường chính.
    - rerank_rrf: Reciprocal Rank Fusion — gộp nhiều ranked list (dùng ở Task 9).
    - rerank_mmr: Maximal Marginal Relevance — vừa relevant vừa diverse.

rerank() là interface thống nhất (mặc định cross_encoder).

Ghi chú: ban đầu dùng Jina Reranker API nhưng key hết balance → chuyển sang
cross-encoder local (miễn phí, chạy CPU, điểm 0..1 sau sigmoid → khớp ngưỡng Task 9).
Muốn nhẹ hơn: đổi RERANK_MODEL = "BAAI/bge-reranker-base" (~1.1GB).
"""

import numpy as np

RERANK_MODEL = "BAAI/bge-reranker-v2-m3"  # ~2.3GB, multilingual, tốt cho tiếng Việt
_reranker = None


def _get_reranker():
    """CrossEncoder local (lazy load, cache). Lần đầu tải ~2.3GB về HF cache."""
    global _reranker
    if _reranker is None:
        from sentence_transformers import CrossEncoder
        _reranker = CrossEncoder(RERANK_MODEL, max_length=512)
    return _reranker


def rerank_cross_encoder(query: str, candidates: list[dict], top_k: int = 5) -> list[dict]:
    """Rerank bằng cross-encoder local. Trả contract dicts, score 0..1 sorted DESC."""
    if not candidates:
        return []

    try:
        model = _get_reranker()
        logits = model.predict(
            [(query, c["content"]) for c in candidates], convert_to_numpy=True
        )
        probs = 1.0 / (1.0 + np.exp(-np.asarray(logits, dtype=float)))  # sigmoid → 0..1
        ranked = sorted(zip(candidates, probs), key=lambda x: x[1], reverse=True)[:top_k]
        return [
            {"content": c["content"], "score": float(p), "metadata": c.get("metadata", {})}
            for c, p in ranked
        ]
    except Exception as e:
        # Graceful fallback: giữ thứ tự theo điểm sẵn có nếu model lỗi.
        print(f"  ⚠ Local reranker lỗi ({e}); fallback giữ thứ tự điểm sẵn có.")
        fb = sorted(candidates, key=lambda c: c.get("score", 0.0), reverse=True)[:top_k]
        return [
            {"content": c["content"], "score": float(c.get("score", 0.0)), "metadata": c.get("metadata", {})}
            for c in fb
        ]


def rerank_rrf(ranked_lists: list[list[dict]], top_k: int = 5, k: int = 60) -> list[dict]:
    """
    Reciprocal Rank Fusion: RRF(d) = Σ 1/(k + rank_r(d)), rank tính từ 1.
    Dedup theo (source, chunk_index) nếu có, fallback theo content.
    """
    def _key(item):
        m = item.get("metadata") or {}
        if m.get("source") is not None and m.get("chunk_index") is not None:
            return (m["source"], m["chunk_index"])
        return item["content"]

    rrf_scores: dict = {}
    representative: dict = {}
    for ranked_list in ranked_lists:
        for rank, item in enumerate(ranked_list, start=1):
            key = _key(item)
            rrf_scores[key] = rrf_scores.get(key, 0.0) + 1.0 / (k + rank)
            representative[key] = item

    out = []
    for key, score in sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]:
        item = dict(representative[key])
        item["score"] = float(score)
        out.append(item)
    return out


def _cosine(a, b) -> float:
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    denom = float(np.linalg.norm(a) * np.linalg.norm(b)) or 1e-12
    return float(np.dot(a, b) / denom)


def rerank_mmr(
    query_embedding: list[float],
    candidates: list[dict],
    top_k: int = 5,
    lambda_param: float = 0.7,
) -> list[dict]:
    """
    MMR = λ·sim(query, doc) − (1−λ)·max(sim(doc, đã chọn)).
    Mỗi candidate cần key 'embedding' (vector bge-m3 1024-dim).
    """
    selected: list[int] = []
    remaining = list(range(len(candidates)))

    while remaining and len(selected) < top_k:
        best_idx, best_score = None, float("-inf")
        for idx in remaining:
            relevance = _cosine(query_embedding, candidates[idx]["embedding"])
            max_sim = max(
                (_cosine(candidates[idx]["embedding"], candidates[s]["embedding"]) for s in selected),
                default=0.0,
            )
            mmr = lambda_param * relevance - (1 - lambda_param) * max_sim
            if mmr > best_score:
                best_idx, best_score = idx, mmr
        selected.append(best_idx)
        remaining.remove(best_idx)

    # Score giảm dần theo thứ tự chọn để giữ contract sort DESC.
    results = []
    for rank, idx in enumerate(selected):
        results.append({
            "content": candidates[idx]["content"],
            "score": float(len(selected) - rank),
            "metadata": candidates[idx].get("metadata", {}),
        })
    return results


def rerank(
    query: str,
    candidates: list[dict],
    top_k: int = 5,
    method: str = "cross_encoder",  # "cross_encoder" | "mmr" | "rrf"
) -> list[dict]:
    """Interface thống nhất. mmr/rrf cần tham số riêng nên gọi hàm trực tiếp."""
    if method == "cross_encoder":
        return rerank_cross_encoder(query, candidates, top_k)
    elif method == "mmr":
        raise NotImplementedError("Gọi rerank_mmr(query_embedding, candidates, ...) trực tiếp")
    elif method == "rrf":
        raise NotImplementedError("Gọi rerank_rrf(ranked_lists, ...) trực tiếp")
    else:
        raise ValueError(f"Unknown rerank method: {method}")


if __name__ == "__main__":
    candidates = [
        {"content": "Điều 249. Tội tàng trữ trái phép chất ma túy, phạt tù 1-5 năm.",
         "score": 0.6, "metadata": {"source": "blhs", "chunk_index": 0}},
        {"content": "Ca sĩ X bị bắt vì sử dụng ma túy tại quán bar.",
         "score": 0.7, "metadata": {"source": "news", "chunk_index": 0}},
        {"content": "Hướng dẫn lập trình Python cơ bản cho người mới.",
         "score": 0.8, "metadata": {"source": "misc", "chunk_index": 0}},
    ]
    print("Cross-encoder (local bge-reranker-v2-m3):")
    for r in rerank("hình phạt tàng trữ trái phép chất ma túy", candidates, top_k=3):
        print(f"  [{r['score']:.4f}] {r['content'][:55]}")

    print("RRF merge (2 ranked lists):")
    for r in rerank_rrf([candidates, list(reversed(candidates))], top_k=3):
        print(f"  [{r['score']:.4f}] {r['content'][:55]}")
