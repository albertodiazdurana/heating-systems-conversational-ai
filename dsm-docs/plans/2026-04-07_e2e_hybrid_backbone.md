# End-to-End Hybrid Backbone Plan (Sprints 1-3)

**Date:** 2026-04-07 (revised 2026-04-08)
**Status:** Draft (reference backbone for per-sprint plans)
**Supersedes:** `done/2026-04-07_e2e_haystack_backbone.md`
**Companion:** `2026-04-07_sprint1_langgraph_plan.md` (detailed Sprint 1)
**Decision:** `2026-04-07_orchestration-framework.md`
**Research basis:**
- `2026-04-07_langgraph-best-practices.md` (Sprint 1)
- `2026-04-07_hybrid-langgraph-haystack-best-practices.md` (Sprint 2)

This document is the **reference backbone** for the project. Per-sprint
plans trace back to this architecture and dependency contract. If a
per-sprint plan diverges, update this file first.

---

## 0. North Star

Bilingual (EN/DE) conversational AI for residential heating, combining:

- **Deterministic tools** (heating curve, standard lookup, unit conversion)
- **Grounded RAG** over the 6K-line `~/dsm-residential-heating-ds-guide/`
- **Evaluated quality** via MLflow + a hand-crafted test set

**Orchestration:** hybrid LangGraph (agent layer) + Haystack (RAG
subsystem behind a single tool boundary).

---

## 1. Architecture (target, end of Sprint 3)

```
              User (Streamlit chat)
                       |
                       v
              [LangGraph StateGraph + MessagesState]
                       |
            InMemorySaver (thread_id per session)
                       |
                       v
              create_react_agent
                       |
   +-------------------+--------------------+
   |                   |                    |
ChatOllama         tools (LangChain @tool)  system prompt
ChatOpenAI          |                       (bilingual + deflection)
                    |
   +----------------+-----------------+-----------------+
   |                |                 |                 |
unit_converter  standard_lookup  heating_curve      rag_search
(plain Python)                                      (LangChain tool
                                                     wrapping Haystack)
                                                          |
                                                          v
                                        [Haystack Pipeline]
                                        SentenceTransformersTextEmbedder
                                        ChromaEmbeddingRetriever
                                        returns docs + citations
```

**Key invariants:**
- LangGraph owns conversation state; Haystack pipelines are stateless per run
- Tools are plain Python, exposed as LangChain `@tool` functions
- LLM provider (`ChatOllama` | `ChatOpenAI`) selected by env
- **Integration boundary:** `rag_search` is the only place that imports
  Haystack. The agent layer has zero Haystack imports; the RAG subsystem
  has zero LangGraph imports.
- Evaluation reuses production pipeline, never a parallel implementation

---

## 2. Tech stack contract

| Concern | Choice | Locked at |
|---|---|---|
| Agent orchestration | LangGraph + `create_react_agent` | Sprint 1 |
| LLM (local) | `ChatOllama(model="qwen2.5:7b")` default, `OLLAMA_MODEL` env | Sprint 1 |
| LLM (cloud) | `ChatOpenAI(model="gpt-4o-mini")` via `LLM_PROVIDER=openai` | Sprint 1 |
| Tool definition | `@tool` decorator, snake_case, dict returns | Sprint 1 |
| Conversation memory | `InMemorySaver()` + `thread_id` per Streamlit session | Sprint 1 |
| UI | Streamlit | Sprint 1 |
| RAG framework | Haystack 2.x (inside `rag_search` tool boundary) | Sprint 2 |
| Vector store | ChromaDB via `chroma-haystack` (zero-ops local persistence for portfolio scope; one-component swap to Qdrant/Weaviate if scale demands) | Sprint 2 |
| Embeddings | `intfloat/multilingual-e5-base` via SentenceTransformers | Sprint 2 |
| Markdown chunking | LangChain `MarkdownHeaderTextSplitter` → convert to Haystack Documents | Sprint 2 |
| Eval | MLflow + hand-crafted test set | Sprint 3 |
| Tests | pytest | Sprint 1 |
| Packaging | uv + pyproject | Sprint 1 |
| Deploy | Docker (multi-stage) | Sprint 3 |

**Dependency growth (cumulative):**

| Sprint | Added |
|---|---|
| 1 | `langgraph`, `langchain`, `langchain-core`, `langchain-ollama`, `langchain-openai`, `streamlit`, `pydantic`, `python-dotenv`, `pytest`, `pytest-cov` |
| 2 | `haystack-ai`, `chroma-haystack`, `sentence-transformers`, `langchain-text-splitters` (for MarkdownHeaderTextSplitter) |
| 3 | `mlflow`, `tiktoken` (cost tracking) |

---

## 3. Sprint 1 — Conversation Engine + Deterministic Tools

**Goal:** End-to-end chat with tool-calling on LangGraph, no retrieval.
**Detail plan:** `2026-04-07_sprint1_langgraph_plan.md`

### MUST
- `create_react_agent` with 3 tools (`unit_converter`, `standard_lookup`, `heating_curve`)
- `InMemorySaver` + per-session `thread_id`
- Bilingual system prompt with canned out-of-scope deflection
- Streamlit chat UI (input, history, tool-call visibility)
- 5+ pytest tests on tools + graph construction smoke test
- `LLM_PROVIDER` env var switch (Ollama default)

### SHOULD
- Tool-call visibility in Streamlit (collapsible sections)
- Basic error handling when tools raise

### WON'T
- RAG, Haystack, conversation reset detection, MLflow

### Exit criteria
- `streamlit run app.py` produces working chat with tool-calling on Ollama
- `pytest` green
- Bilingual queries (EN/DE) work end-to-end
- Out-of-scope queries return the deflection message
- README has "run locally" section

---

## 4. Sprint 2 — Haystack RAG Subsystem + Contribution

**Goal:** Add grounded knowledge retrieval as one tool; validate and
document Haystack's Ollama tool-calling upstream.

### MUST
- **Empirical spike** (first action in sprint):
  `scratch/haystack_ollama_tools_spike.py` — minimal test of
  `OllamaChatGenerator(tools=[add_tool])`. Outcome documented in
  `dsm-docs/research/2026-MM-DD_haystack-ollama-tools-spike-result.md`
- **Embedding-model micro-benchmark (Gate 1, BL-002 edit 2):** before
  locking the ingestion pipeline on `intfloat/multilingual-e5-base`,
  index 5-10 representative EN/DE heating queries (terms like
  *Heizkennlinie*, *Vorlauftemperatur*, *hydraulischer Abgleich*,
  plus equivalent English phrasings) against 2-3 candidate multilingual
  models: `intfloat/multilingual-e5-base`, `BAAI/bge-m3`,
  `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`. Measure
  top-5 retrieval quality (hit@5 on the hand-picked expected source).
  Outcome documented in
  `dsm-docs/research/2026-MM-DD_embedding-model-benchmark.md`; the
  tech-stack contract (backbone §2) is updated if the winning model is
  not e5-base. One-afternoon of work; removes the biggest unquantified
  technical risk flagged by the 2026-04-14 groundedness assessment.
- **Ingestion pipeline** `src/rag/ingest.py` + `scripts/ingest.py`:
  - LangChain `MarkdownHeaderTextSplitter` (header-aware)
  - Convert to Haystack `Document` (one-line conversion)
  - `SentenceTransformersDocumentEmbedder` (multilingual-e5-base)
  - `DocumentWriter` → Chroma (persistent at `data/chroma/`)
  - Idempotent: doc id = hash(source path + chunk index)
- **Retrieval pipeline** `src/rag/retrieval.py`:
  - `SentenceTransformersTextEmbedder` → `ChromaEmbeddingRetriever`
  - Returns `List[Document]` with metadata: `source_doc`, `section_header`
- **`rag_search` tool** `src/tools/rag_search.py`:
  - LangChain `@tool` wrapping the Haystack retrieval pipeline
  - Returns `{"answer": str, "sources": [{"doc": str, "section": str}]}`
  - Lazy pipeline construction via `@lru_cache`
  - **Gate 1 decision (BL-002 edit 5): monolithic vs specialized RAG
    tools.** Panta 2026 precedent (`search_product_kb`, `search_support_kb`)
    argues for multiple topic-specialized `@tool` functions, each with a
    targeted docstring, so the LLM can route accurately. The same argument
    drove the Sprint 1 §5.1 choice of individual unit-converter tools.
    Rejecting it here while accepting it there is inconsistent. Decide at
    Sprint 2 Gate 1 between:
    - **(a) Monolithic:** one `rag_search(query: str)` — fewer tools to
      register; one docstring to tune; harder for the LLM to distinguish
      between standards lookup, system concepts, and MLOps questions.
    - **(b) Specialized:** e.g., `standards_lookup_rag` (DIN/VDI
      sections), `systems_reference_rag` (terminology, components),
      `mlops_reference_rag` (data-science + MLOps sections). Each with a
      docstring matched to the underlying corpus section. Coherent with
      Sprint 1 §5.1.
    - **(c) Hybrid:** one `rag_search` plus metadata filters exposed as
      parameters (requires corpus metadata to be rich enough; the current
      heading-aware chunking may or may not support this).
    The decision is deferred to Sprint 2 Gate 1 (not pre-decided here).
- **Citation rendering**: system prompt instructs model to include
  `[source: {doc} § {section}]` markers; Streamlit UI parses and shows
  a sources panel (optional polish)
- **Hybrid routing via tool descriptions**: the `rag_search` docstring
  clearly signals "use for knowledge questions"; deterministic tool
  docstrings signal "use for calculations". Agent picks correctly.
- 5+ retrieval quality tests (hand-picked Q → expected top-1 source)
- **Upstream contribution:** docs PR (or issue + fix) to
  `haystack-core-integrations` based on spike outcome

### SHOULD
- Tunable retrieval params via env (`RAG_TOP_K`, `RAG_SCORE_THRESHOLD`)
- Bilingual retrieval validation (DE query → EN section)

### WON'T
- **Reranking — deliberate scope choice (BL-002 edit 6), not an omission.**
  Two-stage retrieval (retrieve ~20, rerank to ~5) is the production-standard
  pattern per Panta 2026 precedent and Haystack ships
  `TransformersSimilarityRanker` / cross-encoder rerankers as drop-in pipeline
  components. Single-stage retrieval is sufficient for the portfolio scope;
  reranking is tracked as a Sprint 3 stretch (one-component pipeline addition)
  to revisit if retrieval quality metrics show clear precision gaps.
- Query rewriting (deferred to Sprint 3 stretch)
- Hybrid sparse+dense retrieval

### Exit criteria
- "What is DIN EN 12831?" → grounded answer with citation
- "Calculate heating curve for 1990s building" → still routes to deterministic tool
- Retrieval tests green
- Spike result document exists
- Upstream contribution PR opened or issue filed
- No LangGraph imports in `src/rag/`; no Haystack imports outside
  `src/rag/` and `src/tools/rag_search.py` (boundary enforcement)

### Architecture delta vs Sprint 1
- New: `src/rag/ingest.py`, `src/rag/retrieval.py`, `src/rag/chunking.py`,
  `src/tools/rag_search.py`, `scripts/ingest.py`, `data/chroma/`
- Tool registry adds `rag_search`
- `src/graph.py` only imports the new tool, not Haystack

---

## 5. Sprint 3 — Evaluation Framework + Production Polish

**Goal:** Quantified quality + reproducible demo.

### MUST
- **Evaluation dataset** `eval/test_conversations.yaml`: 20+ entries
  (`question`, `expected_answer_keywords`, `expected_source_doc`,
  `expected_source_section`, `language`, `expected_tool`)
- **Metrics:**
  - Retrieval: hit@k on `expected_source_doc`, MRR on section
  - Answer: keyword recall on `expected_answer_keywords`
  - Routing: confusion matrix (expected_tool vs actual tool used)
  - Conversation: avg turns to resolution, tool usage rate, out-of-scope rate
- **MLflow integration**: each run = `mlflow.start_run()` with params
  + metrics + per-question results table as artifact
- **Prompt engineering comparison:** 2+ system prompt variants evaluated
  head-to-head
- **README:** results table, architecture diagram, one-command setup
- **Docker:** multi-stage build, `docker compose` with app + (optional)
  Ollama sidecar

### SHOULD
- Automated eval CLI: `python -m eval.run --variant=v2 --top-k=5`
- Cost tracking per conversation (`tiktoken`, $/conversation)
- Streamlit polish: collapsible tool calls, source panel, conversation export

### COULD (stretch)
- Voice layer (Whisper STT + OpenAI TTS)
- A/B test across LLM providers on same eval set
- German-only eval subset
- Query rewriting / HyDE

### Exit criteria
- `python -m eval.run` produces MLflow run with all metrics
- README shows results table comparing 2+ prompt variants
- `docker compose up` runs the full demo

---

## 6. File layout (target, end of Sprint 3)

```
src/
  __init__.py
  config.py                    # env loading, ChatOllama/ChatOpenAI factory
  prompts.py                   # bilingual system prompt + deflection
  graph.py                     # build_agent() using create_react_agent
  tools/
    __init__.py
    registry.py                # re-exports all @tool functions
    unit_converter.py          # plain Python + @tool wrapper
    standard_lookup.py
    heating_curve.py
    rag_search.py              # added Sprint 2: wraps Haystack pipeline
  rag/                         # added Sprint 2
    __init__.py
    ingest.py                  # build_ingestion_pipeline() -> Pipeline
    retrieval.py               # build_retrieval_pipeline() -> Pipeline
    chunking.py                # MarkdownHeaderTextSplitter config + HS Document conversion
scripts/
  ingest.py                    # CLI entrypoint (Sprint 2)
eval/                          # added Sprint 3
  __init__.py
  test_conversations.yaml
  metrics.py
  run.py                       # CLI
scratch/                       # gitignored except docs
  haystack_ollama_tools_spike.py  # Sprint 2 spike
data/
  chroma/                      # gitignored persistent vector store
app.py                         # Streamlit UI
tests/
  test_unit_converter.py
  test_standard_lookup.py
  test_heating_curve.py
  test_graph.py                # smoke test for create_react_agent construction
  test_rag_search.py           # added Sprint 2
  test_retrieval.py            # added Sprint 2
  test_eval_metrics.py         # added Sprint 3
Dockerfile                     # added Sprint 3
docker-compose.yml             # added Sprint 3
pyproject.toml
.env.example
README.md
```

---

## 7. Cross-cutting concerns

### Configuration
- All runtime config via `.env` + `src/config.py`
- Factories: `config.get_chat_model()`, `config.get_document_store()`,
  `config.get_embedder()` (Sprint 2+)
- Eval and app use the same factories

### Bilingual handling
- Single system prompt with language-matching instruction
- Multilingual embeddings (e5) handle DE queries → EN docs
- No router node; prompt-level handling only
- Eval set tags each question with `language`

### Observability
- Sprint 1: Python logging at INFO, tool calls logged
- Sprint 3: MLflow tracking for eval; optional structured span logging
  if useful during debugging

### Testing strategy
- **Unit:** tools (plain Python, no LLM)
- **Smoke:** agent construction (no LLM invocation)
- **Integration:** retrieval quality (Sprint 2)
- **Eval:** the eval set IS the integration test for quality (Sprint 3)

### Integration boundary enforcement
The hybrid architecture relies on a clean boundary: Haystack imports only
appear inside `src/rag/` and `src/tools/rag_search.py`. Enforce in code
review; optionally add a test that asserts `src/graph.py` does not
import `haystack`.

---

## 8. Risk register

| Risk | Mitigation |
|---|---|
| LangChain ecosystem churn | Pin exact versions in `pyproject.toml`; smoke-test on upgrade |
| Haystack Agent API churn (we do not use it, but transitive deps may) | Pin haystack-ai when added in Sprint 2 |
| Pydantic version conflict between langchain-core and haystack-ai | Verify at Sprint 2 dependency addition; both use Pydantic v2 |
| Ollama model tool-call reliability on consumer hardware | Document min model in README; OpenAI fallback via env |
| Spike reveals Haystack OllamaChatGenerator tool-calling broken | Acceptable; hybrid still works (LangGraph agent unchanged); contribution becomes issue report |
| Markdown chunking quality with MarkdownHeaderTextSplitter on heating corpus | Validate in Sprint 2 retrieval tests; swap to custom splitter if insufficient |
| Boundary leakage (Haystack imports in agent layer) | Code review + optional import-assertion test |

---

## 9. Success criteria (project-level)

Showcase-ready when:
1. User can ask heating questions in EN or DE and get grounded, cited answers
2. Deterministic calculations return correct results
3. Evaluation framework produces quantified metrics on 2+ prompt variants
4. README explains architecture, shows results, provides one-command setup
5. **Bonus:** upstream contribution to Haystack docs (validates the
   experimental + take-ai-bite framing)

---

## 10. How to use this document

- **Before starting a sprint:** read the relevant section, then write
  per-sprint detail plan referencing it
- **When a per-sprint plan diverges:** update this backbone first
- **When `_reference/sprint-plan.md` conflicts:** this file wins (the
  original was LangGraph-only framed, this is hybrid-extended)
- **Pending cleanup:** `_reference/sprint-plan.md` should either be
  updated to reference this backbone or archived. Decision deferred to
  next wrap-up.