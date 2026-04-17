"""Sprint 1 step 11 manual smoke test runner.

Invokes the build_agent() result against the 5 plan §4.11 queries and
captures evidence to dsm-docs/handoffs/2026-04-17_s5_step11_smoke_test_results.md.

Not a pytest test. Run as: python scripts/smoke_test.py

Reads OLLAMA_MODEL from env (default llama3.1:8b per Sprint 1 plan §6
post-Session-5-update). The model must be already pulled via
'ollama pull llama3.1:8b' and the Ollama daemon reachable at
OLLAMA_BASE_URL (default http://localhost:11434).

Output evidence file is overwritten on each run.
"""

from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.graph import build_agent  # noqa: E402

EVIDENCE_PATH = REPO_ROOT / "dsm-docs" / "handoffs" / "2026-04-17_s5_step11_smoke_test_results.md"


@dataclass
class Query:
    qid: str
    text: str
    expected_tool: str | None
    expected_args_check: str
    language: str
    must_be_in_language: bool


QUERIES: list[Query] = [
    Query(
        qid="Q1",
        text="Convert 24 kW to kcal/h",
        expected_tool="kw_to_kcal_per_h_tool",
        expected_args_check="kw=24",
        language="EN",
        must_be_in_language=False,
    ),
    Query(
        qid="Q2",
        text="What's DIN EN 12831?",
        expected_tool="standard_lookup_tool",
        expected_args_check="standard contains 'DIN EN 12831'",
        language="EN",
        must_be_in_language=False,
    ),
    Query(
        qid="Q3",
        text="Heating curve flow temp at -5°C with slope 1.0",
        expected_tool="heating_curve_tool",
        expected_args_check="outdoor_temp_c=-5, slope=1.0",
        language="EN",
        must_be_in_language=False,
    ),
    Query(
        qid="Q4",
        text="Wie kalt war der Winter?",
        expected_tool=None,
        expected_args_check="DEFLECT, no tool call expected",
        language="DE",
        must_be_in_language=True,
    ),
    Query(
        qid="Q5",
        text="Berechne die Vorlauftemperatur bei -10°C mit Steigung 1.2",
        expected_tool="heating_curve_tool",
        expected_args_check="outdoor_temp_c=-10, slope=1.2",
        language="DE",
        must_be_in_language=True,
    ),
]


def preflight() -> tuple[bool, str]:
    """Return (ok, message). Verify Ollama reachable + model present."""
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    try:
        resp = requests.get(f"{base_url}/api/tags", timeout=5)
        resp.raise_for_status()
    except requests.RequestException as exc:
        return False, f"Cannot reach Ollama at {base_url}: {exc}"
    available = {m["name"] for m in resp.json().get("models", [])}
    if model not in available:
        return False, (
            f"Model '{model}' not present in Ollama. Available: "
            f"{sorted(available) or '(none)'}. Run 'ollama pull {model}' first."
        )
    return True, f"OK: {model} reachable at {base_url}"


def looks_german(text: str) -> bool:
    """Cheap heuristic: looks for German function words / characters."""
    t = text.lower()
    german_signals = [" der ", " die ", " das ", " ist ", " und ", " mit ", " bei ", " ein ", " eine "]
    if any(s in f" {t} " for s in german_signals):
        return True
    if any(c in text for c in "äöüß"):
        return True
    return False


def extract_evidence(messages: list) -> dict:
    """Walk the agent state messages, extract tool calls + final response."""
    tool_calls = []
    tool_results = []
    final_response = ""
    for msg in messages:
        msg_type = type(msg).__name__
        if msg_type == "AIMessage":
            tcs = getattr(msg, "tool_calls", None) or []
            for tc in tcs:
                tool_calls.append(
                    {
                        "name": tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", None),
                        "args": tc.get("args") if isinstance(tc, dict) else getattr(tc, "args", None),
                    }
                )
            content = getattr(msg, "content", "")
            if content and not tcs:
                final_response = content
        elif msg_type == "ToolMessage":
            tool_results.append(
                {
                    "name": getattr(msg, "name", None),
                    "content": getattr(msg, "content", None),
                }
            )
    return {
        "tool_calls": tool_calls,
        "tool_results": tool_results,
        "final_response": final_response,
    }


def run_query(agent, q: Query) -> dict:
    """Invoke agent on one query, return evidence dict + timing."""
    start = time.monotonic()
    try:
        state = agent.invoke(
            {"messages": [("user", q.text)]},
            config={"configurable": {"thread_id": f"smoke-{q.qid}"}},
        )
        elapsed = time.monotonic() - start
        evidence = extract_evidence(state["messages"])
        # Pass / fail heuristics
        called_names = [tc["name"] for tc in evidence["tool_calls"]]
        if q.expected_tool is None:
            tool_pass = len(called_names) == 0
        else:
            tool_pass = q.expected_tool in called_names
        lang_pass = (
            looks_german(evidence["final_response"])
            if q.must_be_in_language
            else True
        )
        return {
            "qid": q.qid,
            "elapsed_sec": round(elapsed, 2),
            "evidence": evidence,
            "tool_pass": tool_pass,
            "lang_pass": lang_pass,
            "overall_pass": tool_pass and lang_pass,
            "error": None,
        }
    except Exception as exc:
        return {
            "qid": q.qid,
            "elapsed_sec": round(time.monotonic() - start, 2),
            "evidence": {"tool_calls": [], "tool_results": [], "final_response": ""},
            "tool_pass": False,
            "lang_pass": False,
            "overall_pass": False,
            "error": f"{type(exc).__name__}: {exc}",
        }


def write_evidence_file(results: list[dict], model: str) -> None:
    lines = [
        "# Sprint 1 Step 11 Smoke Test Results",
        "",
        f"**Run timestamp:** {datetime.now(timezone.utc).isoformat()}",
        f"**Model:** `{model}`",
        f"**OLLAMA_BASE_URL:** `{os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')}`",
        f"**Generated by:** `scripts/smoke_test.py`",
        "",
        "Per-query evidence captured from `agent.invoke()` state. Pass / fail",
        "heuristics: tool match (expected vs called) AND language match (German",
        "required for Q4 + Q5, English-or-any for Q1-Q3).",
        "",
        "## Summary",
        "",
        "| Q | Tool pass | Lang pass | Overall | Elapsed (s) | Error |",
        "|---|---|---|---|---|---|",
    ]
    for r in results:
        lines.append(
            f"| {r['qid']} | {'✓' if r['tool_pass'] else '✗'} | "
            f"{'✓' if r['lang_pass'] else '✗'} | "
            f"{'✓' if r['overall_pass'] else '✗'} | "
            f"{r['elapsed_sec']} | {r['error'] or ''} |"
        )
    overall = all(r["overall_pass"] for r in results)
    lines.extend(["", f"**Overall: {'PASS' if overall else 'FAIL'}**", "", "---", ""])

    for r, q in zip(results, QUERIES, strict=True):
        lines.extend(
            [
                f"## {r['qid']} — {q.language}",
                "",
                f"**Query:** {q.text}",
                f"**Expected tool:** `{q.expected_tool or 'NONE (deflection)'}`",
                f"**Expected args check:** {q.expected_args_check}",
                f"**Language must be:** {q.language if q.must_be_in_language else 'any'}",
                "",
                "### Tool calls",
                "",
                "```json",
                json.dumps(r["evidence"]["tool_calls"], indent=2, default=str),
                "```",
                "",
                "### Tool results",
                "",
                "```json",
                json.dumps(r["evidence"]["tool_results"], indent=2, default=str),
                "```",
                "",
                "### Final response",
                "",
                "```",
                r["evidence"]["final_response"] or "(empty)",
                "```",
                "",
                f"**Elapsed:** {r['elapsed_sec']}s | "
                f"**Tool pass:** {'✓' if r['tool_pass'] else '✗'} | "
                f"**Lang pass:** {'✓' if r['lang_pass'] else '✗'} | "
                f"**Overall:** {'✓' if r['overall_pass'] else '✗'}",
                "",
            ]
        )
        if r["error"]:
            lines.extend([f"**Error:** `{r['error']}`", ""])
        lines.append("---")
        lines.append("")

    EVIDENCE_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    print("=== Sprint 1 step 11 smoke test ===")
    ok, msg = preflight()
    print(f"Preflight: {msg}")
    if not ok:
        return 2

    model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    print(f"Building agent with model={model}...")
    build_start = time.monotonic()
    agent = build_agent()
    print(f"Agent built in {time.monotonic() - build_start:.2f}s")

    results = []
    for q in QUERIES:
        print(f"\n--- {q.qid}: {q.text} ---")
        r = run_query(agent, q)
        if r["error"]:
            print(f"  ERROR: {r['error']}")
        else:
            called = [tc["name"] for tc in r["evidence"]["tool_calls"]]
            print(f"  Tools called: {called}")
            print(f"  Tool pass: {r['tool_pass']} | Lang pass: {r['lang_pass']} | "
                  f"Elapsed: {r['elapsed_sec']}s")
        results.append(r)

    write_evidence_file(results, model)
    print(f"\nEvidence written to: {EVIDENCE_PATH.relative_to(REPO_ROOT)}")
    overall = all(r["overall_pass"] for r in results)
    print(f"OVERALL: {'PASS' if overall else 'FAIL'}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
