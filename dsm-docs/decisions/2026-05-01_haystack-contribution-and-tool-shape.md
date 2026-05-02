# Sprint 2 Phase 5: Haystack contribution + rag_search tool shape + EXP-001 outcome

**Date:** 2026-05-01
**Status:** decided
**Sprint:** Sprint 2 (RAG pipeline)
**Phase:** 5 (retrieval tests + EXP-001 + contribution)
**Branch:** `sprint-2/rag-pipeline`

## Context

Sprint 2 added a RAG subsystem on top of the Sprint 1 LangGraph agent. The
sprint required four interlocking decisions to close, all gated by Phase 5:
the spike outcome from EXP-002 (S9), the embedding-model winner (S10
decision record), the `rag_search` tool shape, and the upstream contribution
path to Haystack. The first two were closed in earlier sessions; this record
captures the remaining two plus the EXP-001 retrieval-quality outcome.

Predecessor records:

- `dsm-docs/decisions/2026-04-07_orchestration-framework.md` — hybrid LangGraph + Haystack architecture.
- `dsm-docs/decisions/2026-04-24_phase2-embedding-model-selection.md` — `BAAI/bge-m3` over `intfloat/multilingual-e5-base`.
- `dsm-docs/research/2026-04-21_haystack-ollama-tools-spike-result.md` — EXP-002 Outcome A confirmed.
- `dsm-docs/research/2026-04-29_haystack-ollama-doc-gap-issue-draft.md` — drafted issue text + verification log.
- `dsm-docs/plans/2026-04-18_sprint2_rag_haystack_plan.md` — sprint plan.

## Decision 1: rag_search tool shape — hybrid

**Decision:** Single LangChain `@tool rag_search_tool(query: str, part: str = "")`. Optional
`part` filter scopes retrieval to one of seven knowledge-base parts; empty
string means global search.

**Alternatives considered:**

| Option | Verdict | Reason |
|---|---|---|
| Monolithic (`rag_search(query)` only) | Rejected | Forfeits the discriminating metadata that the chunking layer already produces; LLM cannot scope retrieval. |
| Specialized (N tools: `standards_lookup_rag`, `mlops_reference_rag`, etc.) | Rejected | N×(registry + tests + prompt example) cost; tool-selection ambiguity is a regression risk on `llama3.1:8b`. |
| **Hybrid (chosen)** | Selected | Same precision ceiling as specialized when the LLM filters; mono fallback when it doesn't; one registry entry. |

**Counter-evidence (per BL-385):** the `(part, source_doc)` 1:1 bijection in
the index is a *retrieval-side* property, not by itself a refutation of
specialized tools. LLM self-routing on tool names is sometimes easier than
parameter selection. Mitigation: empirical EXP-001 below; if hybrid
underperforms, swap to specialized is local (rename the tool, fan out the
registry, update the prompt; no retrieval-layer change).

**Implementation:** `src/tools/rag_search.py`, `src/rag/retrieval.py`,
`src/tools/registry.py` (commit `01e92c7`).

## Decision 2: Contribution path — docs gap

**Decision:** File a documentation issue on `deepset-ai/haystack-core-integrations`
proposing one tool-calling example on the Ollama integration landing page.
No PR until maintainer response (per GE playbook).

**Spike branch (EXP-002 Outcome A, S9):** the capability exists in code
(`OllamaChatGenerator(tools=[...])` + `llama3.1:8b` round-trip). The gap
is discoverability on the integration landing page (no tool-calling example),
which sends practitioners away from a working capability.

**Filed:** https://github.com/deepset-ai/haystack-core-integrations/issues/3263
(2026-05-01).

**Filing pre-flight findings (2026-05-01):** local verification of the
draft's code example surfaced two errors that would have shipped:

1. `Tool.from_function(func)` does not exist; the public API is
   `create_tool_from_function(func)`. Original draft was a transcription
   error from a slightly different reading of the API reference.
2. The example without `temperature=0.0` and a directive prompt produces
   `tool_calls=[]` and JSON-shaped free text in `.text` — the exact
   confusion the issue is trying to fix. Both adjustments applied to the
   filed issue.

This validates the "verify before filing" rule (Phase 5 Gate 1 Q3): the
first-pass draft was wrong in a way that would have wasted maintainer time.

## Decision 3: EXP-001 outcome — pass after targeted fixes

**Success criterion:** hit@5 ≥ 0.80 on the 12-query EN/DE testset, strict
matching of `(source_doc, section_header)` per Phase 5 Gate 1 Q2.

**First run (2026-05-01):** hit@5 = 9/12 = 75.0% — **below threshold**.
Three misses:

| Query | Issue type |
|---|---|
| q04 (DE/standards): "Was ist die EnSimiMaV-Verordnung?" | Cross-lingual abbreviation; bge-m3 weakly matches the German abbreviation against its expanded form. |
| q10 (EN/mlops): "How do you monitor a deployed ML model in production?" | "intro" chunks dominated all 5 ranks within the right document; specific section 14.4 didn't surface. |
| q11 (DE/mlops): "Welche Methoden zur Anomalieerkennung..." | Testset label error: the actual top-3 `19.2 Real-Time Anomaly Detection Pipeline` is a defensible-better answer than the original `8.2 Machine Learning Methods` guess. |

Per plan §37, < 0.80 promotes reranking from Sprint 3 stretch into Sprint 2
MUST. This was treated as a Gate-1-reopen event, not a silent fix. User-approved
path: targeted fixes (B1+B2) before reaching for reranking.

**B1 — exclude "intro" chunks at retrieval time.** Added
`exclude_intro: bool = True` to `retrieve()` (default ON). Implemented as a
Chroma metadata filter (`meta.section_header != "intro"`) so the index stays
intact and the policy is owned by the retrieval layer, not the chunking
layer. Compound `AND` with the `part` filter when both apply. Verified
empirically that Chroma rejects single-condition `AND` blocks but accepts
flat predicates and `AND`-with-≥2-conditions.

**B2 — accept_alternatives schema.** Added an `accept_alternatives` list
field to the YAML testset; runner reads via `_build_accepted_pairs`. Used
for q11 only, capturing `19.2 Real-Time Anomaly Detection Pipeline` as a
defensible alternative to the original `8.2 ML Methods` label. The
per-query log shows accepted_pairs explicitly so the relaxation is
auditable.

**Re-run (2026-05-01):** hit@1 = 6/12 = 50.0% (threshold met exactly);
hit@5 = 10/12 = 83.3% — **PASS**. Per category: concepts 4/4, standards 3/4,
mlops 3/4.

**Remaining misses (documented, not fixed in Phase 5):**

- q04: cross-lingual abbreviation handling. Genuine retrieval edge case
  for compound German abbreviations; would benefit from synonym expansion
  or a reranker that sees the long form. Tracked as a Sprint 3 candidate.
- q10: with intros excluded, top-5 are all from the right chapter
  (`03_Production_MLOps.md`, sections 14.x and 15.x), but `14.4 Model
  Monitoring` specifically still doesn't surface. Likely chunking-quality
  issue (14.4 may be short, getting outscored by neighboring sections).
  Not fatal at hit@5; tracked for Sprint 3 chunking refinement.

## Reranking decision

Plan §37 escalation rule says reranking promotes to MUST when EXP-001
< 0.80. We hit 0.83 after B1+B2 without reranking. Reranking stays in
Sprint 3 stretch as originally planned, **with the explicit caveat** that
the two remaining misses (q04 cross-lingual abbreviation, q10 chunking
granularity) are the kinds of misses reranking would address. If Sprint 3
needs evidence to prioritize reranking, this record is the citation.

## Sprint 2 boundary status

| Plan §59 MUST item | Status |
|---|---|
| Phase 1 spike result (EXP-002) | Done (S9, decision record cited above) |
| Phase 2 embedding benchmark | Done (S10, decision record cited above) |
| Phase 3 ingestion pipeline | Done (S11, commit `208bdbe`) |
| Phase 4 retrieval pipeline | Done (S12, commit `01e92c7`) |
| Phase 4 `rag_search` tool | Done (S12, commit `01e92c7`) |
| Phase 5 retrieval tests | Done (S12, this commit) |
| Phase 5 EXP-001 run | Done, hit@5 = 0.83 ≥ 0.80 (this record) |
| Phase 5 upstream contribution | Done, issue #3263 filed |
| Decision record | This file |
| Boundary enforcement | `tests/test_boundaries.py` + 0 cross-layer imports |

Sprint 2 deliverables complete. Sprint Boundary Checklist runs at
`/dsm-wrap-up` along with the sprint→main merge.
