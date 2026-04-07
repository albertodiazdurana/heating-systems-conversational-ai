**Superseded:** 2026-04-08, replaced by 2026-04-07_e2e_hybrid_backbone.md (hybrid decision)

# End-to-End Haystack Backbone Plan (Sprints 1-3)

**Date:** 2026-04-07
**Status:** Draft (preliminary, reference backbone for later per-sprint plans)
**Supersedes (conceptually):** `_reference/sprint-plan.md` LangGraph framing
**Companion:** `2026-04-07_sprint1_haystack_plan.md` (detailed Sprint 1)

This document is the **reference backbone** for the project. Per-sprint plans
written later must trace back to this architecture and dependency contract. If
a later plan diverges, update this file first.

---

## 0. North Star

Bilingual (EN/DE) conversational AI for residential heating, combining:

- **Deterministic tools** (heating curve, standard lookup, unit conversion)
- **Grounded RAG** over the 6K-line `~/dsm-residential-heating-ds-guide/`
- **Evaluated quality** via MLflow + a hand-crafted test set

Single orchestration framework end-to-end: **deepset Haystack 2.x**.

---

## 1. Architecture (target, end of Sprint 3)

```
                User (Streamlit chat)
                       |
                       v
              [ChatMessageStore]              <- per-session memory (st.session_state)
                       |
                       v
                  [Pipeline]
                       |
   +-------------------+--------------------+
   |                                        |
[ConditionalRouter]                   (telemetry: MLflow tracer)
   |
   +--(out-of-scope)--> [DeflectionGenerator] -----------+
   |                                                     |
   +--(in-scope)------> [Agent]                          |
                          |                              |
                          | tool_calls loop              |
                          v                              |
                  [ToolInvoker]                          |
                          |                              |
       +------------------+------------------+           |
       |          |           |              |           |
  unit_converter standard  heating_curve  rag_search    |
                 _lookup                     |           |
                                             v           |
                                  [Retriever pipeline]   |
                                  Chroma + multilingual  |
                                  -e5 embeddings         |
                                             |           |
                                             v           |
                                   [docs + citations]    |
                          |                              |
                          v                              v
                  [final ChatMessage] <-----------------+
                          |
                          v
              Streamlit renders + sources panel
```

**Key invariants across all sprints:**
- Stateless pipelines per `run()`; conversation memory passed in via `messages`
- Tools are plain Python, wrapped as Haystack `Tool` instances in a registry
- LLM provider (`OllamaChatGenerator` | `OpenAIChatGenerator`) selected by env
- All retrieval flows through one shared Chroma `DocumentStore` instance
- Evaluation reuses the production pipeline, never a parallel implementation

---

## 2. Tech stack contract

| Concern | Choice | Locked at |
|---|---|---|
| Orchestration | `haystack-ai>=2.8` | Sprint 1 |
| LLM (local) | Ollama via `ollama-haystack`, model TBD (llama3.1 / qwen2.5 — must support tool_calls) | Sprint 1 |
| LLM (cloud) | `OpenAIChatGenerator` (built into haystack-ai) | Sprint 1 |
| Vector store | ChromaDB via `chroma-haystack` | Sprint 2 |
| Embeddings | `intfloat/multilingual-e5-base` via `SentenceTransformersDocumentEmbedder` | Sprint 2 |
| Chunking | `DocumentSplitter` (header-aware split for markdown) | Sprint 2 |
| UI | Streamlit | Sprint 1 |
| Eval | MLflow + Haystack `eval` components | Sprint 3 |
| Tests | pytest | Sprint 1 |
| Packaging | uv + pyproject | Sprint 1 |
| Deploy | Docker (multi-stage, Ollama as sidecar or external) | Sprint 3 |

**Dependency growth (cumulative):**

| Sprint | Added |
|---|---|
| 1 | `haystack-ai`, `ollama-haystack`, `streamlit`, `pydantic`, `python-dotenv`, `pytest`, `pytest-cov` |
| 2 | `chroma-haystack`, `sentence-transformers`, `markdown-it-py` (chunking) |
| 3 | `mlflow`, `ragas` (optional, for retrieval metrics), `tiktoken` (cost tracking) |

---

## 3. Sprint 1 — Conversation Engine + Deterministic Tools

**Goal:** End-to-end chat with tool-calling, no retrieval.
**Detail plan:** `2026-04-07_sprint1_haystack_plan.md`

### MUST
- Haystack `Pipeline` with `ConditionalRouter` + `Agent` (ChatGenerator + ToolInvoker)
- Conversation memory via Streamlit `session_state` (passed as `messages` to pipeline)
- Tools: `unit_converter`, `standard_lookup`, `heating_curve` (ported from `~/dsm-residential-energy/`)
- Streamlit chat UI (input, history, tool-call visibility)
- 5+ pytest tests on tools
- LLM provider switch via `LLM_PROVIDER` env var (Ollama default)

### SHOULD
- Bilingual system prompt (EN/DE)
- Out-of-scope deflection via router (keyword heuristic v1)

### WON'T
- RAG, conversation reset detection, MLflow

### Exit criteria
- `streamlit run app.py` produces a working chat with tool-calling on Ollama
- `pytest` green
- README has "run locally" section

---

## 4. Sprint 2 — RAG Pipeline + Knowledge Retrieval

**Goal:** Add grounded knowledge retrieval over the heating guide.

### MUST
- **Ingestion pipeline** (offline script `scripts/ingest.py`):
  - `MarkdownToDocument` -> header-aware `DocumentSplitter` (split by `##`, overlap 1 sentence)
  - `SentenceTransformersDocumentEmbedder` (multilingual-e5-base)
  - `DocumentWriter` -> Chroma (persistent path under `data/chroma/`)
  - Idempotent: re-running replaces by document id (hash of source path + chunk index)
- **Retrieval pipeline**:
  - `SentenceTransformersTextEmbedder` -> `ChromaEmbeddingRetriever` (top_k configurable)
  - Returns docs with metadata: `source_doc`, `section_header`, `subsection`
- **`rag_search` tool**: wraps the retrieval pipeline, exposed to the Agent as a `Tool`
- **Citation rendering**: assistant response includes `[source: 01_Domain_Fundamentals.md § DIN EN 12831]` markers; Streamlit UI renders a sources panel
- 5+ retrieval-quality tests: hand-picked question -> expected top-1 source section
- Hybrid routing handled by the Agent itself: tool descriptions guide the LLM to pick `rag_search` for knowledge questions vs deterministic tools for calculations

### SHOULD
- Tunable retrieval params via env (`RAG_TOP_K`, `RAG_SCORE_THRESHOLD`)
- Bilingual retrieval validation: German query (e.g. "Heizkennlinie") retrieves correct English sections
- Chunk metadata enriched with parent section breadcrumb

### WON'T
- Re-ranking, query rewriting (deferred to Sprint 3 stretch)
- Multi-vector / hybrid sparse+dense

### Exit criteria
- Asking "What is DIN EN 12831?" returns a grounded answer with citation
- Asking "Calculate heating curve for a 1990s building" still routes to the deterministic tool
- Retrieval tests green

### Architecture delta vs Sprint 1
- New: `src/rag/ingest.py`, `src/rag/retrieval.py`, `scripts/ingest.py`, `data/chroma/`
- Tool registry adds `rag_search`
- `pipeline.py` unchanged structurally; only the tool list grows

---

## 5. Sprint 3 — Evaluation Framework + Production Polish

**Goal:** Quantified quality + reproducible demo.

### MUST
- **Evaluation dataset** `eval/test_conversations.yaml`: 20+ entries with `question`, `expected_answer_keywords`, `expected_source_doc`, `expected_source_section`, `language` (en|de), `expected_tool` (deterministic|rag|deflection)
- **Metrics**:
  - Retrieval: hit@k on `expected_source_doc`, MRR on section
  - Answer: keyword recall on `expected_answer_keywords` (cheap), optional LLM-as-judge for fluency
  - Routing: confusion matrix on `expected_tool` vs actual tool used
  - Conversation: avg turns to resolution, tool usage rate, out-of-scope rate
- **MLflow integration**:
  - Each eval run is an `mlflow.start_run()` with params (model, top_k, prompt variant) and metrics
  - Artifacts: per-question results table, confusion matrix plot
- **Prompt engineering comparison**: at least 2 system prompt variants evaluated head-to-head (e.g. concise vs structured-reasoning)
- **README**: results table, architecture diagram, one-command setup
- **Docker**: multi-stage build, `docker compose` with app + (optional) Ollama service

### SHOULD
- Automated eval CLI: `python -m eval.run --variant=v2 --top-k=5`
- Cost tracking per conversation (token usage via `tiktoken`, $/conversation)
- Streamlit polish: collapsible tool calls, source links, conversation export (JSON)

### COULD (stretch)
- Voice layer (Whisper STT + OpenAI TTS)
- A/B test across LLM providers on the same eval set
- German-only evaluation subset with separate report
- Query rewriting / HyDE in retrieval

### Exit criteria
- `python -m eval.run` produces an MLflow run with all metrics populated
- README shows a results table comparing at least 2 prompt variants
- `docker compose up` runs the full demo

---

## 6. File layout (target, end of Sprint 3)

```
src/
  __init__.py
  config.py                  # env loading, generator factory
  prompts.py                 # bilingual system prompt(s), deflection template
  pipeline.py                # build_pipeline() — router + agent, used by app + eval
  tools/
    __init__.py
    registry.py              # all Tool instances
    unit_converter.py
    standard_lookup.py
    heating_curve.py
    rag_search.py            # added Sprint 2 — wraps retrieval pipeline
  rag/
    __init__.py              # added Sprint 2
    ingest.py                # ingestion pipeline factory
    retrieval.py             # retrieval pipeline factory
    chunking.py              # header-aware splitter config
scripts/
  ingest.py                  # CLI entrypoint for ingestion (Sprint 2)
eval/
  __init__.py                # added Sprint 3
  test_conversations.yaml
  metrics.py
  run.py                     # CLI: builds pipeline, runs eval, logs to MLflow
data/
  chroma/                    # persistent vector store (gitignored)
app.py                       # Streamlit UI
tests/
  test_unit_converter.py
  test_standard_lookup.py
  test_heating_curve.py
  test_pipeline.py           # smoke: build pipeline, no LLM call
  test_retrieval.py          # added Sprint 2
  test_eval_metrics.py       # added Sprint 3
Dockerfile                   # added Sprint 3
docker-compose.yml           # added Sprint 3
pyproject.toml
.env.example
README.md
```

---

## 7. Cross-cutting concerns

### Configuration
- All runtime config via `.env` + `src/config.py`
- One source of truth: `config.get_chat_generator()`, `config.get_document_store()`, `config.get_embedder()`
- Eval scripts call the same factories — never instantiate components directly

### Bilingual handling
- System prompt instructs the model to respond in the user's language
- Embeddings are multilingual (e5) so DE queries hit EN docs naturally
- Eval set tags each question with `language` to compute per-language metrics

### Observability
- Sprint 1: Python logging at INFO, tool calls logged
- Sprint 3: MLflow tracking + optional Haystack `Tracer` for span-level inspection

### Testing strategy
- **Unit:** tools (pure Python, no LLM)
- **Smoke:** pipeline construction (no LLM call)
- **Integration:** retrieval quality (Sprint 2), end-to-end with mocked LLM (Sprint 3)
- **Eval:** the eval set IS the integration test for quality (Sprint 3)

---

## 8. Risk register (Haystack-specific additions)

| Risk | Mitigation |
|---|---|
| Haystack 2.x `Agent` API still evolving | Pin exact version in `pyproject.toml`; verify against docs at each sprint start |
| Ollama models with weak tool_calls support | Default to llama3.1 or qwen2.5; document min model in README; fall back to OpenAI in eval |
| `chroma-haystack` integration version drift vs `haystack-ai` | Pin both; smoke-test on dependency upgrade |
| Multilingual embedding quality on technical German | Validate in Sprint 2 with bilingual retrieval tests; swap to `e5-large` if needed |
| MLflow + Haystack integration is custom (no first-class connector) | Wrap eval runs manually; treat MLflow purely as a tracking sink, not a Haystack component |

---

## 9. Success criteria (project-level, unchanged)

The project is showcase-ready when:
1. A user can ask heating domain questions in EN or DE and get grounded, cited answers
2. Deterministic calculations return correct results
3. The evaluation framework produces quantified metrics on at least 2 prompt variants
4. The README explains the architecture, shows results, and provides one-command setup

---

## 10. How to use this document

- **Before starting a sprint:** read the relevant section here, then write the per-sprint detail plan referencing it
- **When a per-sprint plan diverges:** update this backbone first, then the per-sprint plan
- **When `_reference/sprint-plan.md` conflicts with this file:** this file wins (the original was LangGraph-framed and is now superseded)

Suggested follow-up: replace `_reference/sprint-plan.md` with a pointer to this backbone, or archive it. Decision deferred to next wrap-up.