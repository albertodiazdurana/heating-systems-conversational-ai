# Deepened Research: Haystack vs LangGraph for Heating Conversational AI

**Date:** 2026-04-07
**Status:** Complete (medium-depth validation)
**Inputs:** `haystack-vs-langchain-preliminary-research.md`
**Outputs:** Informs `dsm-docs/decisions/2026-04-07_orchestration-framework.md`
**Project framing:** Experimental, may scale to `take-ai-bite` framework

## 1. Why this research exists

The preliminary research recommended Haystack over LangChain for RAG strengths.
Before committing the project to a single framework, the claims need
validation against:

- The **actual project shape** (hybrid agent + RAG, not pure RAG)
- The **Ollama-default constraint** (offline dev, local tool-calling)
- The **experimental nature** of the project (discovery is a goal, not just delivery)
- **Current (2026-04) state** of both frameworks
- **Long-term scaling** to `take-ai-bite` (the project may become a reference
  implementation in that framework, not just a portfolio piece)

Portfolio signal is **explicitly removed** from the decision weights at the
user's direction (the user can showcase both frameworks independently).

## 2. What the preliminary got right

- Haystack's pipeline model is more transparent and easier to debug than
  LangChain's chain abstractions.
- Haystack is genuinely production-ready for RAG; evaluation is first-class.
- LangChain has more surface area and more incidental complexity.
- For **pure document retrieval** over large markdown, Haystack is the cleaner
  choice.

## 3. Where the preliminary needs refinement (for THIS project)

### 3.1 Haystack vs LangChain ≠ Haystack vs LangGraph

The original sprint plan specified **LangGraph**, not bare LangChain. LangGraph
is a low-level state-machine orchestration framework explicitly designed for
stateful multi-turn agents. LangChain's criticisms (over-abstraction, chain
hell) do not automatically transfer to LangGraph, which is closer in
philosophy to Haystack pipelines than to classic LangChain.

**Source:** LangGraph docs describe it as "a low-level orchestration framework
and runtime for building, managing, and deploying long-running, stateful
agents" with "production-ready deployment. Trusted by Klarna, Uber, J.P. Morgan."

The honest comparison is **LangGraph (agent layer) + LangChain (RAG layer)**
vs **Haystack (both layers)** vs **a hybrid of both**.

### 3.2 Project shape: agent-first with RAG as one tool

Sprint 1: conversation engine + 3 deterministic tools, **no RAG**.
Sprint 2: RAG added as **one tool among four** (`unit_converter`,
`standard_lookup`, `heating_curve`, `rag_search`).
Sprint 3: evaluation.

Haystack's RAG superiority dominates ~25% of total scope. The other 75% is
agent orchestration, where LangGraph is the canonical choice. This **opens
the door for a hybrid design** that uses each framework where it is strongest.

### 3.3 The Ollama tool-calling documentation gap

This is the central empirical finding.

**LangGraph + langchain-ollama:**
- Ollama tool-calling documented since July 2024
- Supported models published by Ollama: llama3.1, mistral-nemo, firefunction-v2,
  command-r-plus
- `ChatOllama(..., tools=[...])` is a standard documented pattern
- Works with LangGraph's `create_react_agent` prebuilt helper
- Battle-tested in production by named companies

**Haystack + ollama-haystack:**
- Haystack Agent docs (v2.27, current stable) show only `OpenAIChatGenerator`
  examples. Ollama is **not mentioned** in the Agent docs.
- The `haystack.deepset.ai/integrations/ollama` page describes
  `OllamaChatGenerator` but does **not** mention tool calling or a `tools`
  parameter.
- The `haystack-core-integrations` Ollama README does not surface
  tool-calling as a documented feature.

**Reframing per user direction:** Instead of treating the documentation gap
as a blocker, treat it as a **contribution opportunity**. Possible outcomes:

1. **Best case:** Haystack's `OllamaChatGenerator` already supports
   `tools=[...]` (the underlying Ollama API supports it since July 2024). A
   hands-on test in Sprint 1 verifies this, and the project contributes a
   docs PR + example to `deepset-ai/haystack-core-integrations`.
2. **Middle case:** Tool-calling works with caveats (specific models,
   parameter quirks). The contribution is a more nuanced docs PR.
3. **Worst case:** It does not work. The contribution is an issue report and
   a feature request, and the project uses LangGraph's `langchain-ollama`
   for tool-calling while keeping Haystack for RAG (the hybrid path).

All three outcomes produce value: working code or upstream signal.

### 3.4 Haystack Agent component is new, but stable enough to test

Stable since early 2025 (v2.25+), current as of v2.27 (April 2025). Recent
release notes show:

- **v2.25.2:** Reverted a breaking change (`messages` parameter optional)
- **v2.26.0:** Added Jinja2 system prompt templating
- **v2.27.0:** Further refinements

This is an API that is still settling but no longer experimental. For an
**experimental project**, "still settling" is acceptable risk and contributes
to the discovery goal.

### 3.5 State management: Haystack stateless vs LangGraph stateful

Multi-turn conversation memory is needed for the Streamlit chat.

**LangGraph:** `MessagesState` + `StateGraph` is the native model.
Conversation state is the graph's state. `create_react_agent` accepts a
checkpointer for persistent memory out of the box.

**Haystack:** Pipelines are stateless per `run()`. Conversation memory must
be externally managed and passed in as `messages` on each call. There is a
`ChatMessageStore` in `haystack-experimental` but not in stable Haystack.
For this project, memory could live in `st.session_state` and be passed to
the pipeline each turn, workable but means the framework does not help with
the memory problem, the app does.

This is a **structural mismatch for the agent layer** (LangGraph wins) but
**irrelevant for the RAG layer** (Haystack pipelines are stateless by design,
which is correct for retrieval). It reinforces the hybrid architecture
hypothesis: LangGraph for the stateful conversation, Haystack for stateless
retrieval.

## 4. Where Haystack still wins (and matters)

- **Sprint 2 RAG ingestion pipeline:** Haystack's `DocumentSplitter` +
  `SentenceTransformersDocumentEmbedder` + `DocumentWriter` + Chroma is more
  ergonomic than LangChain's equivalent.
- **Sprint 3 eval:** Haystack has first-class eval components; LangChain
  relies on LangSmith (commercial) or third-party libraries.
- **Debuggability:** Haystack pipeline graphs are more transparent than
  LangGraph's callback flow.
- **Markdown chunking:** Haystack's header-aware splitting is closer to
  what the heating-guide corpus needs.

In a hybrid design, these advantages are captured in the RAG subsystem
without paying the cost in the agent layer.

## 5. Multilingual / German performance

Both frameworks delegate embeddings and generation to the underlying model.
Neither has an intrinsic German advantage. The choice of embedding model
(`intfloat/multilingual-e5-base`) is framework-agnostic. The preliminary
research's implication of a Haystack multilingual edge does not survive
scrutiny.

## 6. Cost and complexity in a hybrid design

| Concern | Pure LangGraph | Pure Haystack | Hybrid |
|---|---|---|---|
| Dependencies | langgraph + langchain + langchain-{ollama,openai,chroma,huggingface} | haystack-ai + ollama-haystack + chroma-haystack + sentence-transformers | union of both, ~14 packages |
| Dep weight | Heavy | Light | Heaviest |
| Learning curve (this user) | Familiar from prior planning | New | Both |
| API churn risk | Low | Medium (Agent settling) | Medium (combined surface) |
| Debugging | LangGraph tracing | Haystack pipeline visualization | Two debug paths |
| Integration surface | None (one framework) | None (one framework) | One boundary: Haystack RAG pipeline wrapped as a LangChain `@tool` |

The hybrid design pays dependency weight and learning curve in exchange for
using each framework where it is strongest. For an **experimental project**
with discovery as a goal, this trade is favorable: the user learns both
frameworks and the project produces a non-trivial integration story.

## 7. Take-AI-Bite scaling considerations

If this project becomes a reference implementation in the `take-ai-bite`
framework:

- **Reusable orchestration patterns** matter more than single-framework purity
- **Loose coupling** between agent, tools, and RAG means future projects can
  swap any layer
- **Documented integration boundary** (LangGraph ↔ Haystack) becomes a
  reusable pattern, not a one-off hack
- **Contribution surface** to upstream LLM frameworks is itself a take-ai-bite
  artifact (showing how human-AI collaboration produces upstream value)

The hybrid design serves all four goals better than either pure option.

## 8. Revised claim matrix

| Preliminary claim | Verdict in this project's context |
|---|---|
| "Haystack is better for RAG over large markdown" | **True**, captured in hybrid via Haystack RAG subsystem |
| "Haystack has superior document preprocessing" | **True**, applies to Sprint 2 only |
| "LangChain is better for dynamic tool-driven workflows" | **True**, captured in hybrid via LangGraph agent |
| "Haystack scales better" | **Not validated**, both scale fine at this size |
| "Haystack has built-in evaluation" | **True**, marginal Sprint 3 edge |
| "LangChain has more abstraction complexity" | **Partially true** for bare LangChain, **mostly false** for LangGraph |
| Implicit: "Haystack is better for agents" | **False**, LangGraph wins |
| Implicit: "Pick one framework" | **Rejected**, hybrid is preferred for an experimental project |

## 9. Recommendation

**Hybrid: LangGraph (agent layer) + Haystack (RAG subsystem).** With explicit
contribution goal: validate Haystack `OllamaChatGenerator` tool-calling
empirically in Sprint 2 and contribute documentation upstream regardless of
outcome (working example, caveats, or issue report).

**Rationale summary:**

1. **Each framework used where it is strongest** (LangGraph stateful agents,
   Haystack stateless RAG pipelines)
2. **Experimental nature** turns the documentation gap into a contribution
   opportunity, not a blocker
3. **Loose coupling** (RAG subsystem behind a single tool boundary) preserves
   optionality if either framework needs to be swapped later
4. **Take-ai-bite scaling** is better served by a documented integration story
   than by single-framework purity
5. **Sprint 1 risk is minimal:** the agent layer uses the well-trodden
   LangGraph + langchain-ollama path; Haystack is introduced only in Sprint 2
   when the agent already works

## 10. Architectural sketch (hybrid)

```
User (Streamlit)
   |
   v
[LangGraph StateGraph]                     <- Sprint 1 (no Haystack yet)
   MessagesState (multi-turn memory)
   |
   v
create_react_agent
   |
   +-- ChatOllama / ChatOpenAI (configurable)
   |
   +-- tools:
       - unit_converter        (plain Python)
       - standard_lookup       (plain Python)
       - heating_curve         (plain Python, ported from heating-app)
       - rag_search            <- Sprint 2: Haystack RAG pipeline behind a
                                   LangChain @tool wrapper
                                |
                                v
                        [Haystack Pipeline]
                        - SentenceTransformersTextEmbedder
                        - ChromaEmbeddingRetriever
                        - returns (docs, citations)
```

**Integration boundary:** A single `rag_search(query: str) -> dict`
LangChain tool that internally invokes a Haystack `Pipeline.run()`. The
agent does not know Haystack exists; the RAG subsystem does not know
LangGraph exists. Either side can be replaced without touching the other.

## 11. Limitations of this research

- **No hands-on prototype.** Medium-depth scope did not include building
  minimal agents in both frameworks. Sprint 1 implementation will be the
  empirical validation.
- **Haystack `OllamaChatGenerator` tool-calling status is inferred from
  documentation absence**, not from running the code. Sprint 2 will verify.
- **Hybrid integration cost is estimated**, not measured. The wrapper tool
  is conceptually simple (one function call) but real costs may emerge.
- **Take-ai-bite scaling assumptions** rely on the framework not yet
  imposing constraints we do not know about.

## 12. Sources consulted

1. Haystack Agent docs: `docs.haystack.deepset.ai/docs/agent` (v2.27)
2. Haystack releases: `github.com/deepset-ai/haystack/releases` (v2.25.1-v2.27.0)
3. Haystack Ollama integration: `haystack.deepset.ai/integrations/ollama`
4. Haystack Ollama source: `github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/ollama`
5. LangGraph overview: `docs.langchain.com/oss/python/langgraph/overview`
6. Ollama tool-calling announcement: `ollama.com/blog/tool-support` (July 2024)
7. Preliminary research: `dsm-docs/research/haystack-vs-langchain-preliminary-research.md`
8. Take-ai-bite framework reference: `~/dsm-graph-explorer/README.md`

## 13. Open follow-ups

- **Empirical Ollama+Haystack test** in Sprint 2 (or earlier as a
  spike) before committing the RAG subsystem to Haystack
- **Contribution coordination:** if take-ai-bite has a doc-contribution
  workflow (graph-explorer or another tool), align the upstream Haystack
  contribution with it
- **Revisit decision** at Sprint 2 entry if Haystack Ollama tool-calling
  empirically fails and the hybrid integration cost is higher than estimated