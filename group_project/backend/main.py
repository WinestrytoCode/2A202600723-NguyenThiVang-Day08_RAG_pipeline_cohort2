"""
FastAPI Backend — DrugLaw Search Engine
"""

import sys
import time
import json
from pathlib import Path
from typing import Optional
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# ── Live Query Failure Log path ────────────────────────────────────────────────
LOG_FILE = Path(__file__).parent.parent / "evaluation" / "logs" / "query_failures.jsonl"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


def _log_live_query(query: str, api_response: dict) -> None:
    """Log every user query and flag failures (top score < 0.3)."""
    results = api_response.get("results", [])
    top_score = results[0]["score"] if results else 0.0
    is_failure = top_score < 0.3 or len(results) == 0
    record = {
        "timestamp": datetime.now().isoformat(),
        "source": "live",
        "query": query,
        "mode": api_response.get("mode"),
        "total_results": api_response.get("total", 0),
        "elapsed_ms": api_response.get("elapsed_ms", 0),
        "top_score": round(top_score, 4),
        "is_failure": is_failure,
        "failure_reasons": (
            [f"Low top rerank score: {top_score:.2f} (< 0.3)"]
            if is_failure and results else
            ["No results returned"] if is_failure else []
        ),
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


_URL_CACHE = {}

def get_url_for_source(source_name: str, doc_type: str) -> Optional[str]:
    if doc_type == "legal":
        pdf_name = source_name.replace(".md", ".pdf")
        return f"/pdf/{pdf_name}"
    if doc_type != "news":
        return None
    if source_name in _URL_CACHE:
        return _URL_CACHE[source_name]
    
    json_name = source_name.replace(".md", ".json")
    json_path = Path(__file__).parent.parent.parent / "data" / "landing" / "news" / json_name
    if json_path.exists():
        try:
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)
                url = data.get("url")
                _URL_CACHE[source_name] = url
                return url
        except Exception:
            pass
    return None


app = FastAPI(title="DrugLaw Search Engine API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount frontend static files
frontend_dir = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

# Mount PDF files directory
pdf_dir = Path(__file__).parent.parent.parent / "data" / "landing" / "legal"
app.mount("/pdf", StaticFiles(directory=str(pdf_dir)), name="pdf")


# ── Lazy-load & cache các model ───────────────────────────────────────────────

_cache: dict = {}


def get_retrievers():
    if "loaded" not in _cache:
        from src.task5_semantic_search import semantic_search
        from src.task6_lexical_search import lexical_search, CORPUS
        from src.task7_reranking import rerank, rerank_rrf
        _cache["semantic_search"] = semantic_search
        _cache["lexical_search"]  = lexical_search
        _cache["rerank"]          = rerank
        _cache["rerank_rrf"]      = rerank_rrf
        _cache["corpus_size"]     = len(CORPUS)
        _cache["loaded"]          = True
    return (
        _cache["semantic_search"],
        _cache["lexical_search"],
        _cache["rerank"],
        _cache["rerank_rrf"],
    )


# ── Schemas ────────────────────────────────────────────────────────────────────

class SearchRequest(BaseModel):
    query: str
    mode: str = "hybrid"        # "hybrid" | "semantic" | "lexical"
    top_k: int = 7
    use_rerank: bool = True


class SearchResult(BaseModel):
    rank: int
    content: str
    score: float
    doc_type: str
    source: str
    chunk_index: int
    retrieval_source: str
    url: Optional[str] = None


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
    elapsed_ms: float
    total: int
    mode: str
    reranked: bool


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/")
def index():
    return FileResponse(str(frontend_dir / "index.html"))


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "corpus_size": _cache.get("corpus_size", "not loaded"),
        "models_loaded": "loaded" in _cache,
    }


@app.get("/api/query-stats")
def query_stats():
    """Return live query failure statistics from the log file."""
    if not LOG_FILE.exists():
        return {"total": 0, "failures": 0, "failure_rate": 0.0, "recent_failures": []}

    with open(LOG_FILE, encoding="utf-8") as f:
        logs = [json.loads(line) for line in f if line.strip()]

    live_logs = [l for l in logs if l.get("source") == "live"]
    failures  = [l for l in live_logs if l.get("is_failure")]
    recent_failures = sorted(failures, key=lambda x: x["timestamp"], reverse=True)[:5]

    return {
        "total": len(live_logs),
        "failures": len(failures),
        "failure_rate": round(len(failures) / len(live_logs), 3) if live_logs else 0.0,
        "recent_failures": [
            {"query": f["query"], "top_score": f["top_score"],
             "reasons": f["failure_reasons"], "ts": f["timestamp"]}
            for f in recent_failures
        ],
    }


@app.post("/api/search", response_model=SearchResponse)
def search(req: SearchRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    semantic_search, lexical_search, rerank, rerank_rrf = get_retrievers()

    t0 = time.perf_counter()

    # ── Step 1: Retrieve ────────────────────────────────────────────────────
    if req.mode == "hybrid":
        dense  = semantic_search(req.query, top_k=req.top_k * 2)
        sparse = lexical_search(req.query,  top_k=req.top_k * 2)
        raw    = rerank_rrf([dense, sparse], top_k=req.top_k * 2)
        for r in raw:
            r["retrieval_source"] = "hybrid"

    elif req.mode == "semantic":
        raw = semantic_search(req.query, top_k=req.top_k)
        for r in raw:
            r["retrieval_source"] = "semantic"

    else:  # lexical
        raw = lexical_search(req.query, top_k=req.top_k)
        for r in raw:
            r["retrieval_source"] = "lexical"

    # ── Step 2: Rerank ──────────────────────────────────────────────────────
    if req.use_rerank and raw:
        try:
            raw = rerank(req.query, raw, top_k=req.top_k, method="cross_encoder")
        except Exception:
            raw = raw[:req.top_k]
    else:
        raw = raw[:req.top_k]

    elapsed_ms = (time.perf_counter() - t0) * 1000

    # ── Step 3: Format ──────────────────────────────────────────────────────
    results = []
    for i, r in enumerate(raw, 1):
        meta = r.get("metadata", {})
        score = r.get("score", 0.0)
        results.append(SearchResult(
            rank=i,
            content=r.get("content", ""),
            score=round(float(score), 4),
            doc_type=meta.get("type", "unknown"),
            source=meta.get("source", ""),
            chunk_index=int(meta.get("chunk_index", 0)),
            retrieval_source=r.get("retrieval_source", "hybrid"),
            url=get_url_for_source(meta.get("source", ""), meta.get("type", "unknown")),
        ))

    response = SearchResponse(
        query=req.query,
        results=results,
        elapsed_ms=round(elapsed_ms, 1),
        total=len(results),
        mode=req.mode,
        reranked=req.use_rerank,
    )

    # ── Step 4: Log query for accuracy tracking ─────────────────────────────
    try:
        _log_live_query(req.query, response.model_dump())
    except Exception:
        pass  # Never let logging break the search response

    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
