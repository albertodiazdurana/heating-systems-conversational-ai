# Hybrid LangGraph + Haystack Best Practices Research (Sprint 2)

**Date:** 2026-04-07
**Scope:** Medium depth (6 web fetches + 1 search)
**Purpose:** Inform Sprint 2 plan and validate hybrid architecture
**Related:** `2026-04-07_langgraph-best-practices.md`, `2026-04-07_orchestration-framework.md`

## 1. Headline finding: Haystack OllamaChatGenerator supports tools

### Claim
The decision record and deepened research flagged "Haystack Ollama
tool-calling is undocumented, risk material." This turned out to be **half
wrong**: the feature is implemented, it is only the marketing docs that
do not mention it.

### Evidence
Source code review of
`haystack-core-integrations/integrations/ollama/.../chat_generator.py`
confirms:

```python
class OllamaChatGenerator:
    def __init__(
        self,
        model: str = "qwen3:0.6b",
        ...
        tools: ToolsType | None = None,  # <-- present
        ...
    ):
```

The docstring states: "A list of `Tool` and/or `Toolset` objects, or a
single `Toolset` for which the model can prepare calls. Each tool should
have a unique name."

The response conversion logic handles tool calls:
```python
if ollama_tool_calls := ollama_message.get("tool_calls"):
    for ollama_tc in ollama_tool_calls:
        tool_calls.append(ToolCall(...))
```

### Implication
The "undocumented Ollama tool-calling" risk is downgraded from **material**
to **minor**:

- The feature exists and is wired to return `tool_calls`
- The gap is in the docs, not the code
- Sprint 2 spike is now a **validation spike** (does it work end-to-end?)
  rather than a **feasibility spike** (does it exist at all?)
- Contribution opportunity shifts from "issue + feature request" to "docs
  PR with working example"

### Decision impact
The hybrid architecture is still the right choice for this project (see
section 4 below), but the **upside scenario improves**: we can reasonably
expect the spike to succeed, and the project can confidently offer a docs
PR to `deepset-ai/haystack-core-integrations` in Sprint 2.

## 2. The hybrid pattern is published and recognized

### Finding
The LangGraph + Haystack hybrid is not a novel or weird combination. A
Packt Publishing book exists on exactly this architecture:
**"Building RAG and Agentic Applications with Haystack 2.0, RAGAS and
LangGraph 1.0"** (github.com/PacktPublishing).

### Evidence
- [PacktPublishing/Building-Natural-Language-and-LLM-Pipelines](https://github.com/PacktPublishing/Building-Natural-Language-and-LLM-Pipelines)
  — chapters cover hybrid RAG with reranking, combining Haystack 2.0 and
  LangGraph 1.0
- [MoritzLaurer/rag-demo](https://github.com/MoritzLaurer/rag-demo) —
  example notebooks using LangChain, LlamaIndex, OR Haystack with HF
  models (not quite hybrid, but shows the frameworks coexist fine)

### Implication
The decision to pursue a hybrid is validated as a known pattern. We
should **read the Packt book's hybrid chapter** (or check if the source
code is public) before the Sprint 2 spike to avoid reinventing patterns
that already have canonical solutions.

**Action:** before Sprint 2 starts, check whether the Packt repo has
Chapter X on LangGraph + Haystack integration as a reference.

## 3. No official Haystack ↔ LangChain adapter

### Finding
There is no first-class adapter in either `haystack-core-integrations`
or LangChain to wrap a Haystack pipeline as a LangChain tool. The
integration is DIY.

### Evidence
- `haystack-core-integrations/integrations/langchain` — does not exist
  (404)
- `haystack.deepset.ai/cookbook/langchain_integration` — does not exist
  (404)
- The Haystack main repo describes itself as "modular pipelines and
  agent workflows" without mentioning LangChain interop

### Pattern (DIY)
Wrapping is trivial. A Haystack pipeline exposes `.run()` returning a
dict; a LangChain `@tool` is a Python function returning a value. The
wrapper is one function:

```python
from functools import lru_cache
from langchain_core.tools import tool
from src.rag.retrieval import build_retrieval_pipeline  # Haystack

@lru_cache(maxsize=1)
def _get_pipeline():
    return build_retrieval_pipeline()

@tool
def rag_search(query: str) -> dict:
    """Search the heating domain knowledge base for grounded information.

    Use this for questions about German heating standards (DIN EN 12831,
    VDI 6030, GEG), heating system terminology, or any topic that requires
    citing the residential heating documentation.

    Args:
        query: Natural language question in English or German.

    Returns:
        Dict with keys: answer (str), sources (list of {doc, section}).
    """
    pipeline = _get_pipeline()
    result = pipeline.run({"text_embedder": {"text": query}})
    return {
        "answer": _format_context(result),
        "sources": _extract_citations(result),
    }
```

### Decision for this project
Adopt the DIY wrapper pattern. Boundary lives entirely in
`src/tools/rag_search.py`. The agent imports only the `rag_search`
function; the Haystack pipeline lives under `src/rag/` and is never
imported by `src/graph.py` or `src/tools/registry.py` directly.

## 4. Pydantic and dependency compatibility

### Finding (partial, needs Sprint 2 verification)
Both LangChain (`langchain-core>=0.3.0`) and Haystack (`haystack-ai>=2.8`)
use Pydantic v2. No known incompatibility as of 2026-04, but dual-framework
projects are rare enough that version drift could surface issues.

### Action
- Pin exact versions in `pyproject.toml` at Sprint 2 entry
- Run a smoke test after adding Haystack deps: import both, build a
  minimal graph + pipeline, invoke once with mocked LLM
- If incompatibility emerges, document and report upstream

## 5. Markdown chunking: Haystack is not markdown-optimized

### Finding
Haystack's `DocumentSplitter` splits by word/sentence/passage/page but is
**not header-aware** for markdown. `HierarchicalDocumentSplitter` creates
parent-child hierarchies but also does not parse markdown headers
specifically. The heating guide corpus (`~/dsm-residential-heating-ds-guide/`,
6 files, ~5800 lines) has a deep heading structure that header-aware
splitting would exploit.

### Comparison

| Splitter | Framework | Markdown-aware? | Notes |
|---|---|---|---|
| `DocumentSplitter` | Haystack | No | word/sentence/passage/page only |
| `HierarchicalDocumentSplitter` | Haystack | No, but hierarchical | Good for parent-child retrieval, needs custom parser |
| `RecursiveDocumentSplitter` | Haystack | No, but recursive | Similar to LangChain's recursive splitter |
| `MarkdownHeaderTextSplitter` | LangChain | **Yes** | Explicitly parses `#`, `##`, `###` |
| `RecursiveCharacterTextSplitter` | LangChain | Partial | Language-aware with `from_language("markdown")` |

### Decision for this project
**Use LangChain's `MarkdownHeaderTextSplitter` even inside the Haystack
RAG subsystem.** The splitter output is a list of LangChain `Document`
objects; convert to Haystack `Document` objects before passing to the
rest of the Haystack pipeline. This is a one-line conversion and
preserves header metadata.

Alternative: write a custom markdown-aware splitter as a Haystack
component. More work, more control. Defer unless `MarkdownHeaderTextSplitter`
proves insufficient.

**Note:** this is a **second integration boundary** (LangChain splitter
feeding Haystack pipeline) in addition to the agent-side boundary
(Haystack pipeline exposed as LangChain tool). Both are narrow and
well-contained.

## 6. Haystack contribution workflow

### Finding (actionable)

**Main Haystack repo (deepset-ai/haystack):**
- **Issue-first** for significant changes
- **Three test tiers:** unit (`hatch run test:unit`), integration
  (`hatch run test:integration`), end-to-end
- **Release notes** required via `hatch run release-note` for every PR
- **Documentation:** edit `docs-website/` folder, follow dedicated docs
  contributing guide, update `sidebars.js` for navigation

**haystack-core-integrations (where ollama-haystack lives):**
- **Fork → cd integrations/ollama → hatch run fmt → hatch run test:types
  → hatch run test:unit → PR**
- Monorepo pattern: work inside individual integration folders
- No explicit cookbook/example template mentioned
- API docs generated from docstrings (update docstrings when changing code)

### Decision for this project
**Sprint 2 spike workflow:**
1. Write a minimal standalone example using `OllamaChatGenerator(tools=[...])`
   with a trivial tool
2. If it works: write a cookbook/example for
   `haystack-core-integrations/integrations/ollama/examples/` (or
   equivalent), submit PR
3. If it works with caveats: PR includes caveats in the example
4. If it does not work: open an issue with repro, then decide whether to
   PR a fix or wait
5. Release notes via `hatch run release-note` for any code changes

## 7. Streaming and conversation memory for hybrid

### Finding
Memory ownership in a hybrid: the **LangGraph agent owns conversation
memory**; the Haystack pipeline is stateless per retrieval call. This
matches both frameworks' native models:

- LangGraph: `MessagesState` in the graph, checkpointed per thread_id
- Haystack: `Pipeline.run()` is idempotent, no state between calls

### Decision
The RAG subsystem receives a single query string and returns a single
result. It does not see conversation history. If the user asks a
follow-up ("tell me more about that"), the LangGraph agent is
responsible for reformulating the query before calling `rag_search`.

This is a **constraint on the system prompt**, not a technical barrier:
instruct the model to rewrite follow-ups into self-contained queries
before passing them to `rag_search`.

## 8. Citation rendering

### Finding
Citations flow: Haystack pipeline → `rag_search` tool → LangChain
ToolMessage → LangGraph state → system prompt → final response.

Each hop must preserve source metadata.

### Pattern
1. Haystack pipeline returns `List[Document]` with `meta` dict containing
   `source_doc`, `section_header`, `subsection`
2. `rag_search` tool returns `{"answer": "...", "sources": [{"doc": ...,
   "section": ...}, ...]}`
3. LangGraph agent's ToolMessage contains this dict
4. System prompt instructs the model to incorporate sources as
   `[source: {doc} § {section}]` markers in the final response
5. Streamlit UI optionally parses markers and renders a collapsible
   sources panel (Sprint 3 polish)

### Decision
Adopt this pattern. Metadata propagation is enforced by tool return
schema and system prompt instruction. Verify in Sprint 2 tests.

## 9. Revised Sprint 2 spike plan

Given the findings, the empirical spike is now specified as:

1. **Minimal example file:** `scratch/haystack_ollama_tools_spike.py`
   (outside `src/`, gitignored or committed separately)
2. **Content:** instantiate `OllamaChatGenerator(model="qwen2.5:7b",
   tools=[add_tool])`, send "what is 2+3?", assert response contains
   a tool call
3. **Timebox:** 1-2 hours. Expected outcome given source code review:
   works on first try or fails with a specific error that tells us
   what is missing
4. **Output:** a follow-up research note
   `2026-MM-DD_haystack-ollama-tools-spike-result.md` with verdict and
   next action (PR, issue, or caveat documentation)

## 10. Sources

- Haystack Agent docs: [docs.haystack.deepset.ai/docs/agent](https://docs.haystack.deepset.ai/docs/agent)
- Haystack contributing: [github.com/deepset-ai/haystack/blob/main/CONTRIBUTING.md](https://github.com/deepset-ai/haystack/blob/main/CONTRIBUTING.md)
- Haystack integrations contributing: [github.com/deepset-ai/haystack-core-integrations/blob/main/CONTRIBUTING.md](https://github.com/deepset-ai/haystack-core-integrations/blob/main/CONTRIBUTING.md)
- OllamaChatGenerator source (tools parameter confirmed): [github.com/deepset-ai/haystack-core-integrations/.../chat_generator.py](https://github.com/deepset-ai/haystack-core-integrations/blob/main/integrations/ollama/src/haystack_integrations/components/generators/ollama/chat/chat_generator.py)
- HierarchicalDocumentSplitter: [docs.haystack.deepset.ai/docs/hierarchicaldocumentsplitter](https://docs.haystack.deepset.ai/docs/hierarchicaldocumentsplitter)
- [Packt: Building RAG and Agentic Applications with Haystack 2.0, RAGAS and LangGraph 1.0](https://github.com/PacktPublishing/Building-Natural-Language-and-LLM-Pipelines)
- [MoritzLaurer/rag-demo](https://github.com/MoritzLaurer/rag-demo)
- [LangChain vs LlamaIndex vs Haystack: Production Lessons (dev.to)](https://dev.to/synsun/langchain-vs-llamaindex-vs-haystack-what-two-weeks-in-production-actually-taught-me-1kl6)

## 11. Revisions to the decision record

Based on these findings, the decision record
(`2026-04-07_orchestration-framework.md`) should be updated in two places:

1. **Section 3 / Driver #2** — downgrade "Ollama tool-calling
   undocumented, material risk" to "Ollama tool-calling documented in
   source but not in marketing pages, minor risk + contribution
   opportunity". The decision recommendation does not change.

2. **Section "Contribution goal"** — specify the contribution as "docs
   PR with working example" as the expected path, with "caveats PR" and
   "issue report" as fallbacks.

These are clarifications, not reversals. The hybrid recommendation still
stands and is reinforced by the Packt book's existence.

## 12. Open questions for Sprint 2 entry

- Does the Packt book's source repo contain a reference LangGraph +
  Haystack integration we should read before building ours?
- Does `haystack-experimental`'s `ChatMessageStore` offer anything we
  want, or is LangGraph's checkpointer sufficient (answer: sufficient)?
- What is the Haystack equivalent of `bind_tools` — is it just passing
  `tools=[...]` to the generator init, or is there a runtime binding
  mechanism?
- Pydantic v2 version pin that works for both `langchain-core` and
  `haystack-ai` — determine empirically at Sprint 2 dependency addition