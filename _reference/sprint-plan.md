# Utility Conversational AI — Sprint Plan

> **Superseded as authoritative plan (2026-04-14).** This document is retained
> as historical input material. The current authoritative orchestration is
> hybrid LangGraph (agent) + Haystack (RAG subsystem behind a LangChain `@tool`
> boundary), not pure LangGraph as framed below. The original sprint
> MUST/SHOULD/WON'T scope in this file is still useful reference.
>
> **Current plans of record:**
> - Backbone: `dsm-docs/plans/2026-04-07_e2e_hybrid_backbone.md`
> - Sprint 1: `dsm-docs/plans/2026-04-07_sprint1_langgraph_plan.md`
> - Decision: `dsm-docs/decisions/2026-04-07_orchestration-framework.md`
>
> Per the Actionable Work Items rule, only items in `dsm-docs/plans/` are
> actionable. This file is input material, not a work queue.

**Project:** Heating Systems Conversational Assistant
**Goal:** LangGraph-based conversational AI for residential heating domain, RAG over existing 6K-line documentation
**Origin:** Portfolio project filling conversational AI gap, oriented to AI Engineer roles in energy/utility sector
**alignment:** (agentic workflows + LLM reasoning, RAG pipelines, evaluation frameworks, prompt engineering standards, German C1+)

---

## Knowledge Base

Source: `~/dsm-residential-heating-ds-guide/` (existing project, ~5,800 lines)

| Document | Lines | Content |
|----------|-------|---------|
| 01_Domain_Fundamentals.md | 411 | German heating standards, DIN EN 12831, VDI 6030, VDI 2067, GEG, HeizKV |
| 02_Data_Science_ML.md | 1,085 | ML for heating systems, feature engineering, time series, anomaly detection |
| 03_Production_MLOps.md | 1,326 | MLflow, CI/CD, model serving, monitoring, drift detection |
| 04_Technical_Stack.md | 1,323 | Python ecosystem, data engineering, deployment patterns |
| 05_Applied_Scenarios.md | 1,187 | Real-world applications, heating curve optimization, load prediction |
| 06_References.md | 163 | Standards bibliography, further reading |

Companion app (deterministic tools source): `~/dsm-residential-energy/` (Streamlit heating curve simulator, DIN EN 12831, VDI 6030)

---

## Sprint 1: Conversation Engine + Deterministic Tools

**Goal:** LangGraph multi-turn conversation state machine with domain-specific tools and basic chat UI.

### MUST

- [ ] LangGraph conversation state machine (nodes: intent_classifier, tool_router, responder, follow_up_handler)
- [ ] Conversation state schema: message history, current intent, tool results, turn count
- [ ] Tool: heating curve calculator (slope, level, based on building year and system type)
- [ ] Tool: standard lookup (given a standard code like "DIN EN 12831", return scope and key parameters)
- [ ] Tool: unit converter (kW <-> kcal/h, degree-day calculations)
- [ ] Multi-turn conversation memory (LangGraph state, not external store)
- [ ] Streamlit chat UI (basic: text input, message history, tool call visibility)
- [ ] 5+ pytest tests for deterministic tools
- [ ] LLM provider: Ollama (local) or OpenAI, configurable

### SHOULD

- [ ] Conversation guardrails: out-of-scope detection, graceful deflection
- [ ] German language support (queries and responses)
- [ ] Conversation reset / new topic detection

### Deliverables

- Working chat interface with tool-calling agent
- Deterministic tools returning correct domain calculations
- README with architecture diagram

---

## Sprint 2: RAG Pipeline + Knowledge Retrieval

**Goal:** Add RAG over the heating documentation, so the agent can answer questions grounded in the knowledge base.

### MUST

- [ ] Document ingestion pipeline: markdown chunking (section-aware, respecting headers)
- [ ] ChromaDB vector store with embeddings (OpenAI or HuggingFace multilingual-e5)
- [ ] RAG tool integrated into LangGraph: retriever -> context injection -> grounded response
- [ ] Source citations in responses (document name, section header)
- [ ] Hybrid routing: deterministic tools for calculations, RAG for knowledge questions
- [ ] 5+ pytest tests for retrieval quality (known question -> expected source section)

### SHOULD

- [ ] Chunk metadata: document, section, subsection for precise attribution
- [ ] Retrieval parameters tunable (top_k, similarity threshold)
- [ ] Bilingual retrieval: German standard names resolve to correct English documentation sections

### Deliverables

- Agent answers domain questions with source citations
- Clear separation between calculated answers (tools) and retrieved answers (RAG)

---

## Sprint 3: Evaluation Framework + Production Polish

**Goal:** Systematic evaluation of conversation quality, plus production-ready demo.

### MUST

- [ ] Evaluation dataset: 20+ test conversations (question + expected answer + expected source)
- [ ] Metrics: factual accuracy (answer vs ground truth), retrieval relevance (correct source section), task completion (did the agent answer the question)
- [ ] MLflow experiment tracking for evaluation runs
- [ ] Prompt engineering comparison: at least 2 system prompt variants evaluated on the test set
- [ ] Conversation-level metrics: average turns to resolution, tool usage rate, out-of-scope rate
- [ ] README update: evaluation results, architecture, demo instructions
- [ ] Docker setup for reproducible deployment

### SHOULD

- [ ] Automated evaluation pipeline (run all test conversations, produce report)
- [ ] Cost tracking per conversation (token usage, provider costs)
- [ ] Streamlit UI polish: collapsible tool calls, source document links, conversation export

### COULD (stretch)

- [ ] Voice layer: Whisper STT + OpenAI TTS, voice input mode in Streamlit
- [ ] A/B testing: compare LLM providers on same test conversations
- [ ] German-only evaluation subset

### Deliverables

- Evaluation report with metrics
- Production-ready demo (Docker + Streamlit)
- Blog-ready project documentation

---

## Architecture Overview

```
User (text or voice)
    |
    v
[LangGraph State Machine]
    |
    +-- intent_classifier --> classify query type
    |
    +-- tool_router --------+-- heating_curve_calculator (deterministic)
    |                       +-- standard_lookup (deterministic)
    |                       +-- unit_converter (deterministic)
    |                       +-- rag_retriever (semantic search -> LLM grounding)
    |
    +-- responder -----------> generate response with citations
    |
    +-- follow_up_handler ---> detect follow-up vs new topic
    |
    v
[Streamlit Chat UI]
```

**State:** message_history, current_intent, tool_results, sources, turn_count

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Orchestration | LangGraph |
| LLM | OpenAI / Ollama (configurable) |
| Vector store | ChromaDB |
| Embeddings | HuggingFace multilingual-e5 or OpenAI |
| Deterministic tools | Python (ported from dsm-residential-energy) |
| UI | Streamlit |
| Evaluation | MLflow |
| Testing | pytest |
| Deployment | Docker |
| Voice (stretch) | Whisper (STT) + OpenAI TTS |

---

## Risk Register

| Risk | Mitigation |
|------|-----------|
| Looks like it was built specifically for ista | Frame as natural extension of existing heating domain work. The documentation predates the ista application. |
| 6K lines may be too small for meaningful RAG | Section-aware chunking with overlap. Quality of content matters more than volume for a demo. |
| Voice layer adds significant complexity | Marked as COULD, not MUST. Text-only is a complete demo. Voice is bonus. |
| Evaluation dataset is hand-crafted, not representative | Acknowledge as limitation. 20+ conversations is sufficient for a portfolio demo, not a production benchmark. |

---

## Success Criteria

The project is showcase-ready when:
1. A user can ask heating domain questions in English or German and get grounded, cited answers
2. Deterministic calculations (heating curves, standard lookups) return correct results
3. The evaluation framework produces quantified metrics on conversation quality
4. The README explains the architecture, shows results, and provides one-command setup