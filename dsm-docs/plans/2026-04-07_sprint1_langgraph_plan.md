# Sprint 1 Plan — LangGraph Conversation Engine

**Date:** 2026-04-07 (revised 2026-04-08; Template 8 retro-fit 2026-04-17)
**Status:** Done (closed Session 6, 7/7 exit criteria met)
**Duration:** ~5 sessions (S3 concept → S4 cont implementation → S5 close)
**Goal:** End-to-end conversational agent with 5 deterministic tools on
LangGraph + Ollama, bilingual EN/DE, no RAG yet.
**Prerequisites:** Sprint 0 (research grounding) complete. Decision artifact
on orchestration framework filed (`2026-04-07_orchestration-framework.md`).
Research artifacts on LangGraph best practices and local-model selection
filed (`2026-04-07_langgraph-best-practices.md`,
`2026-04-17_local-model-selection_research.md`).
**Supersedes:** `done/2026-04-07_sprint1_haystack_plan.md`
**Backbone:** `2026-04-07_e2e_hybrid_backbone.md`
**Decision:** `2026-04-07_orchestration-framework.md`
**Research:** `2026-04-07_langgraph-best-practices.md`,
`2026-04-17_local-model-selection_research.md`

## 0. Template compliance note (added 2026-04-17, Session 5)

This plan was authored in 2026-04-07 before any DSM tool audited
plan-document structure against DSM_2.0.C Template 8. The original
9-section structure (§1 Scope through §9 Gates summary) was missing
several Template-8-mandated sections: Branch Strategy, Phase Boundary
Checklist, Sprint Boundary Checklist, How to Resume, Research Assessment
gate, and Experiment Gate.

Session 5 retro-fitted the missing sections (§1.5, §3.5, §6.5, §10) so
the Sprint 1 closure has a written checklist to drive it. The pre-existing
content in §1-§9 was not restructured; the additions sit alongside.

Future sprint plans (Sprint 2, Sprint 3) should use Template 8 from
DSM_2.0.C as the skeleton from creation rather than retro-fitting. See
[`dsm-docs/feedback-to-dsm/done/2026-04-17_s5_backlogs.md`](../feedback-to-dsm/done/2026-04-17_s5_backlogs.md)
for the three-layer root-cause analysis and the three backlog proposals
filed with DSM Central (BL-A: extend `/dsm-align` with plan-doc audit,
BL-B: `/dsm-plan-align` skill, BL-C: `/dsm-go` Step 3.6 hard gate).

## 0.5 Research Assessment (retro)

Per Template 8, before deliverables are detailed: "Can I describe the scope
in enough detail for a concrete task breakdown? Are there unresolved
unknowns that would make task estimates speculative?"

Sprint 1 grounding artifacts at planning time:
- `dsm-docs/research/2026-04-07_langgraph-best-practices.md` (canonical
  stack, agent factory, system prompt strategy, model survey)
- `dsm-docs/decisions/2026-04-07_orchestration-framework.md` (LangGraph
  + Haystack hybrid pattern)

Unknown at planning time, addressed mid-sprint:
- API rename `langgraph.prebuilt.create_react_agent` → `langchain.agents.create_agent`
  (caught Session 4 cont, plan §5 updated)
- Tool-error propagation behavior of `create_agent` (BL-002 edit 4,
  Session 4 cont, plan §5.4 updated empirically)
- Local model selection (originally cited tutorial defaults; re-grounded
  in Session 5 via `2026-04-17_local-model-selection_research.md`)

## 0.6 Experiment Gate (retro)

Sprint 1 introduces no new user-facing capability that requires an EXP-XXX
definition. Sprint 1 is a **scaffolding sprint**: it stands up the
LangGraph + tools + Streamlit + Ollama harness so that Sprint 2 (RAG) and
Sprint 3 (eval) can attach to it. Per Template 8, this qualifies as a
"performance-only sprint (no new capability), experiment skip justified
in sprint notes."

Sprint 2 (RAG) WILL introduce an EXP definition for the retrieval-quality
test set; that gate fires when Sprint 2 is drafted.

## 1. Scope

**Goal:** End-to-end conversational agent with 3 deterministic tools on
LangGraph + Ollama, no RAG. Sprint 2 introduces Haystack for RAG only.

### MUST
- `create_react_agent` with 3 tools: `unit_converter`, `standard_lookup`,
  `heating_curve`
- LLM provider switch: `ChatOllama(qwen2.5:7b)` default, `ChatOpenAI` via
  `LLM_PROVIDER=openai`
- Multi-turn conversation memory via `InMemorySaver` + per-session
  `thread_id`
- Streamlit chat UI (input, history, tool-call visibility)
- Bilingual (EN/DE) system prompt with canned out-of-scope deflection
- pytest: unit tests on all 3 tools + one graph-construction smoke test
- README "run locally" section

### SHOULD
- Tool-call visibility in Streamlit (collapsible / expandable sections)
- Basic tool error handling (agent returns error to model, which can retry)

### WON'T
- RAG, Haystack dependency, MLflow, conversation reset detection,
  streaming tokens

## 1.5 Branch Strategy

Per DSM_0.2 Three-Level Branching Strategy + DSM_2.0.C Template 8 Branch
Strategy guidance, multi-sprint projects should use Level-3 sprint branches
(`sprint-1/short-description`) off the session branch.

**Deviation in Sprint 1 (documented, not retroactively fixed):**
Sprint 1 work landed directly on session branches (`session-3/...`,
`session-4/...`, `session-5/...`) with PRs merging session branches to
main. No `sprint-1/...` Level-3 branch was created. This is a
methodology deviation observed in Session 5; adopting Level-3 sprint
branches is recommended for Sprint 2 onward.

Reason for the deviation: Sprint 1 spans multiple sessions, and the
`/dsm-go` session-branch creation was treated as the unit of branching.
The Level-3 sprint-branch pattern was not invoked. Recovery: Sprint 2
opens with `git checkout -b sprint-2/rag-pipeline` off the session
branch on the first Sprint 2 implementation session.

## 2. Canonical stack (from research)

| Concern | Choice |
|---|---|
| Agent | `create_react_agent` (LangGraph prebuilt) |
| Model (local) | `ChatOllama(model="qwen2.5:7b")` |
| Model (cloud) | `ChatOpenAI(model="gpt-4o-mini")` |
| Tools | `@tool` decorator, snake_case, dict returns |
| Memory | `InMemorySaver()` + `uuid4` `thread_id` per Streamlit session |
| System prompt | Bilingual, includes deflection, no router |
| Tests | pytest per-tool + smoke test on agent construction |

## 3. File layout

```
src/
  __init__.py                    # [done]
  config.py                      # env loading, model factory
  prompts.py                     # SYSTEM_PROMPT constant
  graph.py                       # build_agent() -> returns create_react_agent result
  tools/
    __init__.py                  # [done]
    registry.py                  # TOOLS list, imports the 3 tool modules
    unit_converter.py            # [done] plain Python + @tool wrapper (to add)
    standard_lookup.py
    heating_curve.py
app.py                           # Streamlit UI
tests/
  __init__.py                    # [done]
  test_unit_converter.py         # [done]
  test_standard_lookup.py
  test_heating_curve.py
  test_graph.py                  # smoke test: build_agent() succeeds
  test_tool_error_handling.py    # BL-002 edit 4: raises from a stub tool,
                                 #   asserts agent recovers gracefully
```

## 3.5 Phase Boundary Checklist (intra-sprint, per Template 8)

Sprint 1 phases retroactively identified from §4 Build order:

- **Phase 1 — Tools:** steps 1-5 (project setup + 5 deterministic tools +
  unit tests). Closed Session 4 lt with 43/43 tests green.
- **Phase 2 — Engine:** steps 6-9 (config factory + system prompt +
  build_agent + tool registry). Closed Session 4 cont with 50/50 tests
  green; included BL-002 edit 4 empirical resolution of tool-error
  propagation behavior.
- **Phase 3 — UI:** step 10 (Streamlit app). Closed Session 4 cont.
- **Phase 4 — Smoke + close:** steps 11-12 (manual smoke test + README).
  In progress Session 5 (model selection re-grounded; Ollama installed;
  pull + smoke pending).

For each phase boundary (intra-sprint), the agent should:
- [ ] Update `dsm-docs/feedback-to-dsm/` with phase observations and methodology scores
- [ ] Create a checkpoint in `dsm-docs/checkpoints/` if a significant milestone was reached
- [ ] Log decisions made during the phase in `dsm-docs/decisions/`
- [ ] Update blog journal materials (`dsm-docs/blog/journal.md`) if insights are worth sharing

## 4. Build order (10 steps)

Each step is a discrete implementation gate per App Development Protocol:
explain → approve → implement → run/test → next.

1. **Revert pyproject.toml** (already done this session)
2. **Run `uv sync`** to create venv and install deps (one-time)
3. **Add `@tool` wrapper to existing `unit_converter.py`** (keep plain
   Python function; add a thin `@tool`-decorated wrapper exposing
   `kw_to_kcal_per_h`, `kcal_per_h_to_kw`, `degree_days` as tools OR
   combine into a single `unit_converter` tool with a method parameter)
   - Decision at gate: individual tools (more LLM-friendly) vs combined
     tool with method param (fewer tools to register). Recommendation:
     individual tools for clarity.
4. **Write `src/tools/standard_lookup.py` + tests**
   - Static dict of DIN EN 12831 design temperatures (DE regions, postal
     code prefixes) and VDI 6030 reference radiator data
   - `@tool` function: `standard_lookup(standard: str, key: str) -> dict`
   - Tests: known values, missing key raises, unknown standard raises
5. **Write `src/tools/heating_curve.py` + tests**
   - **Cross-repo read first** (no write): `~/dsm-residential-energy/`
     source for heating curve logic
   - Port logic as plain Python: `flow_temp(outside_temp, slope,
     offset=0, design_outside_temp=-12, design_flow_temp=70) -> float`
   - `@tool` wrapper returning dict `{"flow_temp": ..., "inputs": ...}`
   - Tests: known points (design temp → design flow, +20°C → base),
     monotonicity, edge cases
6. **Run `pytest`** — all 3 tool modules green
7. **Write `src/config.py`**
   - `load_env()`: loads `.env`
   - `get_chat_model()`: returns `ChatOllama` or `ChatOpenAI` based on
     `LLM_PROVIDER`
   - Tests: not strictly required (thin wrapper around env) but smoke
     test that `get_chat_model()` returns the right type
8. **Write `src/prompts.py`**
   - `SYSTEM_PROMPT` constant: bilingual + deflection
   - Based on the pattern from Track A research section 5
9. **Write `src/graph.py` + `src/tools/registry.py`**
   - `registry.TOOLS = [kw_to_kcal_per_h, kcal_per_h_to_kw, degree_days,
     standard_lookup, heating_curve]`
   - `graph.build_agent(checkpointer=None)` returns
     `create_react_agent(model=get_chat_model(), tools=TOOLS,
     checkpointer=checkpointer or InMemorySaver(), prompt=SYSTEM_PROMPT)`
   - `tests/test_graph.py`: `def test_build_agent():
     assert build_agent() is not None` (smoke test, no LLM invocation)
10. **Write `app.py`** (Streamlit UI)
    - `thread_id` in `st.session_state` (uuid4 on first load)
    - Chat history in `st.session_state.messages`
    - `st.chat_input` + rendering
    - Invoke: `agent.invoke({"messages": [("user", user_input)]},
      config={"configurable": {"thread_id": st.session_state.thread_id}})`
    - Render tool calls as collapsible sections
    - Error handling: catch exceptions, show user-friendly error
11. **Manual smoke test:** `streamlit run app.py`
    - Ask: "Convert 24 kW to kcal/h" → should use `kw_to_kcal_per_h` tool
    - Ask: "What's DIN EN 12831?" → should use `standard_lookup` tool
    - Ask: "Heating curve flow temp at -5°C with slope 1.0" → should use
      `heating_curve` tool
    - Ask: "Wie kalt war der Winter?" → should use deflection (not in scope)
    - Ask: "Berechne die Vorlauftemperatur bei -10°C mit Steigung 1.2"
      → German tool call works end-to-end
12. **README update:** run instructions, tool list, architecture
    one-paragraph description

## 5. Key design decisions

### 5.1 Tool granularity: individual unit converter tools vs combined

Recommendation: **individual** (`kw_to_kcal_per_h`, `kcal_per_h_to_kw`,
`degree_days`). Rationale:
- Each tool has a focused docstring the LLM reads as description
- Combined tools need a `method` parameter that the LLM must set correctly
- Individual tools are simpler to test

Accept 5 tools total (3 unit converter + `standard_lookup` +
`heating_curve`). Small enough that LLM tool selection is not strained.

### 5.2 System prompt language strategy

Single bilingual prompt (no router, no language detection). The model
responds in the user's language. Deflection message is bilingual so it
works regardless of input language.

### 5.3 Memory scope

Sprint 1: in-process only, lost on Streamlit restart. Acceptable for
Sprint 1 exit. `SqliteSaver` upgrade deferred to Sprint 3 polish if
conversation export feature is desired.

### 5.4 Error handling

**Observed behavior** (BL-002 edit 4, verified in commit `d1941b9`,
`langchain 1.2.15` / `langgraph 1.1.6`):

1. `langchain.agents.create_agent` does **not** catch tool exceptions by
   default. A raised exception propagates through `ToolNode` to
   `agent.invoke()` and up to the caller.
2. `BaseTool.handle_tool_error` (bool / str / callable) only catches
   `ToolException` subclasses. Generic `Exception` (including
   `ValueError`) bypasses the flag and re-raises unconditionally.
3. Canonical per-tool recovery pathway: the tool raises `ToolException`
   and sets `handle_tool_error=True`; the error is returned to the
   model as a `ToolMessage` and the agent continues.

**Sprint 1 mitigation:** production tools currently raise plain
`ValueError` (e.g. `standard_lookup` on an unknown standard/key), so
the app-level try/except around `agent.invoke()` in `app.py` (step 10)
is the **primary** safety net, not a backup. Any tool exception surfaces
there as a user-facing error message.

**Deferred:** converting production tools to raise `ToolException` (with
`handle_tool_error=True`) would give per-tool model-visible recovery,
allowing the model to retry or explain. Revisit in Sprint 3 polish if
multi-tool conversations show benefit from in-loop recovery rather than
turn-level failure. See `tests/test_tool_error_handling.py` for the
reference pattern.

## 6. Exit criteria

- [x] All 5 tool unit tests green (55/55 suite total, Session 5 commit `1d9ab3f`)
- [x] Graph construction smoke test green (`tests/test_graph.py` from Session 4 cont)
- [x] `streamlit run app.py` starts without error , closed in Session 6 via [BL-003](BL-003_streamlit-boot-asyncio-invalidstate.md). `.venv` recreated on Python 3.12.13 (was 3.11.0rc1); boot banner emits cleanly on `--server.headless true --server.port 8503`, no `InvalidStateError`. Sprint 1 is now 7/7 §6 boxes. Evidence: `dsm-docs/handoffs/done/2026-04-18_s6_bl003_closure_smoke_test_results.md`.
- [x] All 5 manual smoke test queries (section 4.11) produce expected
      tool call or deflection (5/5 PASS, evidence in
      [`dsm-docs/handoffs/2026-04-17_s5_step11_smoke_test_results.md`](../handoffs/2026-04-17_s5_step11_smoke_test_results.md))
- [x] **Gating: German tool-call works end-to-end on the default Ollama
      model.** Query "Berechne die Vorlauftemperatur bei -10°C mit Steigung
      1.2" triggers `heating_curve_tool` with correct args, response in
      German with correct domain vocabulary and decimal-comma formatting:
      "Die Vorlauftemperatur bei -10°C mit Steigung 1,2 beträgt 56,0 °C."
      (`llama3.1:8b` Q4_K_M, T1000 4GB VRAM partial CPU offload, ~21s).
      Default model is `llama3.1:8b` per
      `dsm-docs/research/2026-04-17_local-model-selection_research.md`.
      Fallback ladder if the gating query fails:
      1. `llama3.2:3b` (faster, lower German quality, same template family)
      2. `qwen3:4b` (no measured evidence, vendor tool-call claim)
      3. `LLM_PROVIDER=openai`
      Document any failure in the smoke-test evidence; do not treat as a
      decision reversal (per groundedness assessment, BL-002 edit 1).
- [x] README has "run locally" section (Session 5 commit `2700a08`)
- [x] `pyproject.toml` pinned deps, no haystack-* deps yet

## 6.5 Sprint Boundary Checklist (per Template 8, customized for Sprint 1)

To be completed when all §6 exit-criteria boxes are checked. This is the
sprint-close checklist that drives the closure work end-to-end.

- [ ] Checkpoint document created (`dsm-docs/checkpoints/2026-04-XX_sprint1_close.md`)
      with: final §6 box state, what shipped vs what was deferred, evidence
      pointers (smoke-test results + commit hashes), decisions made during
      the sprint, lessons learned.
- [ ] Feedback files updated: per-session `YYYY-MM-DD_sN_backlogs.md` and/or
      `YYYY-MM-DD_sN_methodology.md` in `dsm-docs/feedback-to-dsm/` capturing
      sprint-level observations not already in per-phase entries.
- [ ] Decision log updated (`dsm-docs/decisions/`) with any sprint-level
      decisions not already filed (e.g., the model-selection cascade may
      warrant its own decision artifact).
- [ ] Tests passing (DSM 4.0): all unit + integration tests green on the
      final commit.
- [ ] Blog journal entry written (`dsm-docs/blog/journal.md`) summarizing
      Sprint 1 narrative arc, surprises, and what changed methodology-wise.
- [ ] Repository README updated (status line, model identifier, run-locally
      section, tool list, architecture paragraph, roadmap checkbox) — covered
      by step 12 in the Build order.
- [ ] Pending feedback pushed to DSM Central via `/dsm-align` Step 6 or
      direct push.
- [ ] Next steps summary (3-5 sentences): goal of Sprint 2, key
      deliverables, plan reference.
- [ ] All §6 exit-criteria boxes checked.

## 7. Deferred to later sprints (explicit)

- RAG, ChromaDB, Haystack (Sprint 2)
- MLflow, evaluation (Sprint 3)
- Docker, deployment (Sprint 3)
- Streaming tokens in UI (Sprint 3 polish)
- `SqliteSaver` persistent memory (Sprint 3 polish)
- Conversation export (Sprint 3 polish)

## 8. Open questions (not blockers)

- Which Ollama model the user actually has pulled locally — need to
  verify at step 2. If none, document `ollama pull qwen2.5:7b` in README.
- Streamlit tool-call visibility: built-in support? Custom rendering?
  Defer decision to step 10 when building the UI.
- OPENAI_API_KEY handling when `LLM_PROVIDER=ollama` — should config
  skip validation. Addressed in step 7.

## 9. Gates summary

| Gate | Action | Approval |
|---|---|---|
| Concept | This document | **← here, awaiting approval** |
| Impl 1 | Steps 1-2 (pyproject + venv) | pending |
| Impl 2 | Step 3 (unit_converter @tool wrappers) | pending |
| Impl 3 | Step 4 (standard_lookup) | pending |
| Impl 4 | Step 5 (heating_curve, cross-repo read) | pending |
| Impl 5 | Step 6 (pytest green) | pending |
| Impl 6 | Steps 7-9 (config, prompts, graph) | pending |
| Impl 7 | Step 10 (app.py) | pending |
| Run | Step 11 (manual smoke test) | pending |
| Exit | Step 12 (README) | pending |

## 10. How to Resume (per Template 8)

If you are picking up this sprint mid-flight (new session, context cold):

1. **Read this sprint plan top-down**, focus on §0 (Template compliance
   note), §6 (Exit criteria), §6.5 (Sprint Boundary Checklist), §3.5
   (Phase Boundary Checklist) to know where the sprint stands and what
   remains.
2. **Read the most recent checkpoint** in `dsm-docs/checkpoints/`
   (sorted descending). If the checkpoint is from a prior session, it
   was already moved to `done/` by `/dsm-go` Step 3.5; check there too.
3. **Read the most recent handoff** in `dsm-docs/handoffs/` (excluding
   `done/`). If a Sprint-1-specific handoff exists (e.g.,
   `2026-04-17_s5_step11_smoke_test_evidence.md`), it has structured
   continuation context.
4. **Check `git log main..HEAD` on the active session branch** for
   recent commits. The commit messages narrate what just landed.
5. **Re-read MEMORY.md** for the latest-session pointer to the most
   recent state.

For Sprint 1 specifically as of 2026-04-17:
- Implementation steps 1-10 done (Sessions 4 lt + 4 cont)
- Step 11 in progress (Session 5: model selection re-grounded; Ollama
  installed in WSL; pull + smoke test pending)
- Step 12 pending (Session 5 or 6)
- Sprint Boundary Checklist (§6.5) NOT yet started