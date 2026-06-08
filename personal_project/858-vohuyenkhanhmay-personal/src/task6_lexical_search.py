"""
Task 6 — Lexical Search Module (BM25).

Build BM25 index trên cùng tập chunk với Task 4 (load_documents → chunk_documents),
để kết quả lexical khớp đơn vị với semantic (phục vụ fusion ở Task 9).

Tokenize tiếng Việt: chuẩn hoá Unicode NFC + lowercase + tách theo \w (bỏ dấu câu).
Nâng cao (bonus): có thể thay bằng word-segment pyvi/underthesea.

BM25: score(q,d) = Σ IDF(qi) · tf(qi,d)·(k1+1) / (tf(qi,d) + k1·(1-b+b·|d|/avgdl)),
k1=1.5, b=0.75 (mặc định BM25Okapi).

Chạy thử:
    python -m src.task6_lexical_search
"""

import re
import unicodedata

from .task4_chunking_indexing import chunk_documents, load_documents

CORPUS: list[dict] = []   # list of {'content': str, 'metadata': dict}
_bm25 = None


def _tokenize(text: str) -> list[str]:
    """Chuẩn hoá NFC → lowercase → tách token (giữ chữ có dấu, bỏ dấu câu)."""
    return re.findall(r"\w+", unicodedata.normalize("NFC", text).lower())


def build_bm25_index(corpus: list[dict]):
    """Xây dựng BM25 index từ corpus list of {'content', 'metadata'}."""
    from rank_bm25 import BM25Okapi
    return BM25Okapi([_tokenize(doc["content"]) for doc in corpus])


def _ensure_index():
    """Lazy build: nạp corpus (chunk như Task 4) + BM25 index một lần."""
    global CORPUS, _bm25
    if _bm25 is None:
        CORPUS = [
            {"content": c["content"], "metadata": c["metadata"]}
            for c in chunk_documents(load_documents())
        ]
        _bm25 = build_bm25_index(CORPUS)
    return _bm25


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Tìm kiếm từ khóa BM25.

    Returns:
        List of {'content': str, 'score': float, 'metadata': dict}
        sorted by BM25 score descending (chỉ trả kết quả score > 0).
    """
    bm25 = _ensure_index()
    scores = bm25.get_scores(_tokenize(query))

    # Lấy top_k chỉ số điểm cao nhất.
    ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

    results = []
    for i in ranked:
        if scores[i] > 0:
            results.append({
                "content": CORPUS[i]["content"],
                "score": float(scores[i]),
                "metadata": CORPUS[i]["metadata"],
            })
    return results


if __name__ == "__main__":
    for q in [
        "Điều 249 tàng trữ trái phép chất ma túy",
        "ca sĩ Châu Việt Cường",
    ]:
        print(f"\nQuery: {q}\n" + "-" * 60)
        for r in lexical_search(q, top_k=3):
            print(f"[{r['score']:.2f}] ({r['metadata']['source']}) {r['content'][:90].strip()}...")
