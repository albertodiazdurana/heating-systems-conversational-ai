"""EXP-001 runner: retrieval quality on the curated Sprint 2 test set.

Calls the production retrieval pipeline (`src.rag.retrieval.retrieve`) for
each query in `eval/sprint2_retrieval_testset.yaml` and computes strict
hit@1 / hit@5 (a hit requires both `source_doc` AND `section_header` to
match the expected pair, per Phase 5 Gate 1 Q2).

Output:
    Per-query JSONL on stdout, then an aggregate summary table.

Exit code:
    0 if hit@5 >= 0.80 (Sprint 2 EXP-001 success criterion).
    1 otherwise. Plan §37 says <0.80 promotes reranking from Sprint 3
    stretch into Sprint 2 MUST; the non-zero exit signals that escalation
    to whoever invoked the runner.

Usage:
    uv run python eval/exp001_retrieval_quality.py
    uv run python eval/exp001_retrieval_quality.py --testset eval/sprint2_retrieval_testset.yaml --top-k 5
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.rag.retrieval import DEFAULT_TOP_K, retrieve  # noqa: E402

DEFAULT_TESTSET = REPO_ROOT / "eval" / "sprint2_retrieval_testset.yaml"
HIT5_THRESHOLD = 0.80
HIT1_THRESHOLD = 0.50


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--testset",
        type=Path,
        default=DEFAULT_TESTSET,
        help=f"Path to YAML test set (default: {DEFAULT_TESTSET}).",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=DEFAULT_TOP_K,
        help=f"Top-K to retrieve per query (default: {DEFAULT_TOP_K}).",
    )
    return parser.parse_args()


def load_testset(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    queries = data.get("queries", [])
    if not queries:
        raise ValueError(f"No queries found in {path}.")
    return queries


def _build_accepted_pairs(query_entry: dict) -> list[tuple[str, str]]:
    """Return the list of (source_doc, section_header) pairs that count as a hit.

    Always includes the primary expected pair. If `accept_alternatives` is
    present, those (source_doc, section_header) pairs are also accepted —
    used when post-hoc analysis shows the primary expected was a label
    error and another section is a defensible-better answer (logged in
    the testset's `notes` and the Phase 5 decision record).
    """
    accepted: list[tuple[str, str]] = [
        (query_entry["expected_source_doc"], query_entry["expected_section_header"]),
    ]
    for alt in query_entry.get("accept_alternatives", []) or []:
        accepted.append((alt["source_doc"], alt["section_header"]))
    return accepted


def evaluate_query(query_entry: dict, top_k: int) -> dict:
    """Run one query and return per-query log dict."""
    accepted_pairs = _build_accepted_pairs(query_entry)

    documents = retrieve(query=query_entry["query"], top_k=top_k)
    returned = [
        {
            "rank": i + 1,
            "source_doc": d.meta.get("source_doc"),
            "section_header": d.meta.get("section_header"),
            "score": d.score,
        }
        for i, d in enumerate(documents)
    ]

    def _matches(rank_entry: dict) -> bool:
        pair = (rank_entry["source_doc"], rank_entry["section_header"])
        return pair in accepted_pairs

    hit1 = bool(returned) and _matches(returned[0])
    hit5 = any(_matches(r) for r in returned)

    return {
        "id": query_entry["id"],
        "lang": query_entry["lang"],
        "category": query_entry["category"],
        "query": query_entry["query"],
        "expected": {
            "source_doc": query_entry["expected_source_doc"],
            "section_header": query_entry["expected_section_header"],
        },
        "accepted_pairs": [{"source_doc": s, "section_header": h} for s, h in accepted_pairs],
        "returned": returned,
        "hit1": hit1,
        "hit5": hit5,
    }


def print_summary(results: list[dict]) -> None:
    n = len(results)
    n_hit1 = sum(1 for r in results if r["hit1"])
    n_hit5 = sum(1 for r in results if r["hit5"])
    hit1_rate = n_hit1 / n if n else 0.0
    hit5_rate = n_hit5 / n if n else 0.0

    print("\n" + "=" * 60, file=sys.stderr)
    print(f"EXP-001 Retrieval Quality Summary  (N={n})", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"  hit@1: {n_hit1}/{n} = {hit1_rate:.2%}  (threshold {HIT1_THRESHOLD:.0%})", file=sys.stderr)
    print(f"  hit@5: {n_hit5}/{n} = {hit5_rate:.2%}  (threshold {HIT5_THRESHOLD:.0%})", file=sys.stderr)

    by_cat: dict[str, dict[str, int]] = {}
    for r in results:
        cat = r["category"]
        by_cat.setdefault(cat, {"n": 0, "hit5": 0})
        by_cat[cat]["n"] += 1
        if r["hit5"]:
            by_cat[cat]["hit5"] += 1
    print("\n  Per-category hit@5:", file=sys.stderr)
    for cat in sorted(by_cat):
        c = by_cat[cat]
        print(f"    {cat:12s} {c['hit5']}/{c['n']}", file=sys.stderr)

    misses = [r for r in results if not r["hit5"]]
    if misses:
        print(f"\n  hit@5 misses ({len(misses)}):", file=sys.stderr)
        for r in misses:
            print(f"    {r['id']} [{r['lang']}/{r['category']}]: {r['query']}", file=sys.stderr)
            print(
                f"      expected: {r['expected']['source_doc']} :: "
                f"{r['expected']['section_header']}",
                file=sys.stderr,
            )
            for ranked in r["returned"][:3]:
                print(
                    f"      rank {ranked['rank']}: "
                    f"{ranked['source_doc']} :: {ranked['section_header']} "
                    f"(score={ranked['score']:.4f})",
                    file=sys.stderr,
                )
    print("=" * 60, file=sys.stderr)


def main() -> int:
    args = parse_args()
    queries = load_testset(args.testset)

    print(f"# EXP-001  testset={args.testset}  N={len(queries)}  top_k={args.top_k}", file=sys.stderr)
    results = []
    for q in queries:
        result = evaluate_query(q, top_k=args.top_k)
        print(json.dumps(result, ensure_ascii=False))
        results.append(result)

    print_summary(results)

    n = len(results)
    hit5_rate = sum(1 for r in results if r["hit5"]) / n if n else 0.0
    return 0 if hit5_rate >= HIT5_THRESHOLD else 1


if __name__ == "__main__":
    sys.exit(main())
