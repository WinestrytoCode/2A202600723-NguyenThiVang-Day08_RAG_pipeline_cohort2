"""
FastAPI Backend — DrugLaw Search Engine
"""

import sys
import time
from pathlib import Path
from typing import Optional

sys.path.append(str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

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
        ))

    return SearchResponse(
        query=req.query,
        results=results,
        elapsed_ms=round(elapsed_ms, 1),
        total=len(results),
        mode=req.mode,
        reranked=req.use_rerank,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
