**Superseded:** 2026-04-08, replaced by 2026-04-07_sprint1_langgraph_plan.md (hybrid decision)

# Sprint 1 Plan — Haystack Orchestration

**Date:** 2026-04-07
**Status:** Draft (concept gate, awaiting approval)
**Supersedes:** LangGraph-based Sprint 1 plan from 2026-04-06 checkpoint (if approved)

## 1. Decision context

Original Sprint 1 plan used LangGraph as the orchestration layer. This plan rescopes Sprint 1 around **deepset Haystack 2.x** to:

- Unify chat orchestration and RAG (Sprint 2) under one framework
- Reduce custom glue between conversation engine and retrieval pipeline
- Use Haystack's native `Agent` + `ToolInvoker` for tool-calling loop

Trade-off accepted: less idiomatic for complex cyclic agent state than LangGraph; Sprint 1's loop is shallow enough that this does not bite.

## 2. Scope (unchanged from prior plan)

**MUST**
- Conversational agent answering residential heating questions (EN/DE)
- Tool calling: unit conversion, German standard lookup, heating curve calculation
- Streamlit chat UI
- Configurable LLM provider: Ollama (default, offline) or OpenAI via `LLM_PROVIDER` env var

**SHOULD**
- German language support (LLM handles; system prompt is bilingual)
- Out-of-scope deflection (router node returns canned response for non-heating queries)

**WON'T (deferred to Sprint 2/3)**
- RAG over heating guide
- Conversation reset detection
- MLflow evaluation harness

## 3. Architecture

```
User input
   |
   v
[ChatMessageStore]  <-- per-session memory (Streamlit session_state)
   |
   v
[Pipeline]
   |
   +--> [ConditionalRouter] --(out-of-scope)--> [DeflectionGenerator] --> response
   |          |
   |          +--(in-scope)--> [Agent (ChatGenerator + ToolInvoker)]
   |                                   |
   |                                   +-- tools: unit_converter, standard_lookup, heating_curve
   |                                   |
   |                                   v
   |                              [final ChatMessage]
   v
Streamlit renders assistant message
```

**Key components:**
- `ChatGenerator`: `OllamaChatGenerator` or `OpenAIChatGenerator`, selected by `LLM_PROVIDER`
- `Agent`: Haystack 2.x `Agent` component (wraps generator + tool loop, handles tool_calls roundtrip)
- `ConditionalRouter`: lightweight in-scope classifier (LLM-based or keyword fallback) — chooses between deflection and agent
- Tools: plain Python functions wrapped as Haystack `Tool` (or `ComponentTool`) instances
- Memory: `ChatMessageStore` (Haystack experimental) or a thin wrapper around `st.session_state["messages"]`

## 4. Dependency changes

`pyproject.toml` swaps:

| Remove | Add |
|---|---|
| `langgraph` | `haystack-ai>=2.8` |
| `langchain-ollama` | `ollama-haystack` |
| `langchain-openai` | (covered by `haystack-ai`'s built-in `OpenAIChatGenerator`) |

Unchanged: `streamlit`, `pydantic`, `python-dotenv`, `pytest` (dev).
Added later (Sprint 2): `chroma-haystack`.

`.env.example`: **unchanged**. Same vars (`LLM_PROVIDER`, `OLLAMA_MODEL`, `OLLAMA_BASE_URL`, `OPENAI_API_KEY`, `OPENAI_MODEL`).

## 5. File layout

```
src/
  __init__.py
  config.py              # env loading, provider selection
  tools/
    __init__.py
    unit_converter.py    # kw <-> kcal/h, degree_days
    standard_lookup.py   # DIN EN 12831 / VDI 6030 reference values
    heating_curve.py     # ported from ~/dsm-residential-energy/
    registry.py          # wraps the three modules as Haystack Tool instances
  pipeline.py            # builds the Haystack Pipeline (router + agent)
  prompts.py             # system prompt (bilingual), deflection template
app.py                   # Streamlit chat UI
tests/
  __init__.py
  test_unit_converter.py
  test_standard_lookup.py
  test_heating_curve.py
  test_pipeline.py       # smoke test: build pipeline, no LLM call
```

Note: no `state.py` or `graph.py` — Haystack pipelines are stateless per `run()`; conversation state lives in Streamlit `session_state` and is passed in via `messages` parameter.

## 6. Build order

1. **Tools first (pure Python, no Haystack dependency)**
   1. `src/tools/unit_converter.py` + `tests/test_unit_converter.py`
      - `kw_to_kcal_per_h`, `kcal_per_h_to_kw`, `degree_days(base_temp, daily_temps)`
      - Round-trip, known reference values, HDD sequence, edge cases
   2. `src/tools/standard_lookup.py` + tests
      - Static dict of DIN EN 12831 design temps (DE regions) and VDI 6030 reference radiator data
      - Lookup by region/postal code prefix; missing key raises `KeyError`
   3. `src/tools/heating_curve.py` + tests
      - **Read `~/dsm-residential-energy/` first** to port the existing logic (cross-repo read, no write)
      - Function: `flow_temp(outside_temp, slope, offset, design_outside_temp=-12, design_flow_temp=70)`
      - Tests: known points (design temp -> design flow, +20°C -> base), monotonicity
   4. Run `pytest`, all green
2. **Tool registry**
   - `src/tools/registry.py`: build list of `Tool` instances with name, description, parameters schema, function ref
3. **Config + prompts**
   - `src/config.py`: load `.env`, return `ChatGenerator` instance based on `LLM_PROVIDER`
   - `src/prompts.py`: bilingual system prompt, deflection template
4. **Pipeline**
   - `src/pipeline.py`: `build_pipeline() -> Pipeline` with `ConditionalRouter` + `Agent`
   - `tests/test_pipeline.py`: build pipeline, assert components wired (no LLM call)
5. **Streamlit UI**
   - `app.py`: chat input, render history, call `pipeline.run({"messages": st.session_state.messages})`
6. **README update**: how to run (Ollama setup, `streamlit run app.py`), tool list, scope
7. **Move stale plan**: archive old LangGraph plan reference if any

## 7. Open questions / verification needed

Before implementation gate, verify against current Haystack 2.x docs:

1. **Agent component API stability** — `haystack.components.agents.Agent` is in `haystack-ai` since 2.8 but the exact init signature (chat_generator, tools, exit_conditions) may have shifted. Verify on first import.
2. **ToolInvoker vs Agent** — confirm whether `Agent` already wraps `ToolInvoker` internally (expected: yes) or if we need to compose manually.
3. **OllamaChatGenerator tool support** — confirm the Ollama integration supports OpenAI-style `tool_calls` in returned `ChatMessage` (depends on Ollama model: llama3.1, qwen2.5 work; older models do not).
4. **ConditionalRouter routing logic** — for in-scope classification, decide: (a) cheap LLM call with structured output, or (b) keyword heuristic. Recommendation: start with (b) for Sprint 1, upgrade in Sprint 3.

These are flagged for the implementation gate, not blockers for plan approval.

## 8. Out of scope for this plan

- RAG pipeline (Sprint 2)
- ChromaDB setup (Sprint 2)
- MLflow eval (Sprint 3)
- Docker packaging (Sprint 3)

## 9. Approval gates

- **Concept gate (this document):** approve scope and architecture
- **Implementation gate:** per-file diff review, starting with `pyproject.toml` swap and `unit_converter.py`
- **Run gate:** first end-to-end Streamlit run with Ollama