# Heating Systems Conversational AI

LangGraph-based conversational assistant for residential heating systems, bilingual (English / German). Portfolio project targeting AI Engineer roles in the energy and utility sector.

**Status:** Planning phase , Sprint 1 research complete, implementation not yet started.

## Objective

A conversational agent that combines:

- **Deterministic domain tools** for heating curve calculation, degree-day estimation, and unit conversion, grounded in DIN EN 12831 / VDI 6030 / GEG.
- **RAG over a residential heating knowledge base** (~5,800 lines of curated documentation covering German heating standards, ML/DS applications, MLOps, and applied scenarios).
- **Bilingual interaction (EN / DE)** , the agent detects the user's language and responds in kind.

The goal is a portfolio-grade demonstration of agentic workflows, LLM reasoning, RAG pipelines, evaluation, and prompt engineering applied to a real industrial domain.

## Planned Architecture

```
User (Streamlit chat)
        |
        v
  LangGraph ReAct agent  ----+
   (Anthropic Claude)        |
        |                    |
        +--> Tools           +--> Vector store (ChromaDB)
        |     - heating_curve              ^
        |     - degree_day                 |
        |     - unit_converter             |
        |     - knowledge_search ----------+
        v
      Response (EN / DE)
```

## Tech Stack

| Component        | Technology                                  |
|------------------|---------------------------------------------|
| Orchestration    | LangGraph                                   |
| LLM              | Anthropic Claude (via `langchain-anthropic`) |
| Vector store     | ChromaDB                                    |
| Embeddings       | HuggingFace multilingual-e5                 |
| UI               | Streamlit                                   |
| Evaluation       | MLflow                                      |
| Testing          | pytest (unit + LangGraph integration)       |
| Deployment       | Docker                                      |

## Roadmap

- [ ] **Sprint 1** , Conversation engine: LangGraph ReAct agent, deterministic tools (heating curve, degree-day, unit converter), Streamlit chat UI, bilingual handling.
- [ ] **Sprint 2** , RAG pipeline: ChromaDB ingestion of the heating knowledge base, retrieval tool, citation handling.
- [ ] **Sprint 3** , Evaluation and polish: MLflow evaluation framework, prompt iteration, Dockerization, documentation.

## Domain Context

Residential heating systems in the German market. Key terms the agent handles:

- **Heizkennlinie** , heating curve relating outdoor temperature to flow temperature
- **Vorlauftemperatur** , flow (supply) temperature
- **Spreizung** , temperature spread between flow and return
- **Hydraulischer Abgleich** , hydraulic balancing across radiators

## Repository Layout

```
_reference/    Preliminary planning and interaction-design documents
dsm-docs/      Project governance: research, plans, decisions, handoffs
src/           Application code (planned: graph/, tools/, ui/)
tests/         pytest suite (planned)
```

This project is developed using the [DSM (Data Science Methodology)](https://github.com/albertodiazdurana) framework as a spoke project; governance artifacts live under `dsm-docs/`.

## License

[MIT](LICENSE)