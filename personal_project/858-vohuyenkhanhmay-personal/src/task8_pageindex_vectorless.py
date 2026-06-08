"""
Task 8 — PageIndex Vectorless RAG.

API thật (pageindex SDK, PageIndexClient):
    submit_document(pdf) → doc_id  (PDF only, async: OCR + tree)
    get_document(doc_id) → {status, pageNum, ...}
    submit_query(doc_id, query) → retrieval_id   (async)
    get_retrieval(retrieval_id) → {status, retrieved_nodes:[{title, node_id,
        relevant_contents:[{page_index, relevant_content}]}]}

PageIndex KHÔNG trả score số → tổng hợp score theo rank (kết quả đầu ≈ 1.0)
để tương thích ngưỡng fallback của Task 9.

doc_id được cache vào data/pageindex_doc.json để KHÔNG upload lại (đỡ tốn credit).

Chạy:
    python -m src.task8_pageindex_vectorless
"""

import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
LEGAL_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"
# Upload 1 văn bản text vừa phải (tránh BLHS rất nhiều trang → tốn credit).
DEFAULT_PDF = LEGAL_DIR / "luat-phong-chong-ma-tuy-2021.pdf"
CACHE_FILE = Path(__file__).parent.parent / "data" / "pageindex_doc.json"

_client = None


def _get_client():
    global _client
    if _client is None:
        from pageindex import PageIndexClient
        _client = PageIndexClient(api_key=PAGEINDEX_API_KEY)
    return _client


def _wait_processed(doc_id: str, timeout: int = 600, interval: int = 5) -> dict:
    """Poll get_document tới khi status == completed."""
    pi = _get_client()
    deadline = time.time() + timeout
    while time.time() < deadline:
        meta = pi.get_document(doc_id)
        status = meta.get("status")
        if status == "completed":
            return meta
        if status == "failed":
            raise RuntimeError(f"PageIndex xử lý thất bại: {doc_id}")
        time.sleep(interval)
    raise TimeoutError(f"PageIndex chưa xử lý xong sau {timeout}s: {doc_id}")


def _cached_doc_id():
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text(encoding="utf-8")).get("doc_id")
    return None


def upload_document(pdf_path=DEFAULT_PDF, force: bool = False) -> str:
    """Upload PDF lên PageIndex (cache doc_id, reuse nếu đã upload). Trả doc_id."""
    pi = _get_client()
    pdf_path = Path(pdf_path)

    if not force and CACHE_FILE.exists():
        cached = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        if cached.get("source") == pdf_path.name and cached.get("doc_id"):
            print(f"  ↺ Reuse doc_id đã upload: {cached['doc_id']} ({pdf_path.name})")
            return cached["doc_id"]

    print(f"  ↑ Upload {pdf_path.name} → PageIndex (OCR + tree, async)...")
    doc_id = pi.submit_document(str(pdf_path))["doc_id"]
    meta = _wait_processed(doc_id)
    CACHE_FILE.write_text(
        json.dumps({"doc_id": doc_id, "source": pdf_path.name}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"  ✓ Xong: doc_id={doc_id} ({meta.get('pageNum')} trang)")
    return doc_id


def pageindex_search(query: str, top_k: int = 5, doc_id: str = None) -> list[dict]:
    """
    Vectorless retrieval (tree search) qua PageIndex — fallback khi hybrid yếu.

    Returns:
        List of {'content', 'score', 'metadata', 'source': 'pageindex'}.
        score tổng hợp theo rank (không phải similarity thật).
    """
    pi = _get_client()
    doc_id = doc_id or _cached_doc_id()
    if not doc_id:
        raise RuntimeError("Chưa có doc_id PageIndex — chạy upload_document() trước.")

    retrieval_id = pi.submit_query(doc_id, query, thinking=False)["retrieval_id"]

    deadline = time.time() + 180
    res = {}
    while time.time() < deadline:
        res = pi.get_retrieval(retrieval_id)
        status = res.get("status")
        if status == "completed":
            break
        if status == "failed":
            raise RuntimeError(f"PageIndex retrieval thất bại: {res}")
        time.sleep(2)

    nodes = (res.get("retrieved_nodes") or [])[:top_k]
    n = max(len(nodes), 1)
    results = []
    for rank, node in enumerate(nodes):
        # relevant_contents là list-lồng-list các dict {section_title, physical_index, relevant_content}.
        snippets, pages = [], []
        for group in node.get("relevant_contents", []):
            for c in (group if isinstance(group, list) else [group]):
                if isinstance(c, dict):
                    if c.get("relevant_content"):
                        snippets.append(c["relevant_content"])
                    if c.get("physical_index"):
                        pages.append(c["physical_index"])
        content = "\n".join(snippets) or (node.get("title") or "")
        results.append({
            "content": content,
            "score": round(1.0 - rank / n, 4),  # rank-proxy, KHÔNG phải cosine
            "metadata": {
                "title": node.get("title"),
                "node_id": node.get("id"),
                "doc_id": doc_id,
                "physical_index": pages,
            },
            "source": "pageindex",
        })
    return results


if __name__ == "__main__":
    if not PAGEINDEX_API_KEY:
        print("⚠ Hãy set PAGEINDEX_API_KEY trong .env (đăng ký tại https://pageindex.ai/)")
    else:
        doc_id = upload_document()
        for q in [
            "Quy định về cai nghiện ma túy tự nguyện",
            "Trách nhiệm của gia đình trong phòng chống ma túy",
        ]:
            print(f"\nQuery: {q}\n" + "-" * 60)
            for r in pageindex_search(q, top_k=3, doc_id=doc_id):
                title = r["metadata"]["title"]
                print(f"[{r['score']:.2f}] ({title}) {r['content'][:90].strip()}...")
