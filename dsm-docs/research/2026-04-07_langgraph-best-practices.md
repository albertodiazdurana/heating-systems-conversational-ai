# LangGraph Best Practices Research (Sprint 1)

**Date:** 2026-04-07
**Scope:** Medium depth (6 web fetches + 1 search)
**Purpose:** Inform Sprint 1 detail plan for heating conversational AI
**Related:** `2026-04-07_haystack-vs-langgraph-deepened.md`, `2026-04-07_orchestration-framework.md`

## 1. Agent pattern: create_react_agent vs custom StateGraph

### Finding
`create_react_agent` is the canonical prebuilt for a tool-calling chatbot
of this project's size. Custom `StateGraph` is only needed when the flow
has branching beyond the standard ReAct loop (e.g., explicit intent
classifier → router → responder).

### Evidence
- LangGraph prebuilt agents docs describe `create_react_agent` as taking
  an LLM and tools and "setting up the ReAct pattern automatically,
  handling the back-and-forth, tool calling, and result processing."
- 2026 tutorials (DataCamp, DigitalOcean, Oreate AI Blog) converge on
  `create_react_agent` as the default for tool-calling chatbots.
- LangGraph docs explicitly recommend the prebuilt "if you are just
  getting started with agents or want a higher-level abstraction."

### Pattern
```python
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver

model = ChatOllama(model="qwen2.5:latest")
checkpointer = InMemorySaver()
agent = create_react_agent(
    model=model,
    tools=[unit_converter, standard_lookup, heating_curve],
    checkpointer=checkpointer,
    prompt=system_prompt,
)
```

### Decision for this project
**Use `create_react_agent`.** The Sprint 1 scope (3 tools + out-of-scope
deflection) fits the ReAct pattern without needing a custom graph. If
Sprint 2 or 3 introduces branching that does not fit ReAct (e.g., a
multi-step eval loop), revisit then.

**Out-of-scope deflection:** handle via the system prompt, not a separate
graph node. The prompt instructs the model to respond with a canned
deflection message for non-heating queries. No router needed.

## 2. Tool definition: @tool decorator is canonical

### Finding
The `@tool` decorator with type hints and a docstring is the canonical
2026 pattern. `StructuredTool.from_function` exists but is only needed
for edge cases (dynamic tool registration, custom serialization).
Pydantic `args_schema` is the mechanism for complex input types.

### Evidence
- LangChain 2026 docs (docs.langchain.com/oss/python/langchain/tools)
  describe `@tool` as "the simplest way to create a tool"
- Recommendations: snake_case names, type hints required, docstring as
  LLM-facing description, return dicts for structured output

### Pattern
```python
from langchain_core.tools import tool

@tool
def heating_curve(
    outside_temp: float,
    slope: float,
    offset: float = 0.0,
) -> dict:
    """Calculate flow temperature for a heating curve.

    Args:
        outside_temp: Current outside temperature in °C.
        slope: Heating curve slope (Steigung), typically 0.4-1.8.
        offset: Parallel shift in °C, typically -5 to +5.

    Returns:
        Dict with keys: flow_temp (°C), inputs (echoed), formula (description).
    """
    ...
```

### Decision for this project
- All three Sprint 1 tools use `@tool` decorator
- Return dicts (not strings) so later tools (RAG) can return
  `{"answer": ..., "sources": [...]}` uniformly
- snake_case names matching the function name
- Docstrings written for the LLM (not the developer) — they are the
  tool's LLM-facing interface

## 3. Memory: InMemorySaver + thread_id per Streamlit session

### Finding
`InMemorySaver` is the canonical choice for Streamlit chat apps.
`SqliteSaver` persists across restarts; `PostgresSaver` is production-
scale. Per-session isolation is achieved via unique `thread_id` in the
invoke config.

### Evidence
- LangGraph persistence docs: "InMemorySaver is built-in, suitable for
  development/testing. Stores checkpoints in RAM."
- Thread ID is "a unique ID assigned to each checkpoint... used as the
  primary key for storing and retrieving checkpoints."
- Canonical pattern: one `thread_id` per user session; the checkpointer
  automatically loads prior state on each invoke.

### Pattern
```python
# app.py
import streamlit as st
from uuid import uuid4

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid4())

config = {"configurable": {"thread_id": st.session_state.thread_id}}
response = agent.invoke({"messages": [("user", user_input)]}, config=config)
```

### Decision for this project
- **Sprint 1:** `InMemorySaver` (ephemeral, per-session)
- **Sprint 3 stretch:** consider `SqliteSaver` for conversation export
  feature
- Thread ID stored in `st.session_state.thread_id`, generated with
  `uuid4()` on first load

## 4. Ollama model selection

### Finding
Two viable candidates for local tool-calling on consumer hardware:

| Model | Size | Notes |
|---|---|---|
| `qwen2.5:latest` | 7B | Widely used in 2026 tutorials; good tool-calling; ~4.7GB download |
| `qwen3:0.6b` | 0.6B | Default in Haystack's OllamaChatGenerator source; tiny, fast, lower tool-calling reliability |
| `llama3.1:8b` | 8B | Ollama's original tool-calling reference model (July 2024) |
| `gpt-oss:20b` | 20B | LangChain's current ChatOllama docs example; needs 16GB+ RAM |

### Evidence
- LangChain ChatOllama docs (2026) use `gpt-oss:20b` as the example
- Community tutorials (DataCamp, DigitalOcean, Medium) favor
  `qwen2.5:latest` for laptops
- Haystack's OllamaChatGenerator docstring defaults to `qwen3:0.6b`
  (small, fast, for testing)
- Ollama's official tool-support blog (July 2024) lists llama3.1,
  mistral-nemo, firefunction-v2, command-r-plus

### Decision for this project
- **Primary:** `qwen2.5:7b` (balance of quality and size, proven
  tool-calling, ~5GB)
- **Fallback (low RAM):** `qwen3:4b` or `llama3.1:8b`
- **Smoke test:** `qwen3:0.6b` (fast iteration during development)
- Make model configurable via `OLLAMA_MODEL` env var (already planned in
  `.env.example`)

## 5. Bilingual (EN/DE) handling

### Finding
Bilingual support is a **system prompt concern**, not a framework feature.
LangGraph/LangChain have no built-in language detection or routing. The
canonical pattern is a single system prompt that instructs the model to
match the user's language.

### Evidence
- No LangGraph docs page addresses multilingual agents specifically
- Multilingual capability depends entirely on the underlying model
  (qwen2.5, llama3.1, gpt-oss are all multilingual)
- Production pattern (from 2026 dev.to articles): single system prompt
  with explicit instruction to respond in the user's language

### Pattern
```python
SYSTEM_PROMPT = """You are a residential heating systems assistant.
You help users understand heating curves, German standards (DIN, VDI),
and perform unit conversions.

Respond in the user's language (English or German).
If the user writes in German, respond in German.
If the user writes in English, respond in English.

For questions unrelated to residential heating, politely decline:
"I can only help with residential heating topics. / Ich kann nur bei
Themen zu Heizungssystemen helfen."
"""
```

### Decision for this project
- Single bilingual system prompt with explicit language-matching
  instruction + canned deflection
- No separate router or classifier
- Validate with test queries in both languages at Sprint 1 exit

## 6. Testing patterns

### Finding
LangGraph testing is not well-documented yet. The community pattern is:

1. **Test tools as plain Python** (no framework involved)
2. **Smoke-test graph construction** (instantiate, don't invoke)
3. **Integration test with a real LLM** only for critical paths (optional
   in Sprint 1, expected in Sprint 3 eval)
4. **Mock the model** for node-level unit tests when needed

### Evidence
- LangGraph's unit-testing docs page does not currently exist (404)
- Community patterns from DataCamp tutorial: pytest on tool functions
  directly; smoke-test `create_react_agent` construction

### Decision for this project
- **Sprint 1 tests:**
  - Per-tool unit tests (plain Python, no LLM) — already started with
    `test_unit_converter.py`
  - One smoke test: `test_graph_builds()` that instantiates the agent
    without invoking
- **Sprint 3:** real LLM tests via the eval framework (see backbone plan)

## 7. Project layout

### Finding
No official canonical layout. Community convention:

```
src/
  __init__.py
  config.py          # env loading, model factory
  prompts.py         # system prompt(s)
  graph.py           # build_agent() returning create_react_agent result
  tools/
    __init__.py
    registry.py      # all @tool decorated functions or imports
    unit_converter.py
    standard_lookup.py
    heating_curve.py
app.py               # Streamlit UI
tests/
```

### Decision for this project
Adopt this layout. Matches the backbone plan's Sprint 1 section. No
`state.py` needed (MessagesState is imported from langgraph, not
subclassed for Sprint 1 scope).

## 8. Summary: Sprint 1 canonical stack

| Concern | Choice |
|---|---|
| Agent | `create_react_agent` (prebuilt) |
| Model (local) | `ChatOllama(model="qwen2.5:7b")` |
| Model (cloud) | `ChatOpenAI(model="gpt-4o-mini")` |
| Tools | `@tool` decorator, snake_case, dict return |
| Memory | `InMemorySaver()` + `thread_id` per Streamlit session |
| System prompt | Bilingual + canned deflection, no router |
| Tests | pytest on tools; smoke test on graph construction |

## 9. Open questions

- **Streaming:** Do we want token-level streaming in the Streamlit UI?
  LangChain docs confirm `ChatOllama` supports it, but integration with
  `create_react_agent` + Streamlit needs verification. Defer to Sprint 3
  polish.
- **Tool-call visibility in UI:** Streamlit pattern for showing "Agent
  is calling tool X" is DIY. Defer to Sprint 3.
- **Error handling:** What happens when a tool raises? Canonical
  `create_react_agent` behavior is to return the error to the model,
  which may retry or give up. Document observed behavior in Sprint 1 tests.

## 10. Sources

- LangChain tools: [docs.langchain.com/oss/python/langchain/tools](https://docs.langchain.com/oss/python/langchain/tools)
- LangGraph persistence: [docs.langchain.com/oss/python/langgraph/persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
- ChatOllama: [docs.langchain.com/oss/python/integrations/chat/ollama](https://docs.langchain.com/oss/python/integrations/chat/ollama)
- [Hands-On Guide to ReAct Agents Using LangGraph and Ollama (Medium)](https://medium.com/@diwakarkumar_18755/hands-on-guide-to-react-agents-using-langgraph-and-ollama-9e9897e9695c)
- [Building Local AI Agents (DigitalOcean)](https://www.digitalocean.com/community/tutorials/local-ai-agents-with-langgraph-and-ollama)
- [LangGraph Agents Tutorial (DataCamp)](https://www.datacamp.com/tutorial/langgraph-agents)
- [Integrating LangGraph with Ollama (Medium)](https://medium.com/@lifanov.a.v/integrating-langgraph-with-ollama-for-advanced-llm-applications-d6c10262dafa)
- Ollama tool-calling models: [ollama.com/search?c=tools](https://ollama.com/search?c=tools)