# Sprint Plans Groundedness Assessment

**Status:** Done
**Date:** 2026-04-14
**Author:** albertodiazdurana (with Claude, parallel session 4.1)
**Scope extension:** Follow-on to BL-001 (precedent research); same parallel session. Main session to formalize scope in the BL.
**Plans assessed:**
- [dsm-docs/plans/2026-04-07_e2e_hybrid_backbone.md](../plans/2026-04-07_e2e_hybrid_backbone.md)
- [dsm-docs/plans/2026-04-07_sprint1_langgraph_plan.md](../plans/2026-04-07_sprint1_langgraph_plan.md)

**Research cross-referenced:**
- [2026-04-07_langgraph-best-practices.md](2026-04-07_langgraph-best-practices.md) (Sprint 1 basis)
- [2026-04-07_hybrid-langgraph-haystack-best-practices.md](2026-04-07_hybrid-langgraph-haystack-best-practices.md) (Sprint 2 basis)
- [2026-04-07_haystack-vs-langgraph-deepened.md](2026-04-07_haystack-vs-langgraph-deepened.md) (decision driver)
- [2026-04-14_hybrid-architecture-precedents.md](2026-04-14_hybrid-architecture-precedents.md) (new precedent research)

## Question

Are the Sprint 1 and hybrid-backbone plans grounded in the cited research, or do they make claims the research does not back? If gaps exist, are they material enough to require plan revisions before resuming implementation?

## Headline verdict

**Plans are well-grounded at the architecture level and require no structural changes.** Four specific claims rest on thin or implicit evidence (model choice, embedding model, vector store, error handling). Two design choices are worth revisiting at Sprint 2 start in light of the new precedent research (RAG tool granularity, reranker deferral). None is blocking.

## Claim-to-evidence mapping

### Strong grounding (research directly supports plan)

| Plan claim | Research source | Grounding |
|---|---|---|
| `create_react_agent` as prebuilt for Sprint 1 | langgraph-best-practices §1 | Official LangGraph docs quote + 3 tutorials |
| `@tool` decorator as canonical tool definition | langgraph-best-practices §2 | Official LangChain docs quote |
| `InMemorySaver` + `thread_id` per Streamlit session | langgraph-best-practices §3 | Official LangGraph persistence docs |
| Bilingual single system prompt, no router | langgraph-best-practices §5 | Pattern from dev.to articles + model capability (qwen2.5 is multilingual) |
| Tools return dicts (not strings) | langgraph-best-practices §2 decision | Consistency argument for later RAG tool return shape |
| Haystack `OllamaChatGenerator` supports tools | hybrid-best-practices §1 | Source-code quote from haystack-core-integrations |
| `rag_search` DIY wrapper (in-process `@lru_cache`) | hybrid-best-practices §3 + precedents §Precedent 2 | Absence of official adapter + near-isomorphic code in Panta (Mar 2026) Medium enterprise guide |
| No LangChain-Haystack official adapter | hybrid-best-practices §3 | 404 on expected adapter paths |
| LangChain `MarkdownHeaderTextSplitter` inside Haystack pipeline | hybrid-best-practices §5 | Explicit comparison table of 5 splitters (Haystack has no header-aware option) |
| State split (LangGraph owns conversation, Haystack stateless) | hybrid-best-practices §7 + precedents | Confirmed across all 4 strict-lens precedents |
| Citation metadata flow (pipeline → tool → ToolMessage → prompt → response) | hybrid-best-practices §8 | Framework capability chain, no unsupported step |
| Haystack contribution workflow (hatch, release-note, monorepo) | hybrid-best-practices §6 | Cites CONTRIBUTING.md directly |
| Hybrid architecture is not novel | precedents §TL;DR | 4 strict-lens precedents + 1 near-miss |

### Thin or implicit evidence

#### 1. `qwen2.5:7b` as primary local model

- **Claim location:** backbone §2 stack table; Sprint 1 plan §2 canonical stack; research §4 decision
- **Evidence level:** community-tutorial ranking (DataCamp, DigitalOcean, Medium). No benchmark for EN/DE tool-calling on heating queries. Research even notes Haystack's own default is `qwen3:0.6b`.
- **Risk:** if `qwen2.5:7b` tool-calls unreliably in German, Sprint 1 exit fails for the DE path. Single thinnest evidence point in the whole plan.
- **Mitigation in place:** `LLM_PROVIDER=openai` fallback is already a MUST in Sprint 1.
- **Recommended plan edit:** promote the German tool-call query in Sprint 1 plan §4 step 11 ("Berechne die Vorlauftemperatur bei -10°C mit Steigung 1.2") from informal smoke test to a **gating exit criterion** in §6. If DE tool-calling on qwen2.5:7b proves unreliable, the fix is documented (switch LLM_PROVIDER), not a decision reversal.

#### 2. Embedding model `intfloat/multilingual-e5-base`

- **Claim location:** backbone §2 stack table
- **Evidence level:** mentioned once in deepened research §5 with the framing that embedding choice is "framework-agnostic." The specific choice vs `paraphrase-multilingual-mpnet-base-v2`, `BAAI/bge-m3`, `jina-embeddings-v3`, or OpenAI `text-embedding-3-large` is not justified. The choice is inherited from the preliminary Haystack-first direction and was not re-validated after the hybrid pivot.
- **Risk:** medium. e5-base is a reasonable default but may underperform on German technical vocabulary (Heizkennlinie, Vorlauftemperatur, hydraulischer Abgleich) vs newer or larger multilingual models.
- **Recommended plan edit:** Sprint 2 plan should include a Gate-1 validation: index 5-10 representative EN/DE heating queries, measure top-5 retrieval quality on 2-3 candidate embedding models (e5-base, bge-m3, paraphrase-multilingual-mpnet-base-v2) before locking the pipeline. One afternoon of work, possibly removes the biggest unquantified technical risk.

#### 3. ChromaDB as vector store

- **Claim location:** backbone §2 stack table (`chroma-haystack`)
- **Evidence level:** named in research sketches but never compared against Qdrant, Weaviate, Milvus, or Pinecone. Implicit inheritance from Haystack-first direction.
- **Risk:** low. Chroma is defensible for portfolio scope (local, persistent, zero-ops). The lack of justification matters only for record-keeping, not for runtime risk.
- **Recommended plan edit:** one-sentence rationale in backbone §2 ("Chroma chosen for zero-ops local persistence; migration to Qdrant / Weaviate is one-component swap in the Haystack pipeline if scale demands"). No empirical work required.

#### 4. Error handling assumption

- **Claim location:** Sprint 1 plan §5.4: "Let `create_react_agent` handle tool errors natively (returns error to model, which may retry or respond with an explanation)."
- **Evidence level:** research §9 explicitly flags this as an **open question**: "Canonical `create_react_agent` behavior is to return the error to the model, which may retry or give up. Document observed behavior in Sprint 1 tests."
- **Risk:** low. This is a correctness concern during implementation, not an architectural risk. Worst case: Sprint 1 tests surface unexpected behavior and the plan gets a small rewrite.
- **Recommended plan edit:** Sprint 1 plan §5.4 should mark this as assumed-pending-verification and add one test (`test_tool_error_handling`) that raises from a test tool and asserts the agent recovers gracefully. Already covered implicitly by §9 open question but the Sprint 1 tests section should make it explicit.

### Design choices worth revisiting at Sprint 2 start (surfaced by new precedent research)

#### 5. One generic `rag_search` vs multiple topic-specialized RAG tools

- **Current plan:** backbone §3 and §4 define a single `rag_search` tool.
- **Precedent:** Panta (Mar 2026 Medium article, Precedent 2 in 2026-04-14 precedent research) defines **multiple specialized `@tool` functions**: `search_product_kb`, `search_support_kb`. Rationale: each tool has a focused docstring the LLM can route on accurately.
- **Coherence check:** this is the same argument Sprint 1 plan §5.1 uses to choose **individual** unit-converter tools over a combined tool with a method parameter. Rejecting the argument for RAG while accepting it for unit conversion is inconsistent.
- **Recommended plan edit:** Sprint 2 Gate 1 should include a deliberate choice between:
  - **(a) Monolithic:** single `rag_search(query: str)` — fewer tools to register, one docstring to tune, harder for the LLM to distinguish use cases
  - **(b) Specialized:** e.g., `standards_lookup_rag` (DIN/VDI sections), `systems_reference_rag` (terminology, components), `mlops_reference_rag` (data-science and MLOps sections) — each with a targeted docstring matching the underlying corpus section
  - **(c) Hybrid:** one `rag_search` plus metadata filters exposed as parameters (requires corpus metadata to be rich enough; the current heading-aware chunking may or may not support this)
- **Stakes:** medium. Affects Sprint 2 implementation shape and tool-routing quality. Does not affect Sprint 1 or the architecture decision.

#### 6. Reranker deferred to Sprint 3 stretch

- **Current plan:** backbone §4 WON'T list and Sprint 2 plan §1 WON'T list exclude re-ranking; Sprint 3 §COULD lists HyDE / query rewriting. Reranking is implicitly deferred.
- **Precedent:** Panta quote: "two-stage retrieval (retrieve ~20, rerank to ~5) is standard in production RAG." Haystack ships rerankers (`TransformersSimilarityRanker`, cross-encoders) as drop-in pipeline components.
- **Coherence check:** deferral is defensible for portfolio scope (single-stage retrieval is enough to demo grounded Q&A) but it is not explicit in the plan whether this is a scope choice or an oversight. Panta-style two-stage retrieval is arguably one pipeline-step addition.
- **Recommended plan edit:** backbone §4 and Sprint 2 plan §1 WON'T should explicitly read "reranking (deliberate scope choice, one-component addition tracked as Sprint 3 stretch)" rather than silent omission. Low-effort plan hygiene.

### Not-risks (research already protects against these)

- **Hybrid architecture novelty:** 4 strict-lens precedents in 2026-04-14 research.
- **Markdown chunking quality:** backbone §8 risk register has a concrete swap-to-custom-splitter mitigation.
- **Pydantic v2 compat:** hybrid-best-practices §4 explicitly flags for empirical verification at Sprint 2 dependency addition.
- **`OllamaChatGenerator(tools=)` feasibility:** source-code confirmed in hybrid-best-practices §1. The Sprint 2 spike is validation, not feasibility.
- **Boundary leakage (Haystack imports in agent layer):** backbone §7 enforces it in code review and §8 suggests an import-assertion test.
- **Upstream contribution workflow:** hybrid-best-practices §6 covers hatch tooling, release notes, monorepo pattern.

## Recommended plan edits (summary)

| # | File | Section | Edit type | Effort |
|---|---|---|---|---|
| 1 | Sprint 1 plan | §6 exit criteria | Promote DE tool-call smoke to gating criterion | 1 line |
| 2 | Sprint 2 plan + backbone | Sprint 2 §MUST | Add Gate-1 embedding-model validation micro-benchmark | 1 paragraph + 1 afternoon of implementation |
| 3 | Backbone | §2 stack table | Add one-sentence Chroma rationale | 1 line |
| 4 | Sprint 1 plan | §5.4 + test list | Mark error-handling as assumed-pending-verification; add one test | 2 lines + 1 test |
| 5 | Sprint 2 plan | §1 Gate 1 | Add deliberate monolithic-vs-specialized RAG tool choice | 1 paragraph |
| 6 | Backbone + Sprint 2 plan | WON'T lists | Make reranker deferral explicit (deliberate, not omission) | 1 line each |

Edits 1, 3, 4, 6 are plan-hygiene lines. Edits 2 and 5 are substantive: one adds a micro-benchmark task to Sprint 2, the other adds a design-gate decision to Sprint 2.

## Decision-record impact

**None.** The 2026-04-07 orchestration-framework decision is solidly backed, and the one-paragraph precedent-research note added 2026-04-14 is sufficient. The gaps identified here are in the **per-sprint plans**, not in the decision the plans implement.

## Confidence statement

High confidence on the strong-grounding table: every entry traces to an explicit research paragraph.

Medium confidence on the thin-evidence items: they are thin because the research is thin on them, not because the plan over-claims. Calling them "thin" is a call for validation, not a disagreement.

Medium confidence on the design-choice items: Panta precedent is a single published source; a rigorous recommendation would need 2-3 independent implementations of specialized-RAG-tool patterns. Current research is sufficient to **raise the question at Sprint 2 Gate 1**, not to pre-decide the answer.

## Search / reading budget

~30 minutes: two plan reads, three research-file reads, cross-referencing. No new web fetches (all precedents already captured in 2026-04-14 precedent research).
