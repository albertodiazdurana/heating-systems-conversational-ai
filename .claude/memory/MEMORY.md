# Heating Systems Conversational AI — Memory Index

## Latest Session
**Session 10 — 2026-04-23 / 2026-04-29 (full wrap-up):** Opus 4.7 (1M). Spanned 3 lightweight cycles + final full wrap-up on a single branch. Five deliverables: (1) /dsm-align v1.6.3→v1.7.0→v1.8.0 across cycles (with one scope-violation detour caught and corrected: out-of-scope `diff -q` on `~/.claude/commands/` fabricated spoke actions; user corrected in 4 turns). (2) Phase 1 T6 — Haystack upstream issue draft at `dsm-docs/research/2026-04-29_haystack-ollama-doc-gap-issue-draft.md`. (3) Phase 1 T7 / Phase 2 model selection — bge-m3 chosen over e5-base (gap 0.26 vs 0.10, 2.6× advantage). Decision record `dsm-docs/decisions/2026-04-24_phase2-embedding-model-selection.md`; 3 backbone edits (§2/§4/bilingual). Counter-evidence per §8.2.1 (BL-385); §8.7 (BL-402) skip-by-match. (4) BL-004 closed — provenance DAG fully mapped for Sprints 1+2. (5) Three feedback files pushed to Central (`s10_methodology`, `s10_backlogs`, `s10.L2_concurrent-session-guard`). 5 [skill]-and-[pattern]-tagged reasoning lessons.

## Previous Session
**Session 9 — 2026-04-21/22:** Resource-constrained productive session on Sonnet 4.6 (91% all-models used). Sprint 2 Phase 1 T2-T5 complete (haystack-ai+ollama-haystack installed, EXP-002 Outcome A confirmed). Phase 2 benchmark run; model selection deferred to S10 Opus turn. dsm_provenance_DAG.md artifact type designed (BL-004, closed S10).

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
Pending items are owned by the S10 checkpoint, see `dsm-docs/checkpoints/2026-04-29_s10_checkpoint.md`.

## Memories
- [DSM Central propagation queue](project_dsm_central_pending.md) — pattern/ecosystem-scoped lessons awaiting upstream push to DSM Central.
