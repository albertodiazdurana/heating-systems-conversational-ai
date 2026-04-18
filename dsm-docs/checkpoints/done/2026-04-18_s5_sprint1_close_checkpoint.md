**Consumed at:** Session 6 start (2026-04-18)

# Sprint 1 Close Checkpoint (Session 5)

**Date:** 2026-04-18 (work completed late on 2026-04-17 / early 2026-04-18 local time)
**Session:** 5 (`session-5/2026-04-17` branch)
**Sprint:** 1 — Conversation Engine + Deterministic Tools

---

## Final §6 Exit Criteria State

| Box | State | Evidence |
|---|---|---|
| All 5 tool unit tests green | ✓ | 55/55 suite total (commit `1d9ab3f`) |
| Graph construction smoke test green | ✓ | `tests/test_graph.py` from S4 cont |
| `streamlit run app.py` starts without error | ✗ documented | [BL-003](../plans/BL-003_streamlit-boot-asyncio-invalidstate.md): `asyncio.InvalidStateError` on Python 3.11.0rc1; agent layer fully working via `scripts/smoke_test.py` |
| 5 manual smoke queries produce expected behavior | ✓ | [evidence file](../handoffs/2026-04-17_s5_step11_smoke_test_results.md): 5/5 PASS |
| **Gating: German tool-call end-to-end** | ✓ | Q5 PASS: `heating_curve_tool` called with `t_outdoor=-10, slope=1.2`; response "Die Vorlauftemperatur bei -10°C mit Steigung 1,2 beträgt 56,0 °C." |
| README has "run locally" section | ✓ | commit `2700a08` |
| `pyproject.toml` pinned deps, no haystack-* yet | ✓ | from S3/S4 |

**Score: 6/7 boxes met + 1 documented gap (BL-003).** Sprint 1 substantively complete; the gap is environmental (Python rc1) not architectural.

## What shipped (cumulative across S3 + S4 lt + S4 cont + S5)

- 5 deterministic `@tool` functions: `kw_to_kcal_per_h_tool`, `kcal_per_h_to_kw_tool`, `degree_days_tool`, `standard_lookup_tool` (with overview-mode added in S5), `heating_curve_tool`
- LangGraph `langchain.agents.create_agent` wiring (migrated from deprecated `langgraph.prebuilt.create_react_agent` in S4 cont)
- Bilingual EN/DE system prompt
- `InMemorySaver` per-thread memory (one thread per Streamlit session)
- `src/config.py` factory: `LLM_PROVIDER` env routing (Ollama default, OpenAI fallback)
- `app.py` Streamlit UI (boot blocked by BL-003 but renders UI logic intact)
- `scripts/smoke_test.py` end-to-end runner (used as Streamlit substitute for verification)
- 55 pytest tests (was 50 from S4 cont, +5 from S5 standard_lookup overview tests), all green
- Sprint 1 plan retro-fitted with all DSM_2.0.C Template 8 sections (commit `66509b0`)

## What was deferred (explicit, see plan §7)

- RAG, ChromaDB, Haystack → Sprint 2
- MLflow, evaluation → Sprint 3
- Docker, deployment → Sprint 3
- Streamlit polish (streaming tokens, `SqliteSaver` persistent memory, conversation export) → Sprint 3
- Streamlit boot fix (BL-003) → Sprint 3 (or Sprint 2 prep if a working UI is needed for RAG demo)

## Decisions made this sprint

1. **Orchestration (S3):** LangGraph for agent, Haystack for RAG (hybrid). Decision artifact: `dsm-docs/decisions/2026-04-07_orchestration-framework.md`.
2. **API migration (S4 cont):** `langgraph.prebuilt.create_react_agent` → `langchain.agents.create_agent`. Caught on first pytest run after step 9 implementation; migrated in commit `ecb73a1`. Plan §5.4 updated empirically.
3. **Tool-error propagation (S4 cont, BL-002 edit 4):** `create_agent` does NOT catch tool exceptions by default; `BaseTool.handle_tool_error` only catches `ToolException`. Sprint 1 production tools raise plain `ValueError`; app-level `try/except` around `agent.invoke()` is the primary safety net. Per-tool `ToolException` recovery deferred to Sprint 3.
4. **Default model (S5):** `llama3.1:8b` per evidence-weighted research. Cascade: `llama3.1:8b` → `llama3.2:3b` → `qwen3:4b` → OpenAI. Decision artifact: `dsm-docs/research/2026-04-17_local-model-selection_research.md` (607 lines, 35+ cited sources).
5. **standard_lookup overview mode (S5):** added to handle "What is X?" overview queries without breaking existing point-lookup behavior. Surfaced empirically by Q2 of step 11 smoke test.
6. **Sprint 1 plan retro-fit (S5):** added all DSM_2.0.C Template 8 mandatory sections (Branch Strategy, Phase Boundary Checklist, Sprint Boundary Checklist, How to Resume, Research Assessment, Experiment Gate). Filed BL-A/B/C in feedback to DSM Central proposing the structural fix (extend `/dsm-align` with plan-doc audit).

## Lessons captured

- **Methodology Lesson 1 (S5):** evidence-strength scale (third-party benchmark > vendor benchmark > vendor capability claim > anecdotal) prevents the "tutorial-default convenience trail" failure mode. Filed as DSM Central feedback (`done/2026-04-17_s5_methodology.md`).
- **Methodology Lesson 2 (S5):** constraints covered by a documented plan-level fallback become *soft*, even when they look hard in isolation. Same feedback file.
- **Methodology Lesson 3 (S5):** Pre-Generation Brief Gate 2 should require the agent to surface counter-evidence to its own recommendation before asking for approval. Same feedback file. Caught two of the agent's own ranking errors via user push-back this session ("I want a different ranking based on the evidence", "Is that really §6-compliant?").
- **Plan-template gap (S5):** plans in `dsm-docs/plans/` may silently violate Template 8; no DSM tool audits this. Three BLs filed (BL-A: extend `/dsm-align`, BL-B: dedicated `/dsm-plan-align`, BL-C: `/dsm-go` Step 3.6 hard gate). Pushed to DSM Central inbox (`done/2026-04-17_s5_backlogs.md`).

## Next steps (Sprint 2 kickoff pointer)

Sprint 2 deliverables per `dsm-docs/plans/2026-04-07_e2e_hybrid_backbone.md` §4:

1. Open a `sprint-2/rag-pipeline` branch (Level-3 sprint branch, NOT session branch — recovery from the Sprint 1 deviation per the plan §1.5 retro-note)
2. Draft Sprint 2 plan from DSM_2.0.C Template 8 (do NOT inherit the Sprint 1 retro-fit pattern — start with the canonical structure)
3. Sprint 2 introduces RAG via Haystack + ChromaDB; first deliverable is the ingestion script for `~/_projects/dsm-residential-heating-ds-guide/` (~5,800 lines)
4. Sprint 2 introduces an EXP definition (per Template 8 Experiment Gate) for retrieval quality; this is the first user-facing capability sprint, so the Experiment Gate fires
5. Address BL-003 if a working Streamlit UI is needed for Sprint 2 demo, otherwise defer to Sprint 3

## Outstanding questions

- Should the Sprint 1 deviation (no Level-3 sprint branch) be reverted retroactively (PR Sprint 1 commits onto a `sprint-1/...` branch then merge to main), or just documented in plan §1.5 and accepted? Current state: documented and accepted.
- Will Sprint 2 RAG need streaming tokens in the UI to demo well? If yes, Streamlit polish (BL-003 fix + streaming) becomes a Sprint 2 prerequisite.

## Resume protocol (for Session 6 / 7)

1. Read this checkpoint top-down
2. Read `dsm-docs/handoffs/2026-04-17_s5_step11_smoke_test_evidence.md` (the pre-written form) and the corresponding `_results.md` (the filled-in evidence)
3. Read [BL-003](../plans/BL-003_streamlit-boot-asyncio-invalidstate.md) if planning to fix the Streamlit boot
4. Check `git log main..HEAD` on the active session branch for Session 5 commits (8 commits expected: 52c19cb research, 1f373f2 plan §6, 9ff8aa8 housekeeping, b881942 path fix + inbox, 2f39ecb evidence template, 0a9fcc8 methodology feedback, 9d238b9 backlog feedback push, 66509b0 plan retro-fit, 1d9ab3f step 11 + smoke, dc74397 BL-003, 2700a08 README, plus any from this final commit)
5. Decide: open Sprint 2 plan from Template 8, or fix BL-003 first?
