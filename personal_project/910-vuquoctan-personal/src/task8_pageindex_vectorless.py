"""
Task 8 — PageIndex Vectorless RAG.

Đăng ký tài khoản tại: https://pageindex.ai/
SDK & sample code: https://github.com/VectifyAI/PageIndex

PageIndex cho phép RAG mà không cần vector store — sử dụng
structural understanding của document thay vì embedding.

Cài đặt:
    pip install pageindex

Hướng dẫn:
    1. Đăng ký account tại pageindex.ai
    2. Lấy API key
    3. Upload documents
    4. Query sử dụng PageIndex API
"""

import json
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
INDEX_PATH = PROJECT_DIR / "data" / "index" / "chunks.json"

def upload_documents():
    print("PageIndex upload chưa cấu hình. Dùng local fallback.")

def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    if not INDEX_PATH.exists():
        return []

    chunks = json.loads(INDEX_PATH.read_text(encoding="utf-8"))

    query_terms = set(query.lower().split())
    scored = []

    for chunk in chunks:
        content = chunk["content"]
        terms = set(content.lower().split())
        score = len(query_terms.intersection(terms)) / max(len(query_terms), 1)

        if score > 0:
            scored.append({
                "content": content,
                "score": float(score),
                "metadata": chunk.get("metadata", {}),
                "source": "pageindex"
            })

    scored = sorted(scored, key=lambda x: x["score"], reverse=True)
    return scored[:top_k]