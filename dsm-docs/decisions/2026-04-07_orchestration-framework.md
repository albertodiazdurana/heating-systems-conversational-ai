# Decision: Orchestration Framework — Hybrid (LangGraph + Haystack)

**Date:** 2026-04-07
**Status:** Proposed (awaiting approval)
**Scope:** This project only (Heating Systems Conversational AI)
**Supersedes:** Implicit Haystack-only choice from `2026-04-07_sprint1_haystack_plan.md` and `2026-04-07_e2e_haystack_backbone.md`

## Context

The project needs an orchestration layer for a bilingual conversational
agent with deterministic tools (Sprint 1), grounded RAG (Sprint 2), and
evaluation (Sprint 3). Default LLM provider is **Ollama** (offline dev);
OpenAI is the cloud fallback.

The project is **experimental**: discovery is a first-class goal alongside
delivery. It may scale to become a reference implementation in the
`take-ai-bite` framework, so loose coupling and reusable patterns matter
more than single-framework purity.

Initial preliminary research recommended Haystack. Sprint 1 was partially
bootstrapped on that choice (`pyproject.toml` swap, plan docs, scaffolding,
`unit_converter.py` tool). Deepened research
(`2026-04-07_haystack-vs-langgraph-deepened.md`) found:

- The preliminary compared Haystack to bare LangChain, not LangGraph
- The project is agent-first with RAG as one tool, not pure RAG
- Haystack `OllamaChatGenerator` tool-calling is undocumented (gap, but also
  contribution opportunity)
- Each framework has clear strengths in non-overlapping layers

## Decision

**Use a hybrid architecture: LangGraph as the agent layer, Haystack as the
RAG subsystem behind a single tool boundary.**

Sprint 1 introduces only LangGraph (no Haystack dependency yet). Sprint 2
introduces Haystack inside a `rag_search` LangChain tool. The agent does
not know Haystack exists; the RAG subsystem does not know LangGraph
exists. Either layer can be replaced without touching the other.

A secondary goal accompanies this decision: **document Haystack's
`OllamaChatGenerator` tool-calling status upstream**, regardless of empirical
outcome (working example, caveats, or issue report).

## Drivers (in order)

1. **Each framework where it is strongest.** LangGraph is the canonical
   choice for stateful multi-turn tool-calling agents. Haystack is the
   cleaner choice for stateless RAG ingestion and retrieval. A hybrid
   captures both.

2. **Experimental nature turns gaps into opportunities.** Haystack's
   Ollama tool-calling support is implemented in source
   (`OllamaChatGenerator(tools=...)`, confirmed in
   `haystack-core-integrations/.../chat_generator.py`) but not surfaced
   in marketing docs. The risk is minor, and the contribution becomes a
   **docs PR with working example** rather than a feature request. See
   `2026-04-07_hybrid-langgraph-haystack-best-practices.md` section 1.

3. **Loose coupling preserves optionality.** The integration boundary is a
   single function: `rag_search(query: str) -> dict`. If Haystack RAG turns
   out to be the wrong choice in Sprint 2, we replace one tool, not the
   whole project. Symmetrically, if LangGraph turns out to be the wrong
   agent layer, we replace the agent without touching the RAG subsystem.

4. **Take-ai-bite scaling.** A documented integration story between two
   leading LLM frameworks is a more reusable artifact than single-framework
   code. If this project becomes a reference implementation, the hybrid
   pattern is itself part of the reference.

5. **Sprint 1 risk is minimal.** The agent layer uses well-trodden
   `langchain-ollama` + `create_react_agent`. Haystack is introduced only
   in Sprint 2, by which time the agent works and we have empirical
   evidence about which framework to use for retrieval.

Portfolio signal is **explicitly removed** from drivers per user direction.

## Options considered

### Option A: Pure LangGraph

- **Pros:** mature, single dependency tree, well-trodden Ollama path
- **Cons:** verbose RAG ingestion in Sprint 2; weaker eval tooling without
  paid LangSmith; gives up Haystack's RAG ergonomics
- **Verdict:** safe but does not exploit Haystack's strengths; misses the
  experimental discovery goal

### Option B: Pure Haystack

- **Pros:** clean RAG, lighter dep tree, transparent pipelines, built-in eval
- **Cons:** Agent component still settling; Ollama tool-calling undocumented
  (decisive risk for default provider); stateless pipelines mismatch
  multi-turn agent needs; user has no prior experience
- **Verdict:** rejected; the agent-layer mismatch is the wrong cost to pay

### Option C: Hybrid LangGraph + Haystack (chosen)

- **Pros:** each framework where strongest; loose coupling; learns both
  frameworks; produces a reusable integration pattern; the documentation gap
  becomes a contribution
- **Cons:** heaviest dependency tree; doubled learning curve; one
  integration boundary to maintain; requires discipline to keep the boundary
  clean
- **Verdict:** selected. The cons are acceptable for an experimental project
  with discovery goals.

### Option D: Pure LangChain (no LangGraph)

- Rejected because stateful multi-turn is exactly what LangGraph was built to
  simplify over bare LangChain.

## Architectural sketch

```
User (Streamlit chat)
   |
   v
[LangGraph StateGraph + MessagesState]              <- Sprint 1
   |
   v
create_react_agent (or custom graph)
   |
   +-- ChatOllama / ChatOpenAI (configurable via LLM_PROVIDER)
   |
   +-- tools:
       - unit_converter        (plain Python)             <- Sprint 1
       - standard_lookup       (plain Python)             <- Sprint 1
       - heating_curve         (plain Python)             <- Sprint 1
       - rag_search            (LangChain @tool wrapping
                                a Haystack Pipeline)      <- Sprint 2
                                |
                                v
                        [Haystack Pipeline]
                        - SentenceTransformersTextEmbedder
                        - ChromaEmbeddingRetriever
                        - returns {answer, sources}
```

**Integration contract:** The `rag_search` tool exposes a single function
signature. Inside, it lazily constructs a Haystack `Pipeline` (cached) and
calls `.run()`. The LangGraph agent does not import Haystack; the Haystack
pipeline does not import LangGraph.

## Consequences

### Immediate (before resuming Sprint 1)

1. **Revert `pyproject.toml`:**
   - Remove `haystack-ai`, `ollama-haystack`
   - Restore `langgraph`, `langchain`, `langchain-core`, `langchain-ollama`,
     `langchain-openai`
   - Sprint 2 will add `haystack-ai`, `chroma-haystack`,
     `sentence-transformers` later
2. **Backbone plan:** rewrite `2026-04-07_e2e_haystack_backbone.md` as
   `2026-04-07_e2e_hybrid_backbone.md` reflecting the hybrid architecture.
   Mark the original as superseded.
3. **Sprint 1 detail plan:** archive `2026-04-07_sprint1_haystack_plan.md`
   with a superseded header; write `2026-04-07_sprint1_langgraph_plan.md`
   for the LangGraph-only Sprint 1.
4. **Keep as-is** (framework-agnostic): `src/__init__.py`,
   `src/tools/__init__.py`, `tests/__init__.py`, `src/tools/unit_converter.py`,
   `tests/test_unit_converter.py`.

### Sprint-level consequences

**Sprint 1 (LangGraph only):**
- `create_react_agent` (prebuilt) or custom `StateGraph` with `MessagesState`
- `ChatOllama` / `ChatOpenAI` from `langchain-ollama` / `langchain-openai`
- Tools wrapped as `@tool` decorators
- Memory via `MemorySaver` checkpointer or Streamlit `session_state`
- **No Haystack dependency yet**

**Sprint 2 (Haystack RAG subsystem added):**
- Add `haystack-ai`, `chroma-haystack`, `sentence-transformers` to deps
- New module `src/rag/` containing Haystack ingestion + retrieval pipelines
- New tool `src/tools/rag_search.py` wrapping the Haystack pipeline as a
  LangChain `@tool`
- Tool registered with the agent in `src/graph.py`
- **Empirical spike (early in Sprint 2):** test Haystack
  `OllamaChatGenerator(tools=[...])` to determine whether the agent layer
  could itself migrate to Haystack later. Outcome documented in a follow-up
  research note regardless of result.
- Upstream contribution: open issue or docs PR on
  `deepset-ai/haystack-core-integrations` based on spike findings

**Sprint 3 (eval):**
- MLflow integration unchanged
- Optional: try Haystack's eval components for retrieval metrics, LangChain's
  evaluators for agent metrics, compare ergonomics in a research note
- This is itself an experimental discovery output

### Risks introduced by this decision

| Risk | Mitigation |
|---|---|
| Doubled learning curve (two frameworks) | Accepted; discovery is a goal |
| Heaviest dependency tree | Pin versions; revisit at Sprint 2 boundary |
| Integration boundary may leak abstractions | Discipline: only the `rag_search` tool crosses the boundary; enforce in code review |
| Sprint 2 spike may show Haystack Ollama tool-calling fails | Acceptable; the hybrid still works (LangGraph stays as agent layer); contribution becomes an issue report instead of a docs PR |
| Two frameworks may have incompatible Pydantic / tokenizer versions | Lockfile + pinned versions; test on Sprint 2 entry |
| Take-ai-bite framework may impose conventions we do not yet know about | Re-validate at scaling time; the loose-coupling discipline minimizes rework |

### Risks avoided

- Building a multi-turn agent on Haystack's stateless pipeline model
- Committing the entire project to undocumented Ollama tool-calling
- Locking out one framework's strengths
- Delivery-vs-discovery false dichotomy

## Validation criteria

**Decision validated** if, at sprint exits:

- **Sprint 1 exit:** `streamlit run app.py` shows working LangGraph agent
  with three tools on Ollama; pytest green; bilingual queries handled.
- **Sprint 2 exit:** `rag_search` tool returns grounded answers with
  citations; integration boundary clean (no LangGraph imports in `src/rag/`,
  no Haystack imports outside `src/rag/` and `src/tools/rag_search.py`);
  empirical spike report on Haystack Ollama tool-calling exists.
- **Sprint 3 exit:** MLflow eval runs green; comparison note on
  Haystack vs LangChain eval ergonomics exists.

**Decision invalidated** if:

- Sprint 1: `langchain-ollama` tool-calling unreliable on chosen model AND
  OpenAI is unacceptable for offline dev
- Sprint 2: Haystack RAG ergonomics turn out worse than LangChain's for
  this corpus, OR the hybrid integration cost exceeds 2x the estimate
- In either case, reopen this decision with a new record citing the
  empirical findings

## Contribution goal (companion to this decision)

Given the source-code confirmation that `OllamaChatGenerator` already
accepts `tools`, the **expected path is a docs PR with a working
example**. Fallback paths remain if the spike reveals problems:

- **Expected:** docs PR to `deepset-ai/haystack-core-integrations` with
  a working `OllamaChatGenerator + tools` cookbook example, placed in
  `integrations/ollama/examples/` (or wherever the repo's examples
  conventionally live)
- **Fallback (works with caveats):** docs PR documenting the caveats +
  example
- **Fallback (does not work):** GitHub issue with reproduction case,
  then decide whether to contribute a fix

This artifact is itself a take-ai-bite-aligned output (human-AI
collaboration producing upstream value). Coordinate with `graph-explorer`
or other take-ai-bite tooling if a documentation contribution workflow
exists by Sprint 2.

## References

- `dsm-docs/research/haystack-vs-langchain-preliminary-research.md` — input
- `dsm-docs/research/2026-04-07_haystack-vs-langgraph-deepened.md` — validation
- `_reference/sprint-plan.md` — original LangGraph scope (still authoritative
  for sprint MUST/SHOULD/WON'T)
- `dsm-docs/plans/2026-04-07_sprint1_haystack_plan.md` — to be archived
- `dsm-docs/plans/2026-04-07_e2e_haystack_backbone.md` — to be rewritten as hybrid
- `~/dsm-graph-explorer/README.md` — take-ai-bite ecosystem reference