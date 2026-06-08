"""
Task 6 — Lexical Search Module (BM25).

Mặc định sử dụng BM25. Nếu dùng phương pháp khác (TF-IDF, Elasticsearch,
Weaviate BM25 built-in), hãy giải thích cơ chế trong buổi demo → +5 bonus.

Cài đặt:
    pip install rank-bm25

BM25 hoạt động thế nào:
    - Term Frequency (TF): từ xuất hiện nhiều trong document → điểm cao
    - Inverse Document Frequency (IDF): từ hiếm → quan trọng hơn
    - Document length normalization: document dài không bị ưu tiên quá mức
    - Formula: score(q,d) = Σ IDF(qi) * (tf(qi,d) * (k1+1)) / (tf(qi,d) + k1*(1-b+b*|d|/avgdl))
    - k1=1.5 (term saturation), b=0.75 (length normalization)
"""

import json
import re
import numpy as np
from pathlib import Path
from rank_bm25 import BM25Okapi

PROJECT_DIR = Path(__file__).parent.parent
INDEX_PATH = PROJECT_DIR / "data" / "index" / "chunks.json"

_bm25 = None
_corpus = None
_tokenized_corpus = None

def tokenize(text: str) -> list[str]:
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return text.split()

def _load_corpus():
    global _corpus
    if _corpus is None:
        _corpus = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    return _corpus

def build_bm25_index(corpus: list[dict]):
    tokenized_corpus = [tokenize(doc["content"]) for doc in corpus]
    return BM25Okapi(tokenized_corpus)

def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    global _bm25

    corpus = _load_corpus()

    if _bm25 is None:
        _bm25 = build_bm25_index(corpus)

    tokenized_query = tokenize(query)
    scores = _bm25.get_scores(tokenized_query)

    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []
    for idx in top_indices:
        score = float(scores[idx])
        if score > 0:
            results.append({
                "content": corpus[idx]["content"],
                "score": score,
                "metadata": corpus[idx].get("metadata", {})
            })

    return results