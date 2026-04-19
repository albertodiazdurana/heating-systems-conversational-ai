# Heating Systems Conversational AI — Memory Index

## Latest Session
**Session 7 — 2026-04-18 / 2026-04-19:** Inbox processing for Sprint 2 align warnings (W1 reject, W2 BL-003 plan → done/ + 3 README path/content fixes, W3 Sprint 1 plan status In execution → Done 7/7). Sprint 1 plan + BL-003 plan now in `dsm-docs/plans/done/`. Sprint 2 Phase 1 reached Gate 1 (collaborative definition: 7 threads T1-T7, deps `haystack-ai`+`ollama-haystack` via `uv add`); no implementation written. Confirmed package manager is `uv` (uv.lock authoritative), README §2 setup commands stale (`pip install -e .` predates uv adoption), flagged for sprint-close cleanup.

## Previous Session
**Session 6 — 2026-04-18:** Sprint 1 closed 7/7, BL-003 done via `.venv` rebuild on Python 3.12.13. Sprint 2 kicked off: `sprint-2/rag-pipeline` Level-3 branch + Template 8 plan doc with EXP-001 hit@5 + EXP-002 Haystack spike, GE contribution playbook integrated as MUSTs.

## Key decisions
- **Orchestration:** hybrid LangGraph (agent) + Haystack (RAG subsystem behind a LangChain @tool boundary). See `dsm-docs/decisions/2026-04-07_orchestration-framework.md`.
- **Sprint 1 canonical stack:** `langchain.agents.create_agent` + `ChatOllama` + `InMemorySaver` + `@tool` + bilingual system prompt. See `dsm-docs/research/2026-04-07_langgraph-best-practices.md`.
- **Default model:** `llama3.1:8b` per evidence-weighted research. Cascade: `llama3.1:8b` → `llama3.2:3b` → `qwen3:4b` → `LLM_PROVIDER=openai`. See `dsm-docs/research/2026-04-17_local-model-selection_research.md`.
- **Python runtime (S6):** `.venv` built on Python 3.12.13 via `/usr/bin/python3.12`. `/usr/bin/python3.11` on this WSL is 3.11.0rc1 and must not be used.
- **Error handling (§5.4, BL-002 edit 4):** `create_agent` propagates tool exceptions by default. Production tools raise plain `ValueError` → `app.py` try/except is the primary safety net. Per-tool `ToolException` recovery deferred to Sprint 3.
- **standard_lookup overview mode (S5):** empty/missing key returns overview shape (standard, scope, available_keys, note) instead of raising.
- **Sprint 2 branch model (S6):** Level-3 `sprint-2/rag-pipeline` off session-6; per-session branches off sprint-2; sprint-2 merges to main at sprint close only (plan doc stays on sprint-2 until then). BL-003 closure (session-6 work) merges to main at Session 6 wrap-up.
- **GE contribution playbook adopted (S6):** capability-experiment-as-contribution-pipeline, issue-first, PR-conditional on maintainer response. See `_inbox/done/2026-04-13_dsm-graph-explorer_contribution-playbook.md` and Sprint 2 plan EXP-002.

## Pending
- Sprint 2 Phase 1 entry point ready: Gate 1 brief approved (T1-T7), execute T2 onward (`uv add haystack-ai ollama-haystack`, write `scratch/haystack_ollama_tools_spike.py`, run, classify outcome, write `dsm-docs/research/2026-MM-DD_haystack-ollama-tools-spike-result.md`, draft Haystack issue text).
- Sprint 2 Phase 2: embedding model micro-benchmark (e5-base vs bge-m3 vs paraphrase-multilingual-mpnet). Lock winner into pyproject + backbone §2.
- Sprint 2 Phases 3-5 remain: ingestion, retrieval + `rag_search` tool, tests + EXP-001 hit@5 + upstream contribution issue filing.
- Open design questions logged in plan §Open Design Questions (6 items); key ones: monolithic vs specialized `rag_search`, embedding winner, chunking robustness.
- README §2 setup is stale (uses `pip install -e .` instead of `uv sync`); fix at Sprint 2 close, not in-flight.
- `.venv.old-rc1/` kept as fallback; safe to delete once Sprint 2 Phase 1 starts cleanly.

## Memories
- [DSM Central propagation queue](project_dsm_central_pending.md) — pattern/ecosystem-scoped lessons awaiting upstream push to DSM Central.
