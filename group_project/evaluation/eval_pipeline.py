#!/usr/bin/env python3
"""
DrugLaw Search — Evaluation & Accuracy Tracker
================================================
Module tự động:
  1. Chạy golden dataset qua Search API
  2. Tính Precision@K, Recall@K, NDCG, MRR
  3. Phát hiện các trường hợp trả lời kém / sai
  4. Ghi log JSON từng truy vấn
  5. Xuất báo cáo Markdown với phân tích worst performers

Chạy:
    python group_project/evaluation/eval_pipeline.py
    python group_project/evaluation/eval_pipeline.py --live   # monitor server
"""

import json
import sys
import time
import math
import argparse
import hashlib
import requests
from datetime import datetime
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent.parent
EVAL_DIR = Path(__file__).parent
GOLDEN_DATASET_PATH = EVAL_DIR / "golden_dataset.json"
LOG_DIR = EVAL_DIR / "logs"
QUERY_LOG_FILE = LOG_DIR / "query_failures.jsonl"
RESULTS_PATH = EVAL_DIR / "results.md"
LOG_DIR.mkdir(parents=True, exist_ok=True)

API_URL = "http://localhost:8000/api/search"

# ── Score thresholds ──────────────────────────────────────────────────────────
FAILURE_SCORE_THRESHOLD = 0.3   # Rerank score < threshold = FAILED query
KEYWORD_HIT_THRESHOLD   = 0.4   # < 40% keywords found = likely irrelevant answer
MIN_PRECISION_AT_K      = 0.4   # Precision@3 < 0.4 = warn


# =============================================================================
# 1. Golden Dataset Loader
# =============================================================================

def load_golden_dataset() -> list[dict]:
    with open(GOLDEN_DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# =============================================================================
# 2. Search API Wrapper
# =============================================================================

def search(query: str, mode: str = "hybrid", top_k: int = 7,
           use_rerank: bool = True) -> dict:
    """Hit the FastAPI search endpoint."""
    resp = requests.post(API_URL, json={
        "query": query, "mode": mode, "top_k": top_k,
        "use_rerank": use_rerank,
    }, timeout=60)
    resp.raise_for_status()
    return resp.json()


# =============================================================================
# 3. Relevance Scoring (keyword-based oracle)
# =============================================================================

def keyword_hit_score(content: str, expected_keywords: list[str]) -> float:
    """
    Returns fraction of expected keywords found in content (case-insensitive).
    Used as a proxy for ground-truth relevance when we don't have human labels.
    """
    if not expected_keywords:
        return 1.0
    content_lower = content.lower()
    hits = sum(1 for kw in expected_keywords if kw.lower() in content_lower)
    return hits / len(expected_keywords)


def doc_type_matches(result: dict, expected_doc_type: str | None) -> bool:
    if expected_doc_type is None:
        return True
    return result.get("doc_type") == expected_doc_type


def is_result_relevant(result: dict, test_case: dict,
                        kw_threshold: float = 0.25) -> bool:
    """
    A result is considered relevant if:
    - keyword hit rate >= kw_threshold, AND
    - doc_type matches (if expected)
    """
    kw_score = keyword_hit_score(result["content"], test_case["expected_keywords"])
    type_ok = doc_type_matches(result, test_case.get("expected_doc_type"))
    return kw_score >= kw_threshold and type_ok


# =============================================================================
# 4. Metrics
# =============================================================================

def precision_at_k(results: list[dict], test_case: dict, k: int = 3) -> float:
    """Precision@K: fraction of top-K results that are relevant."""
    top = results[:k]
    if not top:
        return 0.0
    relevant = sum(1 for r in top if is_result_relevant(r, test_case))
    return relevant / k


def recall_at_k(results: list[dict], test_case: dict, k: int = 5) -> float:
    """Recall@K: if there's at least 1 relevant in top-K, recall = 1 (simplified)."""
    top = results[:k]
    return 1.0 if any(is_result_relevant(r, test_case) for r in top) else 0.0


def mean_reciprocal_rank(results: list[dict], test_case: dict) -> float:
    """MRR: 1/rank of first relevant result."""
    for i, r in enumerate(results, 1):
        if is_result_relevant(r, test_case):
            return 1.0 / i
    return 0.0


def ndcg_at_k(results: list[dict], test_case: dict, k: int = 5) -> float:
    """Simplified NDCG@K using binary relevance."""
    gains = [1 if is_result_relevant(r, test_case) else 0 for r in results[:k]]
    dcg = sum(g / math.log2(i + 2) for i, g in enumerate(gains))
    ideal_gains = sorted(gains, reverse=True)
    idcg = sum(g / math.log2(i + 2) for i, g in enumerate(ideal_gains))
    return dcg / idcg if idcg > 0 else 0.0


def top_score(results: list[dict]) -> float:
    """Return the rerank score of the top result."""
    return results[0]["score"] if results else 0.0


# =============================================================================
# 5. Failure Detector
# =============================================================================

def detect_failure(test_case: dict, api_response: dict, metrics: dict) -> dict | None:
    """
    Returns a failure record if the query performed poorly, else None.
    Failure criteria:
      - Precision@3 < MIN_PRECISION_AT_K, OR
      - Top result score < FAILURE_SCORE_THRESHOLD, OR
      - No relevant result in top 5
    """
    results = api_response.get("results", [])
    reasons = []

    if metrics["precision_at_3"] < MIN_PRECISION_AT_K:
        reasons.append(f"Low Precision@3={metrics['precision_at_3']:.2f} (< {MIN_PRECISION_AT_K})")
    if metrics["top_score"] < FAILURE_SCORE_THRESHOLD:
        reasons.append(f"Low rerank score={metrics['top_score']:.2f} (< {FAILURE_SCORE_THRESHOLD})")
    if metrics["recall_at_5"] == 0.0:
        reasons.append("No relevant result in top 5")

    # Check if wrong doc_type dominates
    expected_type = test_case.get("expected_doc_type")
    if expected_type and results:
        type_mismatch = sum(1 for r in results[:3] if r.get("doc_type") != expected_type)
        if type_mismatch >= 2:
            reasons.append(f"Doc type mismatch: {type_mismatch}/3 top results are NOT '{expected_type}'")

    if reasons:
        return {
            "timestamp": datetime.now().isoformat(),
            "query_id": test_case.get("id", "unknown"),
            "query": test_case["question"],
            "category": test_case.get("category", ""),
            "difficulty": test_case.get("difficulty", ""),
            "expected_doc_type": test_case.get("expected_doc_type"),
            "failure_reasons": reasons,
            "metrics": metrics,
            "top_3_results": [
                {
                    "rank": r["rank"],
                    "source": r["source"],
                    "doc_type": r["doc_type"],
                    "score": r["score"],
                    "snippet": r["content"][:150],
                }
                for r in results[:3]
            ],
            "elapsed_ms": api_response.get("elapsed_ms", 0),
        }
    return None


# =============================================================================
# 6. Query Logger (for live user traffic)
# =============================================================================

def log_query(query: str, api_response: dict, failure: dict | None,
              source: str = "eval") -> None:
    """Append a record to query_failures.jsonl for persistent tracking."""
    record = {
        "timestamp": datetime.now().isoformat(),
        "source": source,  # "eval" | "live"
        "query": query,
        "query_hash": hashlib.md5(query.encode()).hexdigest()[:8],
        "mode": api_response.get("mode"),
        "total_results": api_response.get("total", 0),
        "elapsed_ms": api_response.get("elapsed_ms", 0),
        "top_score": top_score(api_response.get("results", [])),
        "is_failure": failure is not None,
        "failure_reasons": failure["failure_reasons"] if failure else [],
    }
    with open(QUERY_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


# =============================================================================
# 7. A/B Config Comparison
# =============================================================================

CONFIGS = {
    "hybrid_rerank": {"mode": "hybrid", "use_rerank": True},
    "hybrid_no_rerank": {"mode": "hybrid", "use_rerank": False},
    "semantic_only": {"mode": "semantic", "use_rerank": False},
    "lexical_only": {"mode": "lexical", "use_rerank": False},
}


def run_eval_for_config(config_name: str, config: dict,
                        golden: list[dict]) -> dict:
    """Run all test cases with a specific search config."""
    print(f"\n{'='*60}")
    print(f"  Config: {config_name}")
    print(f"{'='*60}")

    all_metrics = []
    failures = []

    for tc in golden:
        print(f"  [{tc['id']}] {tc['question'][:65]}...")
        try:
            resp = search(tc["question"], top_k=7, **config)
            results = resp.get("results", [])

            metrics = {
                "precision_at_3": precision_at_k(results, tc, k=3),
                "recall_at_5":    recall_at_k(results, tc, k=5),
                "mrr":            mean_reciprocal_rank(results, tc),
                "ndcg_at_5":      ndcg_at_k(results, tc, k=5),
                "top_score":      top_score(results),
            }

            failure = detect_failure(tc, resp, metrics)
            if failure:
                failures.append(failure)
                log_query(tc["question"], resp, failure, source="eval")
                print(f"    ⚠ FAIL: {' | '.join(failure['failure_reasons'])}")
            else:
                log_query(tc["question"], resp, None, source="eval")
                print(f"    ✓ P@3={metrics['precision_at_3']:.2f} "
                      f"MRR={metrics['mrr']:.2f} "
                      f"NDCG@5={metrics['ndcg_at_5']:.2f} "
                      f"score={metrics['top_score']:.2f}")

            all_metrics.append(metrics)
            time.sleep(0.3)  # Be polite to the server

        except Exception as e:
            print(f"    ✗ ERROR: {e}")
            all_metrics.append({
                "precision_at_3": 0, "recall_at_5": 0,
                "mrr": 0, "ndcg_at_5": 0, "top_score": 0,
            })

    n = len(all_metrics)
    avg = {k: sum(m[k] for m in all_metrics) / n for k in all_metrics[0]} if n else {}

    return {
        "config_name": config_name,
        "config": config,
        "n_tests": n,
        "n_failures": len(failures),
        "failure_rate": len(failures) / n if n else 0,
        "avg_metrics": avg,
        "failures": failures,
    }


# =============================================================================
# 8. Report Generator
# =============================================================================

def generate_report(ab_results: dict[str, dict]) -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# 📊 DrugLaw Search — Evaluation Report",
        f"\n_Generated: {ts}_\n",
        "---\n",
        "## 1. Config A/B Comparison\n",
        "| Config | Tests | Failures | Fail% | P@3 | Recall@5 | MRR | NDCG@5 | AvgScore |",
        "|--------|-------|----------|-------|-----|----------|-----|--------|----------|",
    ]

    for name, res in ab_results.items():
        m = res["avg_metrics"]
        lines.append(
            f"| **{name}** | {res['n_tests']} | {res['n_failures']} "
            f"| {res['failure_rate']*100:.0f}% "
            f"| {m.get('precision_at_3', 0):.3f} "
            f"| {m.get('recall_at_5', 0):.3f} "
            f"| {m.get('mrr', 0):.3f} "
            f"| {m.get('ndcg_at_5', 0):.3f} "
            f"| {m.get('top_score', 0):.3f} |"
        )

    # Pick best config
    best = max(ab_results.items(),
               key=lambda x: x[1]["avg_metrics"].get("ndcg_at_5", 0))
    lines.append(f"\n> 🏆 **Best config by NDCG@5:** `{best[0]}`\n")

    # Worst performers
    lines.append("---\n## 2. Worst Performers\n")
    all_failures = []
    for res in ab_results.values():
        all_failures.extend(res["failures"])

    # Deduplicate by query
    seen = set()
    unique_failures = []
    for f in all_failures:
        if f["query"] not in seen:
            seen.add(f["query"])
            unique_failures.append(f)

    if not unique_failures:
        lines.append("✅ No failures detected!\n")
    else:
        for i, f in enumerate(unique_failures, 1):
            lines.append(f"### {i}. [{f['query_id']}] `{f['query'][:80]}`")
            lines.append(f"- **Category:** {f['category']} | **Difficulty:** {f['difficulty']}")
            lines.append(f"- **Metrics:** P@3={f['metrics']['precision_at_3']:.2f}, "
                         f"MRR={f['metrics']['mrr']:.2f}, "
                         f"score={f['metrics']['top_score']:.2f}")
            lines.append(f"- **Failure reasons:** {' | '.join(f['failure_reasons'])}")
            lines.append("\n**Top 3 Results Returned:**")
            for r in f["top_3_results"]:
                lines.append(f"  - #{r['rank']} [{r['doc_type']}] `{r['source']}` "
                             f"score={r['score']:.3f}: {r['snippet'][:100]}...")
            lines.append("")

    # Recommendations
    lines.append("---\n## 3. Improvement Recommendations\n")
    all_fail_reasons = []
    for f in unique_failures:
        all_fail_reasons.extend(f["failure_reasons"])

    doc_type_issues = sum(1 for r in all_fail_reasons if "type mismatch" in r.lower())
    low_score_issues = sum(1 for r in all_fail_reasons if "low rerank score" in r.lower())
    low_prec_issues  = sum(1 for r in all_fail_reasons if "precision" in r.lower())

    if doc_type_issues > 0:
        lines.append(f"- ⚠️ **Doc-type mismatch** ({doc_type_issues}x): "
                     "Xem xét thêm bộ lọc `doc_type` trên frontend hoặc thêm metadata "
                     "vào query để hướng retrieval về đúng loại tài liệu.")
    if low_score_issues > 0:
        lines.append(f"- ⚠️ **Low rerank score** ({low_score_issues}x): "
                     "Cân nhắc thu thập thêm dữ liệu cho các chủ đề còn thiếu "
                     "hoặc cải thiện chất lượng chunks.")
    if low_prec_issues > 0:
        lines.append(f"- ⚠️ **Low precision** ({low_prec_issues}x): "
                     "Thử tăng `CHUNK_OVERLAP` trong task4 hoặc sử dụng "
                     "SemanticChunker thay RecursiveCharacter.")
    if not unique_failures:
        lines.append("- ✅ Pipeline đang hoạt động tốt! Tiếp tục mở rộng golden dataset.")

    # Log summary
    lines.append("\n---\n## 4. Query Log Summary\n")
    if QUERY_LOG_FILE.exists():
        with open(QUERY_LOG_FILE) as f:
            logs = [json.loads(l) for l in f if l.strip()]
        total = len(logs)
        n_fail = sum(1 for l in logs if l["is_failure"])
        live_fail = sum(1 for l in logs if l["source"] == "live" and l["is_failure"])
        lines.append(f"| Metric | Value |")
        lines.append(f"|--------|-------|")
        lines.append(f"| Total logged queries | {total} |")
        lines.append(f"| Eval failures | {n_fail} |")
        lines.append(f"| Live user failures | {live_fail} |")
        lines.append(f"| Log file | `{QUERY_LOG_FILE}` |")
    else:
        lines.append("_Log file not found yet._")

    return "\n".join(lines)


# =============================================================================
# 9. Live Query Monitor (middleware-style logger)
# =============================================================================

def log_live_query(query: str, api_response: dict) -> dict | None:
    """
    Call this function from any layer that processes a real user query.
    It will detect failures and log them to query_failures.jsonl.
    Returns the failure record if one was detected, else None.
    """
    results = api_response.get("results", [])

    # Build a synthetic test case with no ground truth (we only check score)
    synthetic_tc = {
        "id": "live_" + hashlib.md5(query.encode()).hexdigest()[:6],
        "question": query,
        "expected_keywords": [],  # No ground truth in live mode
        "expected_doc_type": None,
        "category": "live",
        "difficulty": "unknown",
    }
    metrics = {
        "precision_at_3": 1.0,  # Can't compute without ground truth
        "recall_at_5":    1.0,
        "mrr":            1.0,
        "ndcg_at_5":      1.0,
        "top_score":      top_score(results),
    }

    failure = None
    if metrics["top_score"] < FAILURE_SCORE_THRESHOLD:
        failure = {
            "timestamp": datetime.now().isoformat(),
            "query_id": synthetic_tc["id"],
            "query": query,
            "category": "live",
            "difficulty": "unknown",
            "expected_doc_type": None,
            "failure_reasons": [f"Low top rerank score: {metrics['top_score']:.2f}"],
            "metrics": metrics,
            "top_3_results": [
                {"rank": r["rank"], "source": r["source"],
                 "doc_type": r["doc_type"], "score": r["score"],
                 "snippet": r["content"][:150]}
                for r in results[:3]
            ],
            "elapsed_ms": api_response.get("elapsed_ms", 0),
        }

    log_query(query, api_response, failure, source="live")
    return failure


# =============================================================================
# 10. Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="DrugLaw Search Evaluation & Accuracy Tracker"
    )
    parser.add_argument("--configs", nargs="+",
                        default=["hybrid_rerank", "hybrid_no_rerank"],
                        choices=list(CONFIGS.keys()),
                        help="Which configs to benchmark")
    parser.add_argument("--query", type=str,
                        help="Run a single query and show metrics")
    args = parser.parse_args()

    # Single-query mode
    if args.query:
        print(f"\n🔍 Running single query: {args.query}")
        try:
            resp = search(args.query, mode="hybrid", top_k=7, use_rerank=True)
            failure = log_live_query(args.query, resp)
            results = resp.get("results", [])
            print(f"\n{'─'*60}")
            print(f"  Total: {resp['total']} | Elapsed: {resp['elapsed_ms']:.0f}ms")
            for r in results[:5]:
                print(f"  #{r['rank']} [{r['doc_type']}] score={r['score']:.3f} "
                      f"source={r['source']}")
                print(f"      {r['content'][:100]}...")
            if failure:
                print(f"\n  ⚠ FAILURE detected: {' | '.join(failure['failure_reasons'])}")
                print(f"  → Logged to {QUERY_LOG_FILE}")
            else:
                print(f"\n  ✓ Query passed quality threshold")
        except Exception as e:
            print(f"  ✗ Error: {e}")
        return

    # Full evaluation mode
    print("\n" + "="*60)
    print("  🧪 DrugLaw Search — Evaluation Pipeline")
    print("="*60)

    golden = load_golden_dataset()
    print(f"\n✓ Loaded {len(golden)} test cases from golden dataset\n")

    ab_results = {}
    for config_name in args.configs:
        config = CONFIGS[config_name]
        ab_results[config_name] = run_eval_for_config(config_name, config, golden)

    # Write report
    report = generate_report(ab_results)
    RESULTS_PATH.write_text(report, encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"  ✓ Evaluation complete!")
    print(f"  📄 Report: {RESULTS_PATH}")
    print(f"  📋 Query log: {QUERY_LOG_FILE}")

    # Print summary table to stdout
    print(f"\n{'─'*60}")
    print(f"  Config Summary:")
    for name, res in ab_results.items():
        m = res["avg_metrics"]
        print(f"  [{name}]  "
              f"Fail={res['failure_rate']*100:.0f}%  "
              f"P@3={m.get('precision_at_3',0):.3f}  "
              f"MRR={m.get('mrr',0):.3f}  "
              f"NDCG@5={m.get('ndcg_at_5',0):.3f}")


if __name__ == "__main__":
    main()
