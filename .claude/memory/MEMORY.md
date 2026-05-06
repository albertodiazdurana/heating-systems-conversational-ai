# Heating Systems Conversational AI — Memory Index

## Latest Session
**Session 13 — 2026-05-05 / 2026-05-07 (full wrap-up):** Opus 4.7 (1M). OSS contribution chain on issue #3263. PR deepset-ai/haystack-integrations#473 (Tool Calling section on landing page) and PR deepset-ai/haystack#11268 (Streaming with Tools section on component reference) opened; ollama-python#663 filed for tool_choice (upstream gap, not Haystack). User audit mid-session surfaced missing Definition of Ready: hatch installed, release note added via `hatch run release-note`, PR #11268 body rewritten to template, mutual-exclusion claim verified by 6-prompt backfill spike (PASS). Cleanup: README §2 `pip install -e .` → `uv sync`, `.venv.old-rc1/` reversibly moved to `/tmp`. BL-005 created (deferred-trigger blog post on OSS contribution + Take-AI-Bite, fires on PR merge). Sprint 2 close blog journal entry first-draft landed (alternate titles in HTML comment). 4 reasoning lessons captured (Verification, Protocol Hygiene, 2× Cross-Repo & Governance). Ecosystem feedback pushed to DSM Central proposing `Read-Before-Draft` protocol step.

## Previous Session
**Session 12 — 2026-04-30 / 2026-05-01 (full):** Sprint 2 closed. Phase 4 retrieval pipeline + `rag_search` hybrid tool; Phase 5 EXP-001 hit@5 0.75→0.83 PASS via B1 (exclude_intro) + B2 (accept_alternatives). Haystack issue #3263 filed.

## Key decisions
- **Orchestration:** hybrid LangGraph (agent) + Haystack (RAG subsystem behind a LangChain @tool boundary). See `dsm-docs/decisions/2026-04-07_orchestration-framework.md`.
- **Sprint 1 canonical stack:** `langchain.agents.create_agent` + `ChatOllama` + `InMemorySaver` + `@tool` + bilingual system prompt. See `dsm-docs/research/2026-04-07_langgraph-best-practices.md`.
- **Default model:** `llama3.1:8b`. Cascade: `llama3.1:8b` → `llama3.2:3b` → `qwen3:4b` → `LLM_PROVIDER=openai`. See `dsm-docs/research/2026-04-17_local-model-selection_research.md`.
- **Python runtime (S6):** `.venv` built on Python 3.12.13 via `/usr/bin/python3.12`. `/usr/bin/python3.11` on this WSL is 3.11.0rc1 — must not be used.
- **Sprint 2 branch model (S6):** Level-3 `sprint-2/rag-pipeline` off session-6; per-session branches off sprint-2; sprint-2 merges to main at sprint close only.
- **EXP-002 result (S9):** Outcome A — Haystack `OllamaChatGenerator(tools=[...])` + llama3.1:8b full tool-calling round-trip confirmed. Requires `temperature=0.0` + directive prompt for reliable `tool_calls` emission.
- **Embedding model (S10):** bge-m3 chosen over e5-base. See `dsm-docs/decisions/2026-04-24_phase2-embedding-model-selection.md`.
- **Phase 3 ingestion (S11):** MarkdownHeaderTextSplitter on H2/H3; doc id = sha256(source_doc::chunk_index)[:16]; ChromaDocumentStore(distance_function="cosine"); DuplicatePolicy.OVERWRITE.
- **Phase 4 tool shape (S12, Q1 hybrid):** single `rag_search_tool(query, part="")` with optional metadata filter on `meta.part`. Specialized N-tools rejected on LOC + tool-selection-ambiguity grounds. See `dsm-docs/decisions/2026-05-01_haystack-contribution-and-tool-shape.md`.
- **Phase 5 retrieval policy (S12):** intro chunks excluded by default at retrieval time (`exclude_intro=True`); chunking layer keeps intros addressable, retrieval layer owns the exclude policy. Compound AND filter shape required when both `part` and `exclude_intro` apply.
- **EXP-001 outcome (S12):** hit@5 = 0.83, hit@1 = 0.50 on 12-query EN/DE testset. Reranking remains a Sprint 3 stretch item; the two remaining misses (q04, q10) are the citation if Sprint 3 needs to prioritize it.
- **Haystack contribution (S12 → S13):** issue #3263 filed S12; maintainer responded 2026-05-05; PR #473 (haystack-integrations) + PR #11268 (haystack) opened; tool_choice filed as upstream issue ollama-python#663 (server-side gap, not Haystack PR).
- **OSS PR Definition of Ready (S13):** Read CONTRIBUTING.md + PR template + `.github/workflows/*.yml` BEFORE drafting any cross-repo PR. Cost ~10 min, prevents retroactive fixes. Ecosystem feedback proposes `Read-Before-Draft` as DSM_0.2 protocol addition.
- **Resource-aware sprint planning (S9):** pool topology (all-models-weekly/sonnet-only) drives task ordering, not deferral.

## Pending
Pending items are owned by the S13 checkpoint, see `dsm-docs/checkpoints/2026-05-07_s13_checkpoint.md`.

## Memories
- [DSM Central propagation queue](project_dsm_central_pending.md) — pattern/ecosystem-scoped lessons awaiting upstream push to DSM Central.
