# Haystack + Ollama Tool-Calling Spike — Result

**Date:** 2026-04-21
**Session:** 9
**Status:** Done
**Target Outcome:** Sprint 2 Phase 1 — determine whether Haystack's tool-calling
API works with llama3.1:8b locally, to inform the RAG subsystem architecture.

---

## Outcome: A — Full tool-calling round-trip successful

All three test sections passed. The RAG subsystem can be wrapped as a
`@tool` (or Haystack `Tool`) behind the existing LangGraph agent boundary.

---

## Evidence

**Versions tested:** haystack-ai 2.28.0, ollama-haystack 6.3.0, llama3.1:8b (local Ollama)

**Script:** `scratch/haystack_ollama_tools_spike.py`

### Section 1: Basic connectivity
- `OllamaChatGenerator(model="llama3.1:8b", url="http://localhost:11434")` connected successfully.
- Single-turn response to "capital of Germany?" → "Berlin". Latency acceptable (~2s).

### Section 2: Tool-calling round-trip
Query: "It is -5°C outside. What flow temperature does my heating system need?"

- `create_tool_from_function(compute_flow_temperature)` generated a valid JSON schema
  with `outdoor_temp` (float) and `heating_curve_slope` (float, optional) parameters.
- Model issued exactly 1 tool call: `compute_flow_temperature(outdoor_temp=-5, heating_curve_slope=1.5)`.
- Tool returned `{"flow_temp": 77.5, "outdoor_temp": -5, "heating_curve_slope": 1.5}`.
- Model's final answer after result injection: coherent, cited the 77.5°C result correctly.

---

## Key findings

### 1. `create_tool_from_function` is the right entry point
Auto-generates JSON schema from Python function signature + docstring. No manual
schema definition needed. The function becomes the tool's implementation; Haystack
handles serialization to the Ollama API's tool format.

### 2. llama3.1:8b correctly triggers tool calls on domain queries
The model recognized that a temperature calculation query should use the registered
tool rather than answering from parametric knowledge. This is the critical behavior
needed for the `rag_search` tool in Phase 3: the agent must select the tool, not
paraphrase from training data.

### 3. Tool result injection via `ChatMessage.from_tool(tool_result=..., origin=tc)`
Haystack's `ChatMessage.from_tool` factory correctly structures the result message.
The model consumed it and produced a coherent final answer. Round-trip is complete.

### 4. Integration path with LangGraph confirmed viable
The Haystack tool can be wrapped as a LangChain `@tool` by:
```python
from langchain_core.tools import tool as lc_tool

@lc_tool
def rag_search(query: str) -> str:
    """Search the heating domain knowledge base."""
    # Haystack pipeline invocation here
    return result
```
The LangGraph agent calls this `@tool`; the `@tool` body runs Haystack internally.
The agent never needs to know Haystack exists. This matches the hybrid
LangGraph+Haystack architecture documented in
`dsm-docs/decisions/2026-04-07_orchestration-framework.md`.

### 5. Package import note
`ollama-haystack` installs under `haystack_integrations.components.generators.ollama`,
not as `ollama_haystack`. Use `importlib.metadata.version("ollama-haystack")` for
version lookup.

---

## Implications for Sprint 2 phases

| Phase | Implication |
|-------|-------------|
| Phase 2 (embeddings) | No change — embedding model selection is independent of tool-calling |
| Phase 3 (ingestion + `rag_search`) | Use `create_tool_from_function` for the `rag_search` Haystack tool; wire it as a LangChain `@tool` |
| Phase 3 (retrieval) | Use `OllamaChatGenerator` with a DocumentStore + Retriever pipeline; no separate generator needed (LangGraph agent handles conversation) |
| Phase 5 (upstream contribution) | Evidence base for filing a Haystack issue or discussion: tool-calling with Ollama works out of the box in v2.28.0 |

---

## Open questions (not blockers for Phase 2)

1. **Streaming with tool calls:** `streaming_callback` parameter exists on `OllamaChatGenerator`. Does it interleave correctly when a tool call is in flight? (Relevant for Streamlit UI in Phase 3+.)
2. **Multi-tool disambiguation:** With both `rag_search` and `compute_flow_temperature` registered, does llama3.1:8b correctly route between them? (Test in Phase 3 integration.)
3. **Error handling:** What does `OllamaChatGenerator` return if the tool call arguments are malformed? Needs a ToolException strategy at the `@tool` boundary (deferred to Sprint 3 per BL-002).

---

## Date Completed
2026-04-21