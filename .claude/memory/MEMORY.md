# Heating Systems Conversational AI — Memory Index

## Latest Session
**Session 8 — 2026-04-19 / 2026-04-21:** Short maintenance session. `/dsm-go` opened `session-8/2026-04-19` off `sprint-2/rag-pipeline` per Sprint 2 branch model. Explicit `/dsm-align` re-run surfaced DSM version jump **v1.5.4 → v1.6.3** with 9 spoke actions across v1.6.0-v1.6.3 (key ones: BL-385 counter-evidence at Gate 2, BL-402 §8.7 token-minimizing config at Gate 1, BL-386/387 default-branch + PR-merge parity, BL-345 DSM_7.0 AI Platform Guide, BL-239 vocabulary linking for blogs). `/dsm-light-wrap-up` hard-refused per BACKLOG-326 cadence gate (branch 2 days old); full `/dsm-wrap-up` ran instead. No code work this session.

## Previous Session
**Session 7 — 2026-04-18/19:** Inbox processing for Sprint 2 align warnings (W1 reject, W2 BL-003 + README path/content fixes, W3 Sprint 1 status → Done 7/7). Sprint 2 Phase 1 reached Gate 1 (T1-T7 threads, deps `haystack-ai`+`ollama-haystack` via `uv add`); no implementation written. Package manager confirmed `uv`.

## Key decisions
- **Orchestration:** hybrid LangGraph (agent) + Haystack (RAG subsystem behind a LangChain @tool boundary). See `dsm-docs/decisions/2026-04-07_orchestration-framework.md`.
- **Sprint 1 canonical stack:** `langchain.agents.create_agent` + `ChatOllama` + `InMemorySaver` + `@tool` + bilingual system prompt. See `dsm-docs/research/2026-04-07_langgraph-best-practices.md`.
- **Default model:** `llama3.1:8b` per evidence-weighted research. Cascade: `llama3.1:8b` → `llama3.2:3b` → `qwen3:4b` → `LLM_PROVIDER=openai`. See `dsm-docs/research/2026-04-17_local-model-selection_research.md`.
- **Python runtime (S6):** `.venv` built on Python 3.12.13 via `/usr/bin/python3.12`. `/usr/bin/python3.11` on this WSL is 3.11.0rc1 and must not be used.
- **Error handling (§5.4, BL-002 edit 4):** `create_agent` propagates tool exceptions by default. Production tools raise plain `ValueError` → `app.py` try/except is the primary safety net. Per-tool `ToolException` recovery deferred to Sprint 3.
- **standard_lookup overview mode (S5):** empty/missing key returns overview shape (standard, scope, available_keys, note) instead of raising.
- **Sprint 2 branch model (S6):** Level-3 `sprint-2/rag-pipeline` off session-6; per-session branches off sprint-2; sprint-2 merges to main at sprint close only. Session-N wrap-ups merge to `sprint-2/rag-pipeline`, NOT main.
- **GE contribution playbook adopted (S6):** capability-experiment-as-contribution-pipeline, issue-first, PR-conditional on maintainer response. See `_inbox/done/2026-04-13_dsm-graph-explorer_contribution-playbook.md` and Sprint 2 plan EXP-002.

## Pending
- **DSM v1.6.0-v1.6.3 spoke actions to review next `/dsm-go`:** BL-385 (§8.2.1 counter-evidence at Gate 2), BL-402 (§8.7 token-minimizing config at Gate 1 — applies to Sprint 2 Phase 1 entry), BL-386/387 (§2.1/§2.2 PR discipline), BL-344 (§1.11 Read the User's Manual), BL-345 (DSM_7.0 §2.1 Claude Code instance), BL-239 (§7.1 vocabulary linking). Full list in `.claude/last-align-report.md`.
- **Sprint 2 Phase 1 entry point ready:** Gate 1 brief approved at S7 (T1-T7), execute T2 onward (`uv add haystack-ai ollama-haystack`, write `scratch/haystack_ollama_tools_spike.py`, run, classify outcome, write `dsm-docs/research/2026-MM-DD_haystack-ollama-tools-spike-result.md`, draft Haystack issue text). Before entering Gate 1 again, apply BL-402 token-minimizing config recommendation and BL-385 counter-evidence.
- Sprint 2 Phase 2: embedding model micro-benchmark (e5-base vs bge-m3 vs paraphrase-multilingual-mpnet). Lock winner into pyproject + backbone §2.
- Sprint 2 Phases 3-5 remain: ingestion, retrieval + `rag_search` tool, tests + EXP-001 hit@5 + upstream contribution issue filing.
- README §2 setup is stale (uses `pip install -e .` instead of `uv sync`); fix at Sprint 2 close, not in-flight.
- `.venv.old-rc1/` kept as fallback; safe to delete once Sprint 2 Phase 1 starts cleanly.
- **Consider running `sync-commands.sh --deploy`** (per v1.6.0 BL-380 + BL-386) to pick up `/dsm-go` Step 2a.6 default-branch verification and `/dsm-backlog` sprint-plan template injection.

## Memories
- [DSM Central propagation queue](project_dsm_central_pending.md) — pattern/ecosystem-scoped lessons awaiting upstream push to DSM Central.
