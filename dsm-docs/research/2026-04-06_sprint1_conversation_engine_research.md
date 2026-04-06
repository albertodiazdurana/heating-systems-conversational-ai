# Sprint 1 Research: Conversation Engine + Deterministic Tools

**Purpose:** Validate assumptions in the preliminary sprint plan (`_reference/sprint-plan.md`) and ground decisions in available sources before formalizing into an actionable sprint plan.
**Target Outcome:** Formal sprint plan in `dsm-docs/plans/`
**Status:** In Progress
**Date:** 2026-04-06

---

## 1. Available Sources Inventory

### 1.1 Knowledge Base

**Location:** `~/dsm-residential-heating-ds-guide/` (verified, exists)
**Size:** 6,019 lines across 6 markdown documents

| Document | Lines | Sprint 1 Relevance |
|----------|-------|---------------------|
| 01_Domain_Fundamentals.md | 411 | HIGH — Ch.1-3: heating curve formula, standards (DIN EN 12831, VDI 6030), control variables, unit definitions |
| 02_Data_Science_ML.md | 1,085 | LOW for Sprint 1, HIGH for Sprint 2-3 |
| 03_Production_MLOps.md | 1,326 | LOW for Sprint 1 |
| 04_Technical_Stack.md | 1,323 | LOW for Sprint 1 |
| 05_Applied_Scenarios.md | 1,187 | MEDIUM — case studies inform tool design |
| 06_References.md | 163 | MEDIUM — standards bibliography for lookup tool |

### 1.2 Companion App

**Location:** `~/dsm-residential-energy-apps/` (verified, exists)
**Note:** The preliminary plan references `~/dsm-residential-energy/` which does NOT exist. Correct path is `~/dsm-residential-energy-apps/`.

**Relevant code in `models/heating-curve/app/`:**

| File | Lines | Reusable for Sprint 1? |
|------|-------|------------------------|
| simulation.py | 425 | YES — `calculate_vorlauf()` is the heating curve formula, directly adaptable as a tool |
| config.py | 365 | YES — `BUILDING_PRESETS`, `DEFAULT_CONFIG`, standards references, parameter ranges |
| analysis.py | 464 | NO — parameter extraction from noisy data, not a conversational tool |
| streamlit_app.py | ~200 | PARTIAL — UI patterns, but this is a simulation app, not a chat interface |

### 1.3 What Exists vs. What Needs to Be Built

| Component | Exists? | Source | Sprint 1 Action |
|-----------|---------|--------|-----------------|
| Heating curve formula | YES | simulation.py:calculate_vorlauf() | Adapt as LangGraph tool |
| Building presets | YES | config.py:BUILDING_PRESETS | Expose through tool parameters |
| Standard lookup data | PARTIAL | Knowledge base Ch.1-5 + 06_References.md | Extract structured standard definitions |
| Unit converter | NO | — | Build from domain knowledge |
| LangGraph state machine | NO | — | Design and implement |
| Streamlit chat UI | NO | — | Build (different from existing simulation UI) |

---

## 2. Deterministic Tools Analysis

### 2.1 Heating Curve Calculator

**Source formula** (from `simulation.py:calculate_vorlauf()`):
```
T_vorlauf = T_base + slope * (T_room - T_outdoor)
```
Clamped to `[t_min, t_max]`, with summer cutoff.

**Parameters available from config.py:**
- slope: 0.2-2.0 (building-type dependent)
- t_base: 20.0°C (DIN EN 12831 standard)
- t_room: 18-24°C (DIN EN 12831 comfort range)
- t_vorlauf_max: 45-85°C (depends on heat distribution system)
- t_vorlauf_min: 20-35°C
- summer_cutoff: 12-20°C

**Building presets ready to use:**
1. Heat Pump + Floor Heating (slope 0.3, max 55°C)
2. Radiators + Good Insulation (slope 1.0, max 65°C)
3. Radiators + Poor Insulation (slope 1.4, max 75°C)
4. Historic Building (slope 1.6, max 80°C)

**Design decision needed:** Should the tool accept raw parameters (slope, t_outdoor, etc.) or building-type presets, or both? The user interactions document (Interaction 2) shows raw parameter input. The presets add helpful context for users who don't know their building's parameters.

**Recommendation:** Accept both. Raw parameters for explicit input, preset name for convenience. The tool should also return contextual notes (e.g., "A slope of 1.8 is plausible for an unrenovated 1975 building").

### 2.2 Standard Lookup

**No existing structured data source.** The knowledge base references standards inline but doesn't have a structured lookup table.

**Standards mentioned across the knowledge base:**
- DIN EN 12831: Heating systems in buildings, design heat load calculation
- VDI 6030: Designing free heating surfaces
- VDI 2067: Economic efficiency of building installations
- DIN 4108: Thermal insulation
- DIN EN 1264: Floor heating design
- GEG (Gebäudeenergiegesetz): German Building Energy Act
- HeizKV (Heizkostenverordnung): Heating Cost Regulation
- DVGW W 551: Legionella prevention in drinking water systems

**Design decision needed:** Build a static lookup dictionary from knowledge base content, or implement as RAG over the standards sections? For Sprint 1 (no RAG yet), a static dictionary is the right approach. Sprint 2 RAG can supplement with deeper context.

**Recommendation:** Create a structured standards dictionary with: code, full name (DE + EN), scope, key parameters, related chapters. This becomes the Sprint 1 tool. Sprint 2 RAG augments it with deeper context retrieval.

### 2.3 Unit Converter

**Not implemented anywhere.** The preliminary plan mentions "kW <-> kcal/h, degree-day calculations."

**Domain-relevant conversions (from knowledge base review):**
- Power: kW <-> kcal/h (1 kW = 860 kcal/h)
- Energy: kWh <-> MJ <-> kcal (1 kWh = 3.6 MJ = 860 kcal)
- Temperature: °C <-> °F (rare in German context, but international users)
- Specific heat: kJ/(kg·K) — not a conversion, but a reference value
- U-value: W/(m²·K) — not a conversion, but a reference value
- Heating degree days: HDD = Σ max(T_base - T_outdoor, 0) per day

**Design decision needed:** Is the unit converter a standalone tool or should degree-day calculations be a separate tool? Degree-day calculation requires a time series (daily temperatures), which is more complex than a simple conversion.

**Recommendation:** Split into two tools:
1. **Unit converter:** Simple bidirectional conversions (kW<->kcal/h, kWh<->MJ, °C<->°F)
2. **Degree-day calculator:** Takes location + period, fetches weather data (reuse Open-Meteo pattern from simulation.py), returns HDD/CDD

However, the degree-day calculator adds significant complexity (API calls, date handling). Consider deferring to Sprint 2 or marking as SHOULD.

---

## 3. Architecture Analysis

### 3.1 Preliminary Plan Architecture

The preliminary plan proposes 4 LangGraph nodes:
```
intent_classifier -> tool_router -> responder -> follow_up_handler
```

**Concerns:**
1. **Rigid pipeline:** This is a sequential pipeline, not a graph. LangGraph's value is conditional routing, cycles, and state management. A fixed sequence doesn't leverage LangGraph's strengths.
2. **Intent classification as a separate node:** Modern LLM-based agents handle intent classification implicitly through tool selection. A separate intent classifier adds latency and a potential error source.
3. **Follow-up handler as a separate node:** Follow-up detection is better handled by conversation state (message history) than a dedicated node.

### 3.2 Alternative: ReAct Agent Pattern

LangGraph's recommended pattern for tool-calling agents is the ReAct (Reason + Act) loop:
```
agent (LLM decides) -> [tool_call | respond]
                    <- tool_result (loops back to agent)
```

**Advantages:**
- Simpler graph, fewer nodes
- LLM handles intent classification naturally through tool selection
- Multi-turn is handled by message history in state
- Follows LangGraph's documented patterns

**Disadvantage:**
- Less explicit control over conversation flow
- Harder to enforce domain guardrails

### 3.3 Recommendation

Start with the ReAct pattern (simpler, proven) and add explicit routing only if needed. The conversation guardrails (out-of-scope detection, deflection) can be handled through the system prompt rather than a dedicated node.

**Research completed.** See Section 4 below.

---

## 4. Technology Stack (Researched)

### 4.1 LangGraph — Version and API

**Target version:** `langgraph` 1.1.6 (latest stable, April 2026)

**Package ecosystem:**

| Package | Version | Purpose |
|---------|---------|---------|
| `langgraph` | 1.1.6 | Core framework (includes `langgraph-prebuilt`) |
| `langchain-anthropic` | 1.4.0 | Claude integration |

**ReAct agent pattern — confirmed as recommended approach:**

```python
from langchain_anthropic import ChatAnthropic
from langchain.tools import tool
from langgraph.prebuilt import create_react_agent

llm = ChatAnthropic(model="claude-sonnet-4-5")

@tool
def my_tool(query: str) -> str:
    """Tool description."""
    return "result"

graph = create_react_agent(llm, tools=[my_tool], prompt="System prompt")
result = graph.invoke({"messages": [{"role": "user", "content": "..."}]})
```

For more control, use `StateGraph` + `ToolNode` + `tools_condition`:

```python
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition

builder = StateGraph(MessagesState)
builder.add_node("llm", call_llm)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "llm")
builder.add_conditional_edges("llm", tools_condition)
builder.add_edge("tools", "llm")
graph = builder.compile()
```

**State management — extend `MessagesState` for custom fields:**

```python
from langgraph.graph import MessagesState

class State(MessagesState):
    language: str = "en"
    # add_messages reducer handles message append automatically
```

**Tool definition — `@tool` decorator with type hints:**

```python
from langchain.tools import tool

@tool
def heating_curve_calculator(
    t_outdoor: float,
    slope: float,
    t_room: float = 20.0,
) -> str:
    """Calculate Vorlauftemperatur from heating curve parameters.

    Args:
        t_outdoor: Outdoor temperature in °C
        slope: Heating curve slope (Neigung), typically 0.3-1.6
        t_room: Target room temperature in °C (default 20)
    """
    # ...
```

Type hints define the schema, docstring becomes the tool description for the LLM.

### 4.2 LLM Provider: Anthropic Claude

**Decision:** Anthropic Claude (user confirmed). Not OpenAI, not Ollama.

```python
from langchain_anthropic import ChatAnthropic

model = ChatAnthropic(
    model="claude-sonnet-4-5",  # or claude-haiku-4-5-20251001 for cost optimization
    temperature=0.7,
    max_tokens=1024,
)
```

**Tool calling:** Claude has native tool calling support via `bind_tools()`. Strict mode available (`strict=True`) for guaranteed schema compliance.

**Bilingual:** Claude handles German technical vocabulary natively. System prompt instruction ("Respond in the language the user writes in") is sufficient.

**Prompt caching:** Available for repeated large contexts (useful when system prompt includes domain glossary).

### 4.3 Bilingual Support

**Decision:** MUST (elevated from SHOULD based on user interactions document).

**Implementation:** System prompt instruction + domain glossary in system prompt. No separate translation layer. Claude handles EN/DE switching naturally.

### 4.4 Streamlit Chat UI

**Minimum viable UI for Sprint 1:**
- `st.chat_input` + `st.chat_message` for conversation
- Tool call visibility (show which tool was called and parameters)
- System message showing capabilities

**Known gotcha:** LangGraph is async, Streamlit reruns entire script. For Sprint 1, use synchronous `graph.invoke()` (simpler). Streaming (async `graph.astream()`) deferred to Sprint 3 polish.

**Session state:** Store messages in `st.session_state`. Use `thread_id` per Streamlit session for LangGraph checkpointer.

### 4.5 Testing Strategy

**Two-tier approach:**

```
tests/
  unit/
    test_tools.py           # deterministic tool functions, no LLM
    test_state.py           # state schema validation
  integration/
    test_graph.py           # full graph with real LLM calls
    test_conversations.py   # multi-turn conversation scenarios
```

**Unit tests** (fast, no API key): test tool functions in isolation, verify graph compiles.

**Integration tests** (require ANTHROPIC_API_KEY): invoke full graph, verify tool selection, check response quality.

```python
# Unit test example
def test_heating_curve_calculator():
    result = calculate_vorlauf(t_outdoor=-10, slope=1.4, t_room=20)
    assert abs(result - 62.0) < 0.1  # T_base(20) + 1.4*(20-(-10)) = 62

# Integration test example
async def test_agent_calls_calculator():
    result = await graph.ainvoke(
        {"messages": [{"role": "user", "content": "Calculate flow temp for -10°C outdoor, slope 1.4"}]}
    )
    tool_calls = [m for m in result["messages"] if hasattr(m, "tool_calls") and m.tool_calls]
    assert len(tool_calls) > 0
```

**Dependencies:** `pytest`, `anyio`, `pytest-asyncio`

---

## 5. Resolved Open Questions

| Question | Decision | Rationale |
|----------|----------|-----------|
| Companion app path | `~/dsm-residential-energy-apps/` | Verified on filesystem |
| Degree-day calculator | MUST for Sprint 1 | User decision |
| LangGraph version | 1.1.6 (latest stable) | Researched, confirmed on PyPI |
| Testing scope | Unit + integration (LangGraph included) | User decision |
| Project structure | Modular: `src/tools/`, `src/graph/`, `src/ui/` | User decision |
| LLM provider | Anthropic Claude | User decision |
| German language | MUST | User decision + interaction patterns |

---

## 6. Summary of Preliminary Plan Corrections

| Preliminary Plan Item | Finding | Action |
|----------------------|---------|--------|
| Companion app path `~/dsm-residential-energy/` | Wrong, actual: `~/dsm-residential-energy-apps/` | Correct in formal plan |
| 4-node pipeline architecture | Overly rigid, doesn't leverage LangGraph | Use ReAct pattern (`create_react_agent` or `StateGraph` + `ToolNode`) |
| Unit converter + degree-day as one tool | Two different tools; degree-day requires weather API | Split into unit_converter + degree_day_calculator |
| German language support as SHOULD | Core to the demo per user interactions doc | Elevate to MUST |
| "Ollama or OpenAI" as LLM | User chose Anthropic Claude | Use `langchain-anthropic` + `ChatAnthropic` |
| Standard lookup tool | No structured data source exists | Build static dictionary from knowledge base |
| "5+ pytest tests for deterministic tools" | Too narrow | Unit tests for tools + integration tests for LangGraph graph |

---

## 7. Proposed Project Structure

```
utility_conversational_ai/
├── _reference/                 # Preliminary plans (read-only reference)
├── dsm-docs/                   # DSM governance artifacts
├── src/
│   ├── __init__.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── heating_curve.py    # calculate_vorlauf, building presets
│   │   ├── standard_lookup.py  # standards dictionary, lookup function
│   │   ├── unit_converter.py   # kW<->kcal/h, kWh<->MJ, °C<->°F
│   │   └── degree_day.py       # HDD/CDD calculation, Open-Meteo API
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── agent.py            # LangGraph agent definition
│   │   └── state.py            # State schema
│   └── ui/
│       ├── __init__.py
│       └── app.py              # Streamlit chat interface
├── tests/
│   ├── unit/
│   │   ├── test_heating_curve.py
│   │   ├── test_standard_lookup.py
│   │   ├── test_unit_converter.py
│   │   └── test_degree_day.py
│   └── integration/
│       ├── test_graph.py
│       └── test_conversations.py
├── .env.example                # ANTHROPIC_API_KEY placeholder
├── requirements.txt
├── pyproject.toml
├── Dockerfile
└── README.md
```
