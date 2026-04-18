# Sprint 2: Haystack RAG Subsystem + Upstream Contribution

**Duration:** 3-5 sessions (estimate; revisit after Phase 1 spike)
**Goal:** Add grounded knowledge retrieval to the agent as one tool (`rag_search`), validated end-to-end on the 6-document heating guide corpus, with a capability-experiment-driven upstream contribution to Haystack.
**Prerequisites:**
- Sprint 1 closed 7/7 (BL-003 closed 2026-04-18, Session 6). Streamlit boots on Python 3.12.13, all 55 tests green, 5/5 smoke PASS.
- `2026-04-07_e2e_hybrid_backbone.md` §4 is the architectural reference for Sprint 2.
- Knowledge base read-only at `/home/berto/_projects/dsm-residential-heating-ds-guide/` (~5,800 lines, 6 thematic MD files + TOC).
- GE contribution playbook received (`_inbox/done/2026-04-13_dsm-graph-explorer_contribution-playbook.md`): issue-first, PR-conditional, capability-experiment-as-evidence.

---

## Research Assessment (before detailing deliverables)

Three unknowns prevent a speculative-free task breakdown; each is addressed by an early phase rather than pre-decided here:

| Unknown | Addressed by | Risk if skipped |
|---|---|---|
| Does Haystack's `OllamaChatGenerator` actually support `tools=[...]` in practice? | Phase 1 spike (capability experiment) | Could invalidate the hybrid architecture's RAG-behind-a-LangChain-tool pattern; we hedge by wrapping the Haystack *retrieval* pipeline in a LangChain `@tool` rather than relying on Haystack's own tool-calling. Spike outcome determines whether the contribution becomes a docs issue or a feature-gap bug report. |
| Which embedding model wins hit@5 on EN/DE heating queries? | Phase 2 micro-benchmark (`intfloat/multilingual-e5-base` vs `BAAI/bge-m3` vs `paraphrase-multilingual-mpnet-base-v2`) | Pre-committing to e5-base before evidence repeats the "tutorial-default convenience trail" failure mode captured in Session 5 methodology lesson 1. |
| Monolithic `rag_search` vs topic-specialized tools vs hybrid with metadata filters? | Open Design Question #1 below; decided at Phase 4 Gate 1 after Phase 3 ingestion confirms section-header metadata is retrievable | Wrong choice inflates prompt routing complexity or degrades retrieval precision. |

Research tiers already completed (Phase 0.5 equivalents), no new research required before starting:
- `2026-04-07_langgraph-best-practices.md` — LangGraph / `create_agent`
- `2026-04-07_hybrid-langgraph-haystack-best-practices.md` — hybrid architecture
- `2026-04-17_local-model-selection_research.md` — `llama3.1:8b` default (Session 5)

---

## Experiment Gate (before implementation begins)

Sprint 2 is the first user-facing capability sprint (`rag_search` is the new capability). Experiment Gate fires, two experiments required:

### EXP-001: Retrieval quality hit@5 (capability experiment)
- [ ] **Dataset:** 10-15 hand-curated EN/DE queries with expected top-1 source document and section header. Mix: standards lookups ("What is DIN EN 12831?", "Was ist VDI 6030?"), system concepts ("How does a heating curve work?", "Was ist Spreizung?"), MLOps-leaning ("What ML techniques apply to heating-curve optimization?"). Stored as `eval/sprint2_retrieval_testset.yaml`.
- [ ] **Success criteria:** hit@5 >= 0.80 (8 of 10 hand-curated expected docs appear in top 5); hit@1 >= 0.50.
- [ ] **Failure handling:** if < 0.80, reranking (Sprint 3 stretch) moves into Sprint 2 MUST.
- [ ] **Runnable script:** `eval/exp001_retrieval_quality.py` — reuses the production retrieval pipeline, never a parallel implementation.

### EXP-002: Haystack OllamaChatGenerator tool-calling spike (capability experiment)
- [ ] **Target:** `OllamaChatGenerator(model="llama3.1:8b", tools=[add_tool])` in a minimal `scratch/haystack_ollama_tools_spike.py`, single turn.
- [ ] **Success criteria (three-outcome):**
  - PASS: tool is called with correct args → pattern works, docs gap is the contribution
  - FAIL-WITH-SIGNAL: Haystack emits tool-call JSON that the framework drops → feature gap, bug report
  - FAIL-NO-SIGNAL: no tool-call path exercised → feature missing entirely, design discussion
- [ ] **Output:** `dsm-docs/research/2026-MM-DD_haystack-ollama-tools-spike-result.md` documenting the chosen outcome branch and evidence (full trace, version pins, minimal repro).
- [ ] **Contribution:** regardless of outcome, an issue is filed on `haystack-core-integrations` with the specific gap description (per GE playbook). PR deferred until maintainer responds. No maintainer-response dependency in the sprint exit criteria.

---

## Branch Strategy

- **Level 3 sprint branch:** `sprint-2/rag-pipeline` (this branch), opened off `session-6/2026-04-18` per DSM_2.0.C Template 8 Branch Strategy ("each sprint creates a Level 3 sprint branch off the session branch"). BL-003 closure commit (`1366115`) rides with this branch until sprint merge.
- **Per-session branches:** `session-N/YYYY-MM-DD` created off `sprint-2/rag-pipeline`, merged back to the sprint branch at wrap-up via PR. Sprint 2 merges back to `main` at sprint close via a single sprint PR.
- **Recovery note:** this is the first sprint to use Level-3 sprint branches; Sprint 1 worked directly on session branches (documented deviation in `2026-04-07_sprint1_langgraph_plan.md §1.5`).

---

## Deliverables

### MUST (Sprint fails without these)

- [ ] **Phase 1 spike result** — `dsm-docs/research/2026-MM-DD_haystack-ollama-tools-spike-result.md` with one of the three outcome branches chosen + full evidence (EXP-002)
- [ ] **Phase 2 embedding benchmark** — `dsm-docs/research/2026-MM-DD_embedding-model-benchmark.md`; winner locked into `pyproject.toml` and tech-stack contract (backbone §2 updated if not e5-base)
- [ ] **Phase 3 ingestion pipeline** — `src/rag/ingest.py` (Haystack `Pipeline` factory) + `scripts/ingest.py` (CLI entrypoint). Idempotent (doc id = hash(source path + chunk index)). Produces persistent Chroma store at `data/chroma/` (gitignored).
- [ ] **Phase 4 retrieval pipeline** — `src/rag/retrieval.py` (Haystack `Pipeline` factory, stateless per run). Returns `List[Document]` with metadata `source_doc` + `section_header`.
- [ ] **Phase 4 `rag_search` tool** — `src/tools/rag_search.py`, LangChain `@tool` wrapping the retrieval pipeline. Monolithic/specialized/hybrid decision made here (Open Design Question #1).
- [ ] **Phase 5 retrieval tests** — `tests/test_retrieval.py` + `tests/test_rag_search.py`, 5+ retrieval-quality tests (hand-picked query → expected top-1 source).
- [ ] **Phase 5 EXP-001 run** — `eval/exp001_retrieval_quality.py` producing hit@5 >= 0.80 on the curated test set.
- [ ] **Phase 5 upstream contribution** — Haystack issue filed with specific gap description per GE playbook; issue URL captured in decision record.
- [ ] **Decision record** — `dsm-docs/decisions/2026-MM-DD_haystack-ollama-contribution-outcome.md` capturing spike outcome, contribution path (docs-gap vs bug-report vs feature-gap), and monolithic/specialized tool choice.
- [ ] **Boundary enforcement:** no LangGraph imports in `src/rag/`; no Haystack imports outside `src/rag/` and `src/tools/rag_search.py`. Verified by code review + optional import-assertion test.

### SHOULD (Expected, defer if blocked)

- [ ] **Tunable retrieval params via env:** `RAG_TOP_K`, `RAG_SCORE_THRESHOLD` wired through `src/config.py`.
- [ ] **Bilingual retrieval validation:** DE query (e.g., "Was ist die Vorlauftemperatur?") retrieves relevant EN section; added to EXP-001 testset.
- [ ] **Citation rendering in system prompt:** `[source: {doc} § {section}]` markers; Streamlit UI parses markers and renders a sources panel.
- [ ] **Blog journal entry** in `dsm-docs/blog/journal.md` capturing the capability-experiment-as-contribution-pipeline narrative (mirror of GE's pattern).

### COULD (Stretch)

- [ ] **Reranking** (two-stage retrieve ~20 → rerank ~5) via `TransformersSimilarityRanker` if Phase 5 hit@5 < 0.80 warrants it (moves to MUST automatically in that case).
- [ ] **Import-assertion test** — `tests/test_boundary.py` verifying no Haystack import in `src/graph.py` or `src/tools/*` except `rag_search.py`.
- [ ] **PR to Haystack** if maintainer responds to the issue within the sprint window; otherwise defer to post-sprint follow-up.

### WON'T (explicit out-of-scope)

- Query rewriting / HyDE (Sprint 3 stretch)
- Hybrid sparse+dense retrieval (Sprint 3 stretch)
- MLflow integration (Sprint 3 MUST)
- Docker packaging (Sprint 3 MUST)
- `SqliteSaver` persistent memory (Sprint 3 SHOULD)

---

## Phases

### Phase 1: Haystack Ollama tool-calling capability spike (EXP-002)
- **Focus:** Determine whether `OllamaChatGenerator(tools=[...])` works in practice; frame result as capability-experiment outcome.
- **Deliverables:** Phase 1 spike result doc, decision record stub.
- **Execution mode:** script (scratch/haystack_ollama_tools_spike.py runs one single-turn Ollama call)
- **DSM references:** DSM 4.0 §4 (capability experiments), DSM_2.0.C Experiment Gate.
- **Success criteria:** One of three outcome branches chosen with evidence; issue description drafted (not yet filed).

### Phase 2: Embedding model micro-benchmark
- **Focus:** Index 5-10 EN/DE heating queries against 2-3 multilingual embedding models; measure hit@5.
- **Deliverables:** Embedding benchmark doc, locked choice in `pyproject.toml` + backbone §2.
- **Execution mode:** script (`scratch/embedding_benchmark.py`, one-afternoon compute job)
- **DSM references:** Session 5 methodology lesson 1 (evidence-strength scale); backbone §4 MUST.
- **Success criteria:** Winner chosen on measured hit@5, rationale recorded.

### Phase 3: Ingestion pipeline
- **Focus:** Convert the 6 heating-guide MD files into a persistent Chroma store via header-aware chunking.
- **Deliverables:** `src/rag/chunking.py`, `src/rag/ingest.py`, `scripts/ingest.py`, `data/chroma/` (gitignored).
- **Execution mode:** both (script for chunking config, `scripts/ingest.py` CLI for running the pipeline).
- **DSM references:** backbone §4 ingestion pipeline spec.
- **Success criteria:** Running `scripts/ingest.py` produces a Chroma store; re-running is idempotent (same doc ids, no duplicates).

### Phase 4: Retrieval pipeline + `rag_search` tool
- **Focus:** Query-time pipeline; decide monolithic vs specialized rag_search; register tool with agent.
- **Deliverables:** `src/rag/retrieval.py`, `src/tools/rag_search.py`, update `src/tools/registry.py`, update `src/graph.py` to register the tool.
- **Execution mode:** script.
- **DSM references:** backbone §4, Open Design Question #1.
- **Success criteria:** From a fresh Python session, `rag_search("What is DIN EN 12831?")` returns a result with at least one document and section-header metadata.

### Phase 5: Retrieval tests + EXP-001 + contribution
- **Focus:** Close the experiment gate, validate hit@5, file the upstream issue, write decision record.
- **Deliverables:** `tests/test_retrieval.py`, `tests/test_rag_search.py`, `eval/sprint2_retrieval_testset.yaml`, `eval/exp001_retrieval_quality.py`, `dsm-docs/decisions/2026-MM-DD_haystack-ollama-contribution-outcome.md`, GitHub issue URL on `haystack-core-integrations`.
- **Execution mode:** both (script for EXP-001 runner, document for decision record and issue draft).
- **DSM references:** DSM 4.0 §4, DSM_2.0.C Sprint Boundary Checklist.
- **Success criteria:** pytest green, EXP-001 hit@5 >= 0.80, issue filed.

**Phase planning notes:**
- Phase 1 gates Phase 3-4 indirectly: if the spike reveals Haystack tool-calling is unusable, the *upstream contribution* shape changes but the *RAG subsystem* still ships (we wrap the Haystack retrieval pipeline in a LangChain `@tool`, not an OllamaChatGenerator tool). Architecture does not change on spike outcome.
- Phase 2 gates Phase 3 materially: ingestion must use the winning embedding model, not a guess.
- Phase 3 gates Phase 4: retrieval needs a store to retrieve from.
- Phases 4 and 5 can interleave Phase 5 test authoring with Phase 4 code.

---

## Phase Boundary Checklist (intra-sprint)

- [ ] Update `dsm-docs/feedback-to-dsm/{YYYY-MM-DD_sN_methodology.md}` with phase observations and scores
- [ ] Create checkpoint in `dsm-docs/checkpoints/` if significant milestone (phase complete, design question decided)
- [ ] Log decisions in `dsm-docs/decisions/` (Phase 1 spike outcome, Phase 2 embedding winner, Phase 4 monolithic/specialized choice)
- [ ] Update `dsm-docs/blog/journal.md` with narrative fragments (contribution journey, embedding benchmark surprises)

---

## Open Design Questions

1. **Monolithic vs specialized `rag_search`.** Panta 2026 precedent and Sprint 1 §5.1 individual unit converters argue for specialization (e.g., `standards_lookup_rag`, `systems_reference_rag`, `mlops_reference_rag`). Decided at **Phase 4 Gate 1** after Phase 3 confirms metadata richness. If section-header metadata reliably identifies document type, hybrid (one tool + metadata filter parameter) is also viable.
2. **Embedding model winner.** Decided at end of Phase 2 on measured hit@5, not pre-committed. Candidates: `intfloat/multilingual-e5-base`, `BAAI/bge-m3`, `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`.
3. **Contribution path on spike outcome.** Three branches (docs gap, feature bug, feature missing) lead to three different issue descriptions. Decided at end of Phase 1.
4. **Chunking strategy robustness.** `MarkdownHeaderTextSplitter` default behavior on the heating guide's heading hierarchy (H1-H4 mix, bilingual headings) is unverified. Validated empirically in Phase 3; swap to custom splitter if chunks split mid-section or lose context.
5. **Whether to adopt GE's artifact pattern verbatim.** GE shipped: deep-dive research + runnable experiment + blog journal + decision record. Ours could mirror this exactly. Decision deferred to end of Phase 5 based on time budget.
6. **Citation UI scope.** Sources panel in Streamlit is in SHOULD; the system prompt citation marker is in MUST. Decide at Phase 5 if the panel fits the sprint or defers to Sprint 3 polish.

---

## How to Resume

1. Read this sprint plan end-to-end
2. Read `2026-04-07_e2e_hybrid_backbone.md` §4 for the architectural target
3. Read `_inbox/done/2026-04-13_dsm-graph-explorer_contribution-playbook.md` for the contribution playbook
4. Read the most recent checkpoint in `dsm-docs/checkpoints/`
5. Check the current phase via the most recent decision record in `dsm-docs/decisions/` (Phase 1 result → Phase 2 result → Phase 4 tool-shape decision)
6. Verify branch state: should be on `sprint-2/rag-pipeline` or a session branch off it
7. Run `pytest` to confirm green baseline before starting new work

---

## Sprint Boundary Checklist

- [ ] Sprint close checkpoint in `dsm-docs/checkpoints/`
- [ ] Feedback files updated (`YYYY-MM-DD_sN_backlogs.md`, `YYYY-MM-DD_sN_methodology.md`)
- [ ] Decision log complete (spike outcome, embedding winner, tool-shape choice, contribution path)
- [ ] Tests passing (55 Sprint 1 + 5+ Sprint 2 retrieval = 60+ total)
- [ ] EXP-001 hit@5 >= 0.80 recorded with full metrics in the decision record or a dedicated experiment doc
- [ ] Haystack issue URL captured in `dsm-docs/decisions/2026-MM-DD_haystack-ollama-contribution-outcome.md`
- [ ] Blog journal entry on the contribution journey
- [ ] Backbone `2026-04-07_e2e_hybrid_backbone.md` updated if any Sprint 2 reality diverged from its §4
- [ ] README updated (Sprint 2 status, new setup step for `scripts/ingest.py`, new tool in the tools list)
- [ ] Sprint 2 branch merged to `main` via PR; `sprint-2/rag-pipeline` deleted after merge
- [ ] Next-steps summary at bottom of checkpoint: Sprint 3 goal, evaluation framework, MLflow + Docker
