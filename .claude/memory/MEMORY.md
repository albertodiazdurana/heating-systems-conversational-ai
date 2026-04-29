# Heating Systems Conversational AI — Memory Index

## Latest Session
**Session 11 — 2026-04-29 (full wrap-up):** Opus 4.7 (1M). Sprint 2 Phase 3 ingestion landed: header-aware chunking + Haystack→Chroma pipeline + CLI runner, all behind the four-gate model. Five governance items: (1) Sprint 1 §6.5 boundary checklist retro-completed (8 [x] + 1 [N/A README §2 deferred]); plan moved to `done/`. (2) BL-420 §10.2.1 checkpoint identifier rule cached for next /dsm-checkpoint; BL-418/BL-419 acknowledged as user-scope/Central-only. (3) Inbox: 2 align-update entries → done/. (4) S10 checkpoint → done/. Implementation: src/rag/__init__.py, src/rag/chunking.py (split_markdown_file on H2/H3), src/rag/ingest.py (with_doc_ids via dataclasses.replace, build_ingestion_pipeline with cosine + OVERWRITE), scripts/ingest.py CLI; tests +13 (chunking 6, ingest 7); pyproject +3 deps (chroma-haystack, langchain-text-splitters, opentelemetry-exporter-otlp-proto-grpc>=1.41.0 to fix unpinned-OT-in-chromadb resolver skew). Real KB → 134 chunks; smoke run (bge-m3 download + Chroma write) deferred to next session. 6 [pattern]-and-[project]-tagged reasoning lessons.

## Previous Session
**Session 10 — 2026-04-23/29 (full):** /dsm-align v1.6.3→v1.8.0; Phase 1 T6 Haystack issue draft; Phase 2 bge-m3 chosen (gap 2.6× e5-base); BL-004 closed (provenance DAG); 3 feedback files pushed to Central.

## Key decisions
- **Orchestration:** hybrid LangGraph (agent) + Haystack (RAG subsystem behind a LangChain @tool boundary). See `dsm-docs/decisions/2026-04-07_orchestration-framework.md`.
- **Sprint 1 canonical stack:** `langchain.agents.create_agent` + `ChatOllama` + `InMemorySaver` + `@tool` + bilingual system prompt. See `dsm-docs/research/2026-04-07_langgraph-best-practices.md`.
- **Default model:** `llama3.1:8b`. Cascade: `llama3.1:8b` → `llama3.2:3b` → `qwen3:4b` → `LLM_PROVIDER=openai`. See `dsm-docs/research/2026-04-17_local-model-selection_research.md`.
- **Python runtime (S6):** `.venv` built on Python 3.12.13 via `/usr/bin/python3.12`. `/usr/bin/python3.11` on this WSL is 3.11.0rc1 — must not be used.
- **Sprint 2 branch model (S6):** Level-3 `sprint-2/rag-pipeline` off session-6; per-session branches off sprint-2; sprint-2 merges to main at sprint close only.
- **EXP-002 result (S9):** Outcome A — Haystack `OllamaChatGenerator(tools=[...])` + llama3.1:8b full tool-calling round-trip confirmed. RAG-behind-@tool architecture validated.
- **Embedding model (S10):** bge-m3 chosen over e5-base (Phase 2 micro-benchmark, gap 0.26 vs 0.10; cosine similarity). Decision record `dsm-docs/decisions/2026-04-24_phase2-embedding-model-selection.md`.
- **Phase 3 ingestion (S11):** MarkdownHeaderTextSplitter on H2/H3 (no soft-wrap); H1 captured as `part` metadata; doc id = sha256(source_doc::chunk_index)[:16]; ChromaDocumentStore(distance_function="cosine"); DuplicatePolicy.OVERWRITE. KB source path via `src.config.get_kb_source_dir()` (env var KB_SOURCE_DIR).
- **Resource-aware sprint planning (S9):** pool topology (all-models-weekly/sonnet-only) drives task ordering, not deferral. Convention added to Sprint 2 plan; BL sent to DSM Central.

## Pending
Pending items are owned by the S11 checkpoint, see `dsm-docs/checkpoints/2026-04-29_s11_checkpoint.md`.

## Memories
- [DSM Central propagation queue](project_dsm_central_pending.md) — pattern/ecosystem-scoped lessons awaiting upstream push to DSM Central.
