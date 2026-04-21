# Heating Systems Conversational AI — Memory Index

## Latest Session
**Session 9 — 2026-04-21/22:** Resource-constrained productive session on Sonnet 4.6 (91% all-models used). Setup: resource-aware sprint planning formalized (BL proposal to DSM Central, Sprint 2 plan annotation, subscription file corrected Thu 21:00/Mon 09:59). Sprint 2 Phase 1 T2-T5 complete: `haystack-ai 2.28.0` + `ollama-haystack 6.3.0` installed; EXP-002 spike Outcome A (full tool-calling round-trip with llama3.1:8b). Phase 2 benchmark run: e5-base gap 0.10/20.7 texts/s vs bge-m3 gap 0.26/6.4 texts/s; model selection deferred to Opus. New artifact type designed: `dsm_provenance_DAG.md` (BL-004 for Sprint 1 completion; second BL to DSM Central). Feedback file `2026-04-21_s9_backlogs.md` has two BL proposals.

## Previous Session
**Session 8 — 2026-04-19/21:** Maintenance. `/dsm-align` surfaced DSM v1.5.4→v1.6.3 delta (9 spoke actions). No code work.

## Key decisions
- **Orchestration:** hybrid LangGraph (agent) + Haystack (RAG subsystem behind a LangChain @tool boundary). See `dsm-docs/decisions/2026-04-07_orchestration-framework.md`.
- **Sprint 1 canonical stack:** `langchain.agents.create_agent` + `ChatOllama` + `InMemorySaver` + `@tool` + bilingual system prompt. See `dsm-docs/research/2026-04-07_langgraph-best-practices.md`.
- **Default model:** `llama3.1:8b`. Cascade: `llama3.1:8b` → `llama3.2:3b` → `qwen3:4b` → `LLM_PROVIDER=openai`. See `dsm-docs/research/2026-04-17_local-model-selection_research.md`.
- **Python runtime (S6):** `.venv` built on Python 3.12.13 via `/usr/bin/python3.12`. `/usr/bin/python3.11` on this WSL is 3.11.0rc1 — must not be used.
- **Sprint 2 branch model (S6):** Level-3 `sprint-2/rag-pipeline` off session-6; per-session branches off sprint-2; sprint-2 merges to main at sprint close only.
- **EXP-002 result (S9):** Outcome A — Haystack `OllamaChatGenerator(tools=[...])` + llama3.1:8b full tool-calling round-trip confirmed. RAG-behind-@tool architecture validated.
- **Embedding benchmark (S9):** bge-m3 gap 2.6× larger than e5-base (0.26 vs 0.10); e5-base 3.2× faster on CPU. Selection decision pending Opus turn post-Thu 21:00.
- **Resource-aware sprint planning (S9):** pool topology (all-models-weekly/sonnet-only) drives task ordering, not deferral. Convention added to Sprint 2 plan; BL sent to DSM Central.

## Pending
- **Phase 1 T6+T7 (post-Thu 21:00 Opus):** T6 = draft Haystack upstream issue text; T7 = Gate 1 re-brief applying BL-402 (§8.7) + BL-385 (§8.2.1 counter-evidence).
- **Phase 2 model selection (Opus):** bge-m3 vs e5-base decision based on benchmark. Lock winner into pyproject + backbone §2.
- **DSM v1.6.x spoke actions still pending:** BL-385, BL-386/387, BL-344, BL-345 (DSM_7.0 §2.1), BL-239. BL-402 partially applied (resource-aware ordering). Full list in `.claude/last-align-report.md`.
- **BL-004:** Complete Sprint 1 provenance section in `dsm-docs/plans/dsm_provenance_DAG.md` (5-task audit of Sprint 1 research/decisions not in active S9 context).
- **Sprint 2 Phases 3-5:** ingestion, retrieval + `rag_search` tool, tests + EXP-001 hit@5 + upstream contribution filing. After Phase 2 decision.
- **README §2 stale** (`pip install -e .` → `uv sync`): fix at Sprint 2 close.
- `.venv.old-rc1/` safe to delete once Sprint 2 Phase 1 confirmed clean (confirmed in S9).

## Memories
- [DSM Central propagation queue](project_dsm_central_pending.md) — pattern/ecosystem-scoped lessons awaiting upstream push to DSM Central.
