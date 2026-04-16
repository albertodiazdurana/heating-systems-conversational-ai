# Sprint 1 Plan — LangGraph Conversation Engine

**Date:** 2026-04-07 (revised 2026-04-08)
**Status:** Draft (concept gate, awaiting approval)
**Supersedes:** `done/2026-04-07_sprint1_haystack_plan.md`
**Backbone:** `2026-04-07_e2e_hybrid_backbone.md`
**Decision:** `2026-04-07_orchestration-framework.md`
**Research:** `2026-04-07_langgraph-best-practices.md`

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

- [ ] All 5 tool unit tests green
- [ ] Graph construction smoke test green
- [ ] `streamlit run app.py` starts without error
- [ ] All 5 manual smoke test queries (section 4.11) produce expected
      tool call or deflection
- [ ] **Gating: German tool-call works end-to-end on the default Ollama
      model.** Query "Berechne die Vorlauftemperatur bei -10°C mit Steigung
      1.2" must trigger the `heating_curve` tool and return a correct
      German-language response. If this fails on `qwen2.5:7b`, document the
      observed failure and switch `LLM_PROVIDER=openai` as the Sprint 1
      baseline; do not treat the failure as a decision reversal (per
      groundedness assessment, BL-002 edit 1)
- [ ] README has "run locally" section
- [ ] `pyproject.toml` pinned deps, no haystack-* deps yet

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