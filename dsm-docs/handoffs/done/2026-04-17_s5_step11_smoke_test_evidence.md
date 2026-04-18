# Sprint 1 Step 11 Smoke Test Evidence

**Date Completed:** 2026-04-18
**Outcome Reference:** Consumed at Session 6 start

**Date created:** 2026-04-17 (Session 5 prep)
**Date completed:** _to fill in next session_
**Outcome reference:** _to fill in next session (commit hash, plan §6 box check)_

**Purpose:** Capture step 11 manual smoke-test evidence in a structured form
so the §6 exit-criteria boxes can be checked with traceable evidence rather
than "I ran it, it worked." Form pre-written in Session 5 for Session 6 to
fill in.

---

## Hardware context (from Session 5 probes)

| Resource | Observed | Probe |
|---|---|---|
| GPU | Quadro T1000 with Max-Q Design | `nvidia-smi -L` |
| VRAM total | 4096 MiB | `nvidia-smi --query-gpu=memory.total --format=csv` |
| VRAM free at probe time | 3166 MiB | `nvidia-smi --query-gpu=memory.free --format=csv` |
| CUDA runtime | 12.8 | `nvidia-smi` |
| CPU | Intel i7-10875H (16 threads) | `lscpu` |
| RAM | 31 GiB total, 25 GiB available | `free -h` |
| WSL kernel | 6.6.87.2-microsoft-standard-WSL2 | `uname -r` |

**Implication:** GPU passthrough live; Ollama in WSL2 will use the GPU. 4 GB
VRAM ceiling means 7-8B Q4_K_M models will partial-offload to CPU.

---

## Pre-test setup checklist

Fill in as completed:

- [ ] Ollama installed in WSL: `curl -fsSL https://ollama.com/install.sh | sh`
- [ ] `ollama serve` running (background or separate terminal)
- [ ] `ollama pull llama3.1:8b` completed (~4.9 GB, expect 10-30 min)
- [ ] `curl http://localhost:11434/api/tags` from WSL returns JSON listing `llama3.1:8b`
- [ ] `pip install -e .` (or equivalent project install) succeeds
- [ ] Smoke test 1 (graph construction): `python -c "from src.graph import build_agent; build_agent()"` succeeds
- [ ] `streamlit run app.py` starts without error
- [ ] First-load timing recorded: time from `streamlit run` to first render of chat input

**Default model selection:** `llama3.1:8b` per
[`dsm-docs/research/2026-04-17_local-model-selection_research.md`](../research/2026-04-17_local-model-selection_research.md)
§5.1.

---

## Smoke test queries (from Sprint 1 plan §4.11)

Five queries from `dsm-docs/plans/2026-04-07_sprint1_langgraph_plan.md` §4.11
lines 126-132. Each row gets filled in with actual model output.

### Q1. EN unit conversion

**Query:** "Convert 24 kW to kcal/h"

**Expected:** Tool call to `kw_to_kcal_per_h` with `kw=24`. Numeric answer
in kcal/h (~20640).

| Field | Observed |
|---|---|
| Tool called | _fill in_ |
| Tool args | _fill in_ |
| Tool result | _fill in_ |
| Final response | _fill in_ |
| Pass / Fail | _fill in_ |
| Notes | _fill in_ |

### Q2. EN standard lookup

**Query:** "What's DIN EN 12831?"

**Expected:** Tool call to `standard_lookup` with `standard="DIN EN 12831"`.
Response includes title (heat-load calculation) and brief description.

| Field | Observed |
|---|---|
| Tool called | _fill in_ |
| Tool args | _fill in_ |
| Tool result | _fill in_ |
| Final response | _fill in_ |
| Pass / Fail | _fill in_ |
| Notes | _fill in_ |

### Q3. EN heating curve

**Query:** "Heating curve flow temp at -5°C with slope 1.0"

**Expected:** Tool call to `heating_curve` with `outdoor_temp_c=-5,
slope=1.0` (and the default offset/exponent if model omits them). Numeric
flow temperature returned.

| Field | Observed |
|---|---|
| Tool called | _fill in_ |
| Tool args | _fill in_ |
| Tool result | _fill in_ |
| Final response | _fill in_ |
| Pass / Fail | _fill in_ |
| Notes | _fill in_ |

### Q4. DE deflection

**Query:** "Wie kalt war der Winter?"

**Expected:** Out of scope (no historical-weather tool); model should
deflect in German rather than fabricate or call an unrelated tool.

| Field | Observed |
|---|---|
| Tool called (should be none) | _fill in_ |
| Final response | _fill in_ |
| German? Y/N | _fill in_ |
| Pass / Fail | _fill in_ |
| Notes | _fill in_ |

### Q5. DE gating query (HARDEST, this is the §6 gate)

**Query:** "Berechne die Vorlauftemperatur bei -10°C mit Steigung 1.2"

**Expected:** Tool call to `heating_curve` with `outdoor_temp_c=-10,
slope=1.2`. Final response IN GERMAN with correct numeric result and
correct domain vocabulary ("Vorlauftemperatur", correct decimal comma in
the number, e.g., "32,5°C").

| Field | Observed |
|---|---|
| Tool called | _fill in_ |
| Tool args | _fill in_ |
| Tool result | _fill in_ |
| Final response (verbatim, copy from Streamlit) | _fill in_ |
| Response in German? Y/N | _fill in_ |
| Domain vocab correct? Y/N (Vorlauftemperatur, etc.) | _fill in_ |
| Numeric format German? Y/N (comma decimal, °C suffix) | _fill in_ |
| Pass / Fail (all three sub-criteria must pass) | _fill in_ |
| Notes | _fill in_ |

---

## Performance measurements

To be captured during Q5 (the heaviest query) using Ollama's response
metadata. Run `OLLAMA_DEBUG=1 ollama serve` if metadata not visible by
default.

| Metric | Value |
|---|---|
| Prompt eval rate (tokens/sec) | _fill in_ |
| Generation rate (tokens/sec) | _fill in_ |
| Time to first token | _fill in_ |
| Total response time | _fill in_ |
| GPU memory used during inference | _fill in_ |
| CPU memory used during inference | _fill in_ |
| GPU/CPU offload split (from `ollama ps`) | _fill in_ |

**Pass criterion:** Sustained ≥5 tok/s generation rate (per research §8.3).
Below 5 tok/s, fall back to `llama3.2:3b` per plan §6 cascade.

---

## Failure-mode response (per research §6)

### If Q5 fails on tool-call (model returns text, not structured call)

Likely cause: Llama 3.1 chat template registration issue (similar to
[continuedev #9639](https://github.com/continuedev/continue/issues/9639)).
Mitigation: verify Ollama Modelfile registers the Llama 3.1 chat template
correctly. If template engineering does not resolve, move to
`llama3.2:3b` (research §6.1).

### If Q5 latency intolerable (sustained <5 tok/s)

Move to `llama3.2:3b` (research §6.2). Pull required:
`ollama pull llama3.2:3b` (~2.0 GB).

### If Q5 German quality insufficient

Try `qwen3:4b` (research §6.3). Pull required: `ollama pull qwen3:4b`
(~2.5 GB).

### If all three local models fail

Set `LLM_PROVIDER=openai` + `OPENAI_API_KEY` in environment, restart
Streamlit. Plan §6 explicitly anticipates this fallback.

---

## §6 exit-criteria status (to update at end of step 11)

Cross-reference with `dsm-docs/plans/2026-04-07_sprint1_langgraph_plan.md`
§6:

- [ ] All 5 tool unit tests green (already done in Session 4 cont, 50/50 tests)
- [ ] Graph construction smoke test green (already done in Session 4 cont)
- [ ] `streamlit run app.py` starts without error → covered by setup checklist
- [ ] All 5 manual smoke test queries (section 4.11) produce expected tool
      call or deflection → covered by Q1-Q5 tables above
- [ ] **Gating: German tool-call works end-to-end** → covered by Q5 table
- [ ] README has "run locally" section → step 12, separate
- [ ] `pyproject.toml` pinned deps, no haystack-* deps yet → already done

---

## Outcome (fill in at end of step 11)

**Default model used:** _fill in (llama3.1:8b expected)_

**Model that passed §6 gating query:** _fill in_

**Tokens/sec sustained:** _fill in_

**Decision:** _Sprint 1 closed | switched to fallback {model} because {reason} | switched to OpenAI because {reason}_

**Commit hash for Sprint 1 close:** _fill in_

**Lessons learned to capture in `.claude/reasoning-lessons.md`:** _fill in_

---

**Next session opens with:** install Ollama → pull llama3.1:8b → fill in this
form Q1 through Q5 → check §6 boxes → step 12 (README) → close Sprint 1.
