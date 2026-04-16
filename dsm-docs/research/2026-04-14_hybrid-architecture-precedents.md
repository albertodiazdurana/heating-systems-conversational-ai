# Hybrid Agent + RAG Architecture: Precedent Research

**Status:** Done
**Date:** 2026-04-14
**BL:** [BL-001](../plans/BL-001_hybrid-agent-rag-architecture-precedents.md)
**Related decision:** [2026-04-07 orchestration framework](../decisions/2026-04-07_orchestration-framework.md)

## Research question (restated)

Are there published precedents for hybrid LLM architectures using one framework as the agent layer and a different framework as the RAG subsystem, integrated through a single tool-call boundary? If so, what do their boundary contracts look like, and what tradeoffs do they report?

## TL;DR

The pattern is **published and documented but under-theorized**: ≥4 strict-lens precedents (including a Packt book, a 2026 enterprise-guide Medium article with full code, a multi-agent pattern post, and LlamaIndex's canonical `QueryEngineTool` primitive) show that "agent framework A + RAG framework B with one tool-call boundary" is an established tutorial-level pattern. The shared boundary contract is remarkably consistent: `RAG-framework.query_engine()` wrapped as a LangChain `@tool` and consumed by an agent framework's tool node.

However, the pattern has **no academic paper, no canonical vendor-blog reference architecture, and no named architectural label**. It is a de-facto convention propagated through tutorials. The orchestration decision (2026-04-07) chose a pattern that is conventional in tutorials but **not** conventional in vendor marketing or academic literature. This is worth noting in the decision record's validation section but does not warrant changing the decision.

## Precedent tally

| Lens | Required | Found |
|------|----------|-------|
| Strict (different vendors, different abstractions, one tool boundary) | ≥3 | **4 strong + 1 near-miss** |
| Lenient (any hybrid LLM-stack integration with loose-coupling rationale) | ≥5 | Saturated (common in tutorial content) |

**Outcome:** Strict lens satisfied → lenient lens not separately enumerated → **not novel-ish**. No addendum to orchestration decision record required. See "Implications" below for the lightweight update.

## Per-precedent capture

### Precedent 1: Funderburk, *Building RAG and Agentic Applications with Haystack 2.0, RAGAS and LangGraph 1.0* (Packt, 2025)

- **Source:** [PacktPublishing/Building-Natural-Language-and-LLM-Pipelines](https://github.com/PacktPublishing/Building-Natural-Language-and-LLM-Pipelines); author Laura Funderburk; Packt first edition
- **Stack:** Haystack 2.0 pipelines (RAG) + LangGraph 1.0 (agent) + RAGAS (evaluation)
- **Boundary contract:** Haystack pipelines deployed as REST endpoints via FastAPI/Hayhooks, then exposed as callable tools inside LangGraph supervisor-worker graphs. Quote: *"Serve pipelines as LangGraph-compatible microservices"* and *"Use LangGraph to orchestrate multi-agent workflows."*
- **State ownership:** Haystack pipelines are stateless per-call; LangGraph owns conversation/agent state.
- **Pros reported:** clean separation; each framework used where strongest; supervisor-worker composability.
- **Cons reported:** None explicit in the book's marketing copy; implied overhead from REST-boundary serialization vs in-process call.
- **Project type:** Pedagogical (book), with production-deployment chapters (7, 8, epilogue).
- **Closeness to our architecture:** HIGH on framework pair (LangGraph + Haystack); differs on boundary (REST microservice vs in-process `@tool`). Our decision favors in-process because we do not need horizontal scaling of the RAG subsystem in the portfolio-project scope.

### Precedent 2: Abhishek Panta, *End-to-End RAG Pipeline with LlamaIndex, LangGraph and LangChain: A Complete Enterprise Guide* (Medium, 2026-03-29)

- **Source:** [Medium article](https://medium.com/@abhipantdev8/end-to-end-rag-pipeline-with-llamaindex-a-complete-enterprise-guide-2eff0881aa0f)
- **Stack:** LlamaIndex (indexing/retrieval, vector + BM25 + reranker) + LangChain (tool abstraction, LLM binding) + LangGraph (state machine, checkpointing)
- **Boundary contract:** `index.as_query_engine()` (LlamaIndex) → decorated as `@tool` (LangChain) → consumed by `ToolNode` (LangGraph). Example:
  ```python
  @tool
  def search_product_kb(query: str) -> str:
      """Search the product knowledge base..."""
      product_query_engine = index.as_query_engine(...)
      response = product_query_engine.query(query)
      return f"{str(response)}\n\nSources: ..."

  tools = [search_product_kb, search_support_kb, calculate_roi]
  llm_with_tools = llm.bind_tools(tools)
  tool_node = ToolNode(tools=tools)
  ```
- **State ownership:** LlamaIndex query engines instantiated per-call (stateless); LangGraph owns conversation state via checkpointer.
- **Pros reported:** *"explicit state machine"* with *"full control over execution flow, checkpointing, and error handling"* versus *"implicit agent loops"*; streaming support; two-stage retrieval (retrieve ~20, rerank to ~5) standard in production.
- **Cons reported:** None explicit. Author frames the pattern as best-practice.
- **Project type:** Enterprise-guide tutorial; demo-grade code; production-framed narrative.
- **Closeness to our architecture:** **VERY HIGH on boundary shape** (identical `@tool` wrapping pattern, identical framing that "LangChain for tool abstraction, LangGraph for orchestration"). Differs on RAG framework (LlamaIndex vs our Haystack). The boundary contract transfers cleanly.

### Precedent 3: ScrapegraphAI, *Multi-Agent Systems: LangGraph, LlamaIndex & CrewAI*

- **Source:** [scrapegraphai.com/blog/multi-agent](https://scrapegraphai.com/blog/multi-agent)
- **Stack:** LangGraph (orchestration) + CrewAI (agent roles/tasks) + LlamaIndex (RAG)
- **Boundary contract:** CrewAI agents invoke LlamaIndex `query_engine.query(...)` inside node functions. Example:
  ```python
  def analyze_data(state):
      summary = query_engine.query(state["content"])
      insights = analyst.run(f"Analyze the summary: {summary}")
  ```
  Boundary here is a **function-call boundary**, not strictly a `@tool`-wrapped boundary: the LlamaIndex query is called directly inside the LangGraph node function rather than being exposed as a discoverable tool to an LLM. This is a weaker form of the pattern.
- **State ownership:** LangGraph owns orchestration state; CrewAI owns per-agent state; LlamaIndex is stateless.
- **Pros reported:** complementary roles, additive composition.
- **Cons reported:** None. The article is uncritical.
- **Project type:** Blog pattern post; pedagogical.
- **Closeness to our architecture:** MEDIUM. Three-framework stack is more complex than ours; the boundary is direct-function-call rather than LLM-discoverable tool, which is a different pattern. Useful as evidence the general family exists.

### Precedent 4: LlamaIndex `QueryEngineTool` (canonical primitive)

- **Source:** [LlamaIndex docs: Agent with Query Engine Tools](https://developers.llamaindex.ai/python/examples/agent/openai_agent_with_query_engine/) and [QueryEngineTool API](https://docs.llamaindex.ai/en/stable/api_reference/tools/query_engine/)
- **Stack:** LlamaIndex + any LLM-agent consumer
- **Boundary contract:** `QueryEngineTool(query_engine=..., metadata=ToolMetadata(name, description))`. Designed as a cross-framework primitive, though docs primarily show consumption by LlamaIndex's own agents.
- **State ownership:** Tool is stateless; caller owns state.
- **Pros reported:** *"the description is extremely important because it helps the LLM decide when to use that tool"* — docs explicitly call out tool-description quality as a first-class concern.
- **Cons reported:** None in docs; in practice, the LlamaIndex-native consumption is much more documented than cross-framework consumption, suggesting the pattern is supported but not idiomatic for LlamaIndex.
- **Project type:** Official framework documentation.
- **Closeness to our architecture:** MEDIUM. This is the primitive underneath Precedent 2; our architecture uses Haystack's equivalent (pipelines behind an `@tool`), so the abstraction parallel is the relevant part, not the specific API.

### Near-miss: Elastic Search Labs, *LangGraph, Llama3 & Elasticsearch: Build a local agent for RAG* (2024-09-02)

- **Source:** [elastic.co/search-labs/blog/local-rag-agent-elasticsearch-langgraph-llama3](https://www.elastic.co/search-labs/blog/local-rag-agent-elasticsearch-langgraph-llama3)
- **Stack:** LangGraph + Elasticsearch (as retriever) + Llama3 (local LLM)
- **Boundary contract:** Elasticsearch retriever is called **inside a graph node function** (`retrieve(state)`), not wrapped as a tool. Quote: *"Rather than having the agent make decisions at every step in the loop, we'll define a 'control flow' in advance."*
- **Why near-miss, not strict:** no tool-call boundary. Retrieval is a deterministic workflow step, not LLM-selected. This is the **alternative architectural pattern**: predefined control flow vs. agent tool-selection. Useful as a comparator in Sprint 2 design discussions.

## What the boundary contracts have in common

Across Precedents 1-4 (the strict ones), the boundary shape converges on:

1. **Calling convention:** single function call, `(query: str) -> str` (or structured return), stateless per invocation.
2. **State split:** agent framework owns conversation / thread / checkpoint state; RAG framework owns retrieval state (index, vector store, reranker); they share no in-memory structures.
3. **Discovery mechanism:** tool description (docstring or `ToolMetadata`) is how the LLM learns to call the RAG subsystem. Quality of the docstring is the primary tuning surface.
4. **Integration glue:** LangChain's `@tool` decorator is the de-facto lingua franca, even when neither side is LangChain-based (Haystack, LlamaIndex). This is because LangGraph's `ToolNode` consumes LangChain-shaped tools.

This matches our orchestration decision exactly. The only contract variable we need to choose is in-process (Precedent 2's `@tool` wrapping a function that instantiates the Haystack pipeline) vs out-of-process (Precedent 1's Hayhooks microservice). For the portfolio scope, in-process is the right call; out-of-process is a Sprint 3 deployment concern at most.

## Why the pattern is published but under-theorized

No arXiv paper, no deepset official blog, no LangChain official blog, and no named conference talk has canonized this pattern. Hypotheses:

1. **Framework marketing incentive.** Each framework markets itself as complete; Haystack's docs pitch Haystack for agents (and ship an `Agent` component), LangGraph's docs pitch LangGraph for retrieval (with Corrective/Adaptive RAG patterns), LlamaIndex ships its own agents. Cross-framework composition is anti-marketing for any single framework.
2. **Tutorial-level pattern, production-level silence.** Teams running this pattern in production (Grid Dynamics Temporal case, referenced in ZenML) tend to migrate toward workflow engines (Temporal) rather than publish "how we combined two LLM frameworks," because the framework combination is not the interesting part of the production story.
3. **Recency.** LangGraph reached 1.0 in 2025, Haystack 2.0 and LangGraph 1.0 are the frameworks that made the pattern clean. Earlier combinations were messier and not worth writing up. The Packt book appearing in 2025 is evidence the pattern is now stable enough to teach.
4. **MCP and agent SDKs reshaping the debate.** The *Why LLM Frameworks Are Being Replaced by Agent SDKs* (MindStudio, 2025) thread argues that MCP standardizes tool integration and makes heavyweight LLM frameworks less necessary. If this thesis holds, the "LangGraph + Haystack over @tool" pattern might be transitional, with MCP eventually replacing LangChain's `@tool` as the boundary standard.

These are hypotheses, not findings. They do mean we should not expect a canonical reference for the pattern; expect tutorials and books.

## Implications for our project

### For Sprint 2 scoping

- We can lean on Precedent 2 (Panta 2026) as a **structural template** for the `@tool`-wrapped Haystack pipeline. The code signature transfers directly, substituting `index.as_query_engine()` with a Haystack `Pipeline.run(...)` call.
- Precedent 1 (Funderburk/Packt) is the closest published match on framework pair. Consider purchasing the book if Sprint 2 scope grows to multi-agent supervisor patterns; for single-agent + RAG-tool, Precedent 2's simpler structure is sufficient.
- The near-miss (Elastic / direct-node retrieval) is worth flagging as the **alternative we rejected**: we chose agent-selected tool calls over deterministic control flow because conversational open-ended queries benefit from agent routing. This distinction belongs in Sprint 2 design notes.

### For upstream contribution

- **Not novel.** Do not pitch the pattern itself as a contribution. The `OllamaChatGenerator`-tools-docs PR opportunity (from the 2026-04-07 decision record) stands on its own merits.
- **Possibly contributable:** a worked example in Haystack's tutorials or deepset's blog of "Haystack pipeline as LangGraph tool" would be a useful contribution, because no official Haystack or LangGraph blog covers this and Precedent 1 (Packt book) is paywalled. This is a *documentation* contribution, not a *code* contribution.

### For the orchestration decision record

- Minimal update to the Validation criteria section noting: *"Pattern is established in tutorials (Funderburk 2025, Panta 2026) but lacks academic/official-blog canonization. No addendum needed; decision stands."*
- No full addendum is warranted because the research confirmed (not contradicted) the decision's premises.

## Search budget used

~90 minutes research time; 9 web searches; 4 deep fetches. Under the BL's 2-hour cap. Strict lens met threshold in Batch 2; lenient lens not separately enumerated.

## References (all external sources cited)

- [PacktPublishing/Building-Natural-Language-and-LLM-Pipelines](https://github.com/PacktPublishing/Building-Natural-Language-and-LLM-Pipelines) — Funderburk, Haystack 2.0 + LangGraph 1.0 + RAGAS
- [Abhishek Panta — End-to-End RAG Pipeline with LlamaIndex, LangGraph and LangChain](https://medium.com/@abhipantdev8/end-to-end-rag-pipeline-with-llamaindex-a-complete-enterprise-guide-2eff0881aa0f) — Medium, 2026-03-29
- [ScrapegraphAI — Multi-Agent Systems: LangGraph, LlamaIndex & CrewAI](https://scrapegraphai.com/blog/multi-agent)
- [LlamaIndex — Agent with Query Engine Tools](https://developers.llamaindex.ai/python/examples/agent/openai_agent_with_query_engine/)
- [LlamaIndex — QueryEngineTool API reference](https://docs.llamaindex.ai/en/stable/api_reference/tools/query_engine/)
- [Elastic Search Labs — LangGraph, Llama3 & Elasticsearch local RAG agent](https://www.elastic.co/search-labs/blog/local-rag-agent-elasticsearch-langgraph-llama3) (near-miss; direct-node pattern)
- [Leanware — LangGraph vs Haystack](https://www.leanware.co/insights/langgraph-vs-haystack-which-is-best-for-ai-development) (recommends combining; no code)
- [DigitalOcean — RAG with Haystack and LangChain](https://www.digitalocean.com/community/tutorials/production-ready-rag-pipelines-haystack-langchain) (comparison, not integration; disqualified)
- [ZenML — Best LLM Orchestration Frameworks](https://www.zenml.io/blog/best-llm-orchestration-frameworks) (treats frameworks as peers; ZenML wraps rather than bridges)
- [MindStudio — Why LLM Frameworks Are Being Replaced by Agent SDKs](https://www.mindstudio.ai/blog/llm-frameworks-replaced-by-agent-sdks) (counter-narrative; MCP thesis)
- [Haystack docs — Migrating from LangGraph/LangChain to Haystack](https://docs.haystack.deepset.ai/docs/migrating-from-langgraphlangchain-to-haystack) (evidence that deepset frames the two as competitors, not composable)
- [Temporal blog — Grid Dynamics prototype-to-prod](https://temporal.io/blog/prototype-to-prod-ready-agentic-ai-grid-dynamics) (production-scale workflow-engine alternative)
