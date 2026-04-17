# Heating Systems Conversational AI

LangGraph-based conversational assistant for residential heating systems, bilingual (English / German). Portfolio project targeting AI Engineer roles in the energy and utility sector.

**Status:** Sprint 1 complete (6/7 exit boxes met; Streamlit UI boot blocked by [BL-003](dsm-docs/plans/BL-003_streamlit-boot-asyncio-invalidstate.md), agent layer fully working).

## Objective

A conversational agent that combines:

- **Deterministic domain tools** for heating curve calculation, degree-day estimation, unit conversion, and German heating-standards lookup, grounded in DIN EN 12831 / VDI 6030 / GEG.
- **RAG over a residential heating knowledge base** (~5,800 lines of curated documentation covering German heating standards, ML/DS applications, MLOps, and applied scenarios). *Sprint 2 deliverable.*
- **Bilingual interaction (EN / DE)** , the agent detects the user's language and responds in kind.

The goal is a portfolio-grade demonstration of agentic workflows, LLM reasoning, RAG pipelines, evaluation, and prompt engineering applied to a real industrial domain.

## Architecture (Sprint 1, current)

```
User (Streamlit chat or scripts/smoke_test.py)
        |
        v
  langchain.agents.create_agent  ----+
   (Ollama llama3.1:8b default)      |
   InMemorySaver per-session         |
        |                            |
        +--> 5 @tool functions
              - kw_to_kcal_per_h_tool
              - kcal_per_h_to_kw_tool
              - degree_days_tool
              - standard_lookup_tool
              - heating_curve_tool
        |
        v
      Response (EN / DE per user input)
```

### Target architecture (end of Sprint 3)

The current architecture extends in Sprints 2 and 3 with a Haystack RAG subsystem (ChromaDB + multilingual-e5 embeddings) exposed as a `knowledge_search` `@tool` to the same `create_agent`, and an MLflow evaluation harness wrapping the agent. See [`dsm-docs/plans/2026-04-07_e2e_hybrid_backbone.md`](dsm-docs/plans/2026-04-07_e2e_hybrid_backbone.md) for the full target.

## Tools

The 5 deterministic tools shipped in Sprint 1 (registered in [`src/tools/registry.py`](src/tools/registry.py)):

| Tool | Purpose |
|---|---|
| `kw_to_kcal_per_h_tool(kw)` | Convert thermal power kW → kcal/h |
| `kcal_per_h_to_kw_tool(kcal_per_h)` | Convert thermal power kcal/h → kW |
| `degree_days_tool(base_temp, daily_temps)` | Heating degree-days (HDD) sum from a daily temperature series |
| `standard_lookup_tool(standard, key="")` | Look up named values from German heating standards (DIN EN 12831, VDI 6030, DIN 4703, DIN EN 1264, DIN 4702-8, VDI 2067, DVGW W 551, VDI 3807). Empty `key` returns an overview of available keys. |
| `heating_curve_tool(t_outdoor, slope, ...)` | Compute flow temperature from a heating curve (Heizkennlinie) per VDI 6030 |

## Tech Stack

| Component | Technology |
|---|---|
| Orchestration | LangGraph (`langchain.agents.create_agent`, `InMemorySaver`) |
| LLM | Ollama (`llama3.1:8b` default) or OpenAI (configurable via `LLM_PROVIDER` env var) |
| Vector store | ChromaDB *(Sprint 2)* |
| Embeddings | HuggingFace multilingual-e5 *(Sprint 2)* |
| UI | Streamlit *(boot blocked by BL-003 on Python 3.11.0rc1; agent works via `scripts/smoke_test.py`)* |
| Evaluation | MLflow *(Sprint 3)* |
| Testing | pytest (55 unit + integration tests, all green) |
| Deployment | Docker *(Sprint 3)* |

## Run Locally

Tested on WSL2 Ubuntu with Python 3.11. Native Linux and macOS use the same commands.

### 1. Install Ollama and pull the default model

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1:8b   # ~4.9 GB
curl http://localhost:11434/api/tags   # verify daemon reachable
```

The Ollama install script registers a systemd service that starts on boot. NVIDIA GPUs are auto-detected via CUDA; CPU-only inference also works (slower).

### 2. Set up the project venv

```bash
git clone https://github.com/albertodiazdurana/heating-systems-conversational-ai.git
cd heating-systems-conversational-ai
python3.11 -m venv .venv     # or python3.12; see BL-003 for Python rc1 caveat
.venv/bin/pip install -e .
```

### 3. Run the smoke test (recommended way to verify end-to-end)

```bash
.venv/bin/python scripts/smoke_test.py
```

Runs all 5 plan §4.11 queries through the full `create_agent + Ollama` stack and writes evidence to [`dsm-docs/handoffs/2026-04-17_s5_step11_smoke_test_results.md`](dsm-docs/handoffs/2026-04-17_s5_step11_smoke_test_results.md). Exits 0 on full pass.

### 4. Streamlit UI (currently blocked)

```bash
.venv/bin/streamlit run app.py
```

On Python 3.11.0rc1 this aborts with `asyncio.InvalidStateError` , see [BL-003](dsm-docs/plans/BL-003_streamlit-boot-asyncio-invalidstate.md) for the diagnosis and fix path. The agent layer itself is fully working (smoke test confirms 5/5); only the Streamlit runtime needs a Python upgrade to a 3.11.x final or 3.12 venv.

### 5. Configuration

Environment variables (all optional, sensible defaults):

| Var | Default | Effect |
|---|---|---|
| `LLM_PROVIDER` | `ollama` | `ollama` or `openai` |
| `OLLAMA_MODEL` | `llama3.1:8b` | Any model present in `ollama list` |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Override for remote Ollama |
| `OPENAI_API_KEY` | none | Required when `LLM_PROVIDER=openai` |

Model selection rationale: see [`dsm-docs/research/2026-04-17_local-model-selection_research.md`](dsm-docs/research/2026-04-17_local-model-selection_research.md). Cascade: `llama3.1:8b` → `llama3.2:3b` → `qwen3:4b` → OpenAI.

## Roadmap

- [x] **Sprint 1** , Conversation engine: LangGraph `create_agent`, 5 deterministic tools, bilingual handling. Evidence: [`dsm-docs/handoffs/2026-04-17_s5_step11_smoke_test_results.md`](dsm-docs/handoffs/2026-04-17_s5_step11_smoke_test_results.md). Streamlit UI boot deferred via [BL-003](dsm-docs/plans/BL-003_streamlit-boot-asyncio-invalidstate.md).
- [ ] **Sprint 2** , RAG pipeline: ChromaDB ingestion of the heating knowledge base, retrieval tool, citation handling.
- [ ] **Sprint 3** , Evaluation and polish: MLflow evaluation framework, prompt iteration, Dockerization, full Streamlit integration.

## Domain Context

Residential heating systems in the German market. Key terms the agent handles:

- **Heizkennlinie** , heating curve relating outdoor temperature to flow temperature
- **Vorlauftemperatur** , flow (supply) temperature
- **Spreizung** , temperature spread between flow and return
- **Hydraulischer Abgleich** , hydraulic balancing across radiators

## Repository Layout

```
src/                Application code (graph, tools, prompts, config)
tests/              pytest suite (55 tests, all green)
scripts/            Helper scripts (smoke_test.py)
app.py              Streamlit UI entrypoint
_reference/         Preliminary planning and interaction-design documents
dsm-docs/           Project governance: research, plans, decisions, handoffs, blog
```

This project is developed using the [DSM (Data Science Methodology)](https://github.com/albertodiazdurana) framework as a spoke project; governance artifacts live under `dsm-docs/`.

## License

[MIT](LICENSE)
