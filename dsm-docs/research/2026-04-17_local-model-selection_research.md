# Local Model Selection for Sprint 1

**Purpose:** Choose a default local LLM for the Sprint 1 conversational agent
on this specific hardware (Quadro T1000, 4 GB VRAM), grounded in published
evidence rather than tutorial defaults.

**Target outcome:** A ranked recommendation cascade (primary → fast fallback →
no-evidence fallback → escape hatch) with every selection traceable to a cited
source or session-captured probe. Recommendation feeds Sprint 1 step 11
(manual smoke test) and supersedes the model-selection paragraph in
`2026-04-07_langgraph-best-practices.md §4`.

**Status:** Done

**Date:** 2026-04-17

**Author:** Session 5 (Heating Systems Conversational AI)

**Traceability:**
- Sprint 1 plan: [`dsm-docs/plans/2026-04-07_sprint1_langgraph_plan.md`](../plans/2026-04-07_sprint1_langgraph_plan.md), specifically §6 "Exit criteria" (gating German tool-call query) and §8 open question on model availability.
- Prior research it supersedes: [`dsm-docs/research/2026-04-07_langgraph-best-practices.md`](2026-04-07_langgraph-best-practices.md) §4 "Ollama model selection" — that section surveyed 2026 tutorial defaults; this doc is a project-fit study.

---

## 0. Why this research exists

The original Sprint 1 plan defaulted to `llama3.1:8b` and listed `qwen2.5:7b`
as the primary recommendation in the prior research doc. Both choices entered
the plan via a *survey of what 2026 tutorials default to* (LangChain forum,
Ollama tutorial pages, Haystack source defaults), not via an evidence-grounded
fit study for this repo on this hardware. The user flagged this convenience
trail as a methodological gap before committing to a model for step 11.

The methodological hinge of this re-evaluation is an explicit **evidence-
strength scale** applied uniformly to every candidate:

| Evidence strength | Example |
|---|---|
| **Strong** | Third-party published benchmark with method + score (e.g., Berkeley Function Calling Leaderboard score for the model at a stated quantization) |
| **Medium** | Vendor's own published benchmark in a technical report (e.g., Meta's MMLU-DE 60.59 for Llama-3.1-8B) |
| **Weak** | Vendor model-card capability claim without a number ("supports tool calling") |
| **Anecdotal** | Community reproduction in GitHub issues, HuggingFace discussions, Reddit threads |
| **None** | No information found in primary sources |

The prior research mixed these strengths uniformly. This doc weights them.

---

## 1. Hardware constraints

### 1.1 Probed facts

Captured this session via `nvidia-smi`, `free`, `nproc`, `lscpu`, and `df`:

| Resource | Observed | Probe |
|---|---|---|
| GPU | Quadro T1000 with Max-Q Design | `nvidia-smi -L` |
| VRAM total | 4096 MiB | `nvidia-smi --query-gpu=memory.total --format=csv` |
| VRAM free at probe time | 3166 MiB | `nvidia-smi --query-gpu=memory.free --format=csv` |
| Driver | 573.57 | `nvidia-smi --query-gpu=driver_version --format=csv` |
| CUDA runtime | 12.8 | `nvidia-smi` header |
| CPU | Intel i7-10875H (16 threads, base 2.30 GHz) | `lscpu` |
| RAM (WSL2) | 31 GiB total, 25 GiB available | `free -h` |
| Swap | 8 GiB | `free -h` |
| Disk free at `/` | 838 GiB | `df -h /` |
| WSL kernel | 6.6.87.2-microsoft-standard-WSL2 | `cat /proc/version` |
| Ollama running? | No (connection refused on `localhost:11434` and WSL2 gateway `10.255.255.254:11434`) | `curl --max-time 3 http://localhost:11434/api/tags` |

**Implication:** GPU passthrough is live (CUDA 12.8 visible from inside WSL2).
Ollama installed natively in WSL2 will use the GPU directly. The 4 GB VRAM
ceiling is the hard constraint that drives everything below.

### 1.2 VRAM-fit math at Q4_K_M

Q4_K_M is the Ollama default quantization for all candidates considered. Per
[llama.cpp quantize README](https://github.com/ggml-org/llama.cpp/blob/master/tools/quantize/README.md),
Q4_K_M uses ~4.5 bits per weight and is labeled "medium, balanced quality,
recommended". On-disk size approximates VRAM need plus ~1 GB for KV cache and
runtime overhead at modest context.

| Model | Q4_K_M disk (Ollama) | VRAM need est. | Fits 4 GB? |
|---|---|---|---|
| `qwen2.5:3b` | 1.9 GB | ~2.9 GB | Yes, comfortable |
| `llama3.2:3b` | 2.0 GB | ~3.0 GB | Yes, comfortable |
| `phi3.5:3.8b` | 2.2 GB | ~3.2 GB | Yes, tight |
| `qwen3:4b` | 2.5 GB | ~3.5 GB | Yes, tight |
| `gemma3:4b` | 3.3 GB | ~4.3 GB | **Borderline / no** with KV cache at 32K context |
| `qwen2.5:7b` | 4.7 GB | ~5.7 GB | **No** — partial CPU offload |
| `llama3.1:8b` | 4.9 GB | ~5.9 GB | **No** — partial CPU offload |

Sources: [Ollama qwen2.5:3b](https://ollama.com/library/qwen2.5:3b),
[llama3.2:3b](https://ollama.com/library/llama3.2:3b),
[phi3.5:3.8b](https://ollama.com/library/phi3.5:3.8b),
[qwen3:4b](https://ollama.com/library/qwen3:4b),
[gemma3:4b](https://ollama.com/library/gemma3:4b),
[qwen2.5:7b](https://ollama.com/library/qwen2.5:7b),
[llama3.1:8b](https://ollama.com/library/llama3.1:8b).

### 1.3 Partial-offload latency expectations for 7-8B class

Plan §6 explicitly accepts the OpenAI fallback if local performance is
unacceptable. This bounds the cost of "model is too slow" and means latency
is a *soft* constraint, not a hard one. With CUDA-aware llama.cpp, ~50-70%
of a 7-8B Q4_K_M model can stay on GPU on a 4 GB VRAM card; the rest is CPU
inference at the i7-10875H's memory bandwidth. Realistic throughput estimate:
5-15 tokens/sec for prompt processing, slower for generation under multi-turn
tool-call traces. Step 11 measures this empirically.

---

## 2. Screening criteria

Six criteria, applied in elimination order. Each criterion has an explicit
"what counts as Pass" definition and an evidence-strength threshold.

### C1. Tool-calling reliability (hard filter)

**What counts as Pass:** Either (a) a third-party structured-tool-call
benchmark score (BFCL preferred) with a passing number, OR (b) a vendor
explicit tool-calling claim in the model card AND no contradicting community
evidence.

**Why it's the first filter:** The agent uses `langchain.agents.create_agent`
with 5 `@tool` definitions. A model that cannot reliably emit OpenAI-style
function-call JSON fails Sprint 1 step 11 immediately, regardless of any other
strength.

### C2. Multilingual EN/DE (hard filter)

**What counts as Pass:** A published per-language German benchmark number
(MGSM-DE, MMLU-DE, Global-MMLU-DE, FLORES-200 EN/DE, or Belebele DE), OR
explicit vendor listing of German as an officially-supported language with at
least one corroborating data point.

**Why hard:** Sprint 1 plan §6 gating exit-criterion is the German query
"Berechne die Vorlauftemperatur bei -10°C mit Steigung 1.2" — must trigger the
`heating_curve` tool AND respond in German. A model with weak German degrades
Sprint 1 to "works in English only", which fails §6.

### C3. Context window (medium filter, ≥32K)

**What counts as Pass:** Native context ≥ 32K tokens. Tool-call agents
accumulate `ToolMessage` history fast; 8K is tight for multi-turn traces.

### C4. VRAM fit on T1000 4 GB (soft filter)

**What counts as Pass:** Q4_K_M model + KV cache at 32K context fits in
~4 GB. Models exceeding this still rank if their evidence on C1+C2 dominates.
Latency cost of partial offload is accepted under the OpenAI escape hatch.

### C5. Domain vocabulary tolerance (deferred to step 11)

No published benchmark covers HVAC technical German vocabulary
("Heizkennlinie", "Vorlauftemperatur", "Spreizung", "hydraulischer Abgleich").
This criterion is acknowledged but cannot be scored from literature; deferred
to step 11 empirical verification.

### C6. License polish for portfolio repo (soft filter, tiebreaker)

**Tier 1 (best):** MIT, Apache 2.0
**Tier 2 (acceptable):** Llama Community License, Gemma Terms of Use
**Tier 3 (problematic):** Non-commercial / research-only

---

## 3. Candidate scoring grid

Seven candidates, scored across the six criteria. Cells use:

- ✓ Strong = Third-party benchmark or vendor benchmark, passing
- ✓ Medium = Vendor capability claim, no contradicting evidence
- ⚠ Caveat = Vendor claim with contradicting community evidence OR partial pass
- ✗ Fail = Failing benchmark, no claim, or excluded by criterion definition
- — None = No published information found

| Model | C1 Tool-call | C2 German | C3 Context | C4 VRAM fit | C6 License |
|---|---|---|---|---|---|
| `qwen2.5:3b` | ⚠ Framework-only ([Qwen-Agent](https://github.com/QwenLM/Qwen-Agent)), [BFCL 38.7 v3](https://openreview.net/forum?id=2GmDdhBdDk) | ⚠ German listed in 29 langs ([HF](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct)), no per-lang number | ✓ 32K | ✓ 1.9 GB | ✗ qwen-research **non-commercial** ([LICENSE](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct/blob/main/LICENSE)) |
| `llama3.2:3b` | ⚠ **Removed from BFCL** Nov 2024 for prompt-style template ([CHANGELOG](https://github.com/ShishirPatil/gorilla/blob/main/berkeley-function-call-leaderboard/CHANGELOG.md)); Meta blog claims tool-calling ([Meta](https://ai.meta.com/blog/llama-3-2-connect-2024-vision-edge-mobile-devices/)) | ✓ **MMLU-DE 53.3** ([MODEL_CARD](https://github.com/meta-llama/llama-models/blob/main/models/llama3_2/MODEL_CARD.md)); German officially supported ([HF](https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct)) | ✓ 128K | ✓ 2.0 GB | ✓ Llama 3.2 Community |
| `qwen3:4b` | ✓ Vendor claim explicit ([HF](https://huggingface.co/Qwen/Qwen3-4B)); BFCL submitted, score not retrievable from leaderboard ([CHANGELOG #1015](https://github.com/ShishirPatil/gorilla/blob/main/berkeley-function-call-leaderboard/CHANGELOG.md)) | — Aggregate MMMLU 71.42 / MGSM 67.74 only ([Qwen3 report](https://arxiv.org/html/2505.09388v1)); German not named in supported list | ✓ 32K native, 131K with YaRN | ✓ 2.5 GB | ✓ Apache 2.0 |
| `gemma3:4b` | ✓ Vendor claim explicit ([Google blog](https://blog.google/technology/developers/gemma-3/)); BFCL submitted, no score retrieved | — Aggregate "140+ languages" only ([HF blog](https://huggingface.co/blog/gemma3)); German not named | ✓ 128K | ⚠ 3.3 GB borderline | ⚠ Gemma Terms of Use |
| `phi-3.5-mini:3.8b` | ✗ No vendor tool-call claim; community reports of empty `tool_calls` ([HF discussion #7](https://huggingface.co/microsoft/Phi-3.5-mini-instruct/discussions/7)) | ✓✓ **MMLU-DE 62.4, MGSM-DE 69.6** ([HF](https://huggingface.co/microsoft/Phi-3.5-mini-instruct)) — best of all 7 | ✓ 128K | ✓ 2.2 GB | ✓ MIT |
| `qwen2.5:7b` | ⚠ Framework-only ([Qwen-Agent](https://github.com/QwenLM/Qwen-Agent)); [BFCL 44.7 overall, 71.8 single-turn AST v3](https://openreview.net/forum?id=2GmDdhBdDk) | ⚠ German listed in 29 langs ([HF](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct)), no per-lang number | ✓ 131K | ✗ 4.7 GB partial offload | ✓ Apache 2.0 |
| `llama3.1:8b` | ✓✓ Vendor chat-template claim ([HF](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct)); **BFCL 76.1** parallel-multi tool-calling ([Meta eval_details](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/eval_details.md), [FriendliAI](https://medium.com/friendliai/experience-meta-llama-3-1s-outstanding-performance-on-friendli-7fef3510f020)) | ✓✓ **MMLU-DE 60.59** ([Meta eval_details](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/eval_details.md)); German officially supported | ✓ 128K | ✗ 4.9 GB partial offload | ✓ Llama 3.1 Community |

### 3.1 Headline finding

**No 3-4B candidate has both a published German benchmark number AND a
published structured-tool-calling benchmark number.** Every small-model
candidate has at most one measured number on the two hard filters.

The 7-8B "stretch" tier has both kinds of evidence, but does not fit the
T1000 4 GB VRAM and will partial-offload to CPU.

The single model in the entire shortlist with **both hard-filter benchmarks
measured and passing** is `llama3.1:8b`.

### 3.2 Quantization gap (caveat applying to all rows)

All BFCL and Meta-published evaluations were run on BF16 weights, not on the
Q4_K_M quantization Ollama serves by default. There is no public BFCL
benchmark for the 3-8B model class at Q4_K_M.

llama.cpp's own table shows +0.0535 perplexity delta at Q4_K_M for 7B
([README](https://github.com/ggml-org/llama.cpp/blob/master/tools/quantize/README.md)),
which is small. But the broader literature converges on a key point:
*structured-output and "precise adherence to format" tasks degrade
disproportionately versus a plain perplexity delta would suggest*.

- [Red Hat half-million-eval study](https://developers.redhat.com/articles/2024/10/17/we-ran-over-half-million-evaluations-quantized-llms): 4-bit stays close to FP for general tasks; degradation spikes at 3-bit.
- [arXiv 2501.03035 on quantization and reasoning](https://arxiv.org/html/2501.03035v2): up to 32% accuracy loss on numerical/planning tasks under aggressive quant.
- [LocalBench methodology](https://localbench.substack.com/p/gguf-benchmark-methodology): explicitly includes a tool-calling category measured via KL divergence vs BF16; published tables not retrievable.

**Read all BFCL numbers in the grid above as upper bounds.** Real Q4_K_M
performance is unknown but plausibly worse than the BF16 score by some
fraction.

### 3.3 Community evidence (anecdotal but converging)

Community reports of model + Ollama + LangChain integration issues, by
candidate:

- **Qwen2.5 (3B + 7B):** Multiple chat-template breakage issues. [vllm #9454](https://github.com/vllm-project/vllm/issues/9454) (langchain function-call errors), [ollama #8588](https://github.com/ollama/ollama/issues/8588) ("Qwen not recognizing tools"), [ollama #14745](https://github.com/ollama/ollama/issues/14745) ("Qwen prints tool call instead of executing it" — chat-template regression). Pattern: model emits the tool call as text rather than as a structured call. Affects both sizes. Fixable via correct template, but ongoing.
- **Phi-3.5-mini:** [HF discussion #7](https://huggingface.co/microsoft/Phi-3.5-mini-instruct/discussions/7) reports empty `tool_calls`; model narrates "if I were not in a simulation, I would call tool X" instead of emitting the call. Reliability OK with one tool, degrades with multiple. Reproducible by multiple users.
- **Llama-3.1-8B:** [continuedev #9639](https://github.com/continuedev/continue/issues/9639) shows Q4_K_M GGUF returning "model does not support tools" (chat-template registration issue, not weight issue). Fixable.
- **Gemma3 (March 2025 release):** Too new for community signal volume.
- **Qwen3 (April 2025 release):** Too new for community signal volume.
- **Llama-3.2-3B:** No specific LangChain issue thread surfaced; the BFCL removal is the strongest signal and is structural rather than community.

The pattern across all candidates: **chat-template + quantization combination
is where tool-calling breaks, not the BF16 weights.** This is empirically
confirmed in step 11 by running the gating query, not predicted from the
literature.

---

## 4. Models excluded early

Four candidates eliminated before the recommendation cascade, with the
elimination reason and the evidence supporting it.

### 4.1 `phi-3.5-mini:3.8b` — eliminated on tool-calling

Has the **best published German numbers of all 7 candidates** (MMLU-DE 62.4,
MGSM-DE 69.6, both per-language and from the vendor's own eval). License is
MIT (best in shortlist). Fits VRAM cleanly (2.2 GB).

Excluded because:
1. Microsoft does not claim tool-calling support for Phi-3.5-mini in the
   [HF model card](https://huggingface.co/microsoft/Phi-3.5-mini-instruct).
2. [HF discussion #7](https://huggingface.co/microsoft/Phi-3.5-mini-instruct/discussions/7)
   reports reproducible empty-`tool_calls` failures and a narration-instead-of-execution pattern.
3. C1 is a hard filter; the German evidence cannot rescue a model that fails
   the tool-calling gate.

If Sprint 3 reopens model selection with relaxed Sprint 1 constraints (e.g.,
custom tool-call template engineering), Phi-3.5-mini would re-enter the
shortlist.

### 4.2 `qwen2.5:3b` — eliminated on license

[qwen-research license](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct/blob/main/LICENSE)
is non-commercial. For a portfolio repo the technical use is OK, but the
license carries a yellow flag for any future commercial demo or adaptation,
and the rest of the Qwen2.5 family (7B, 14B) is Apache 2.0 — there is no
reason to take the license hit on the 3B size when alternatives are available.

### 4.3 `qwen2.5:7b` — strictly dominated by `llama3.1:8b`

Both models partial-offload to CPU on the T1000 (4.7 GB and 4.9 GB
respectively). On every measurable axis at the same VRAM cost:

| Axis | qwen2.5:7b | llama3.1:8b |
|---|---|---|
| BFCL overall | 44.7 v3 (BFCL paper) | 76.1 (Meta own, parallel-multi) |
| Vendor tool-call claim | None (framework via Qwen-Agent) | Explicit (chat template) |
| German benchmark | None published | MMLU-DE 60.59 (Meta own) |
| License | Apache 2.0 | Llama 3.1 Community |
| Disk | 4.7 GB | 4.9 GB |

Qwen2.5-7B wins only on license (Apache 2.0 vs Llama Community), which is a
soft tiebreaker. It loses on every measurable hard-filter axis.

### 4.4 `gemma3:4b` — strictly dominated by `qwen3:4b`

Both have **zero measured numbers on either hard filter**. The tiebreakers:

| Tiebreaker | qwen3:4b | gemma3:4b | Winner |
|---|---|---|---|
| Disk / VRAM headroom | 2.5 GB | 3.3 GB | qwen3 |
| License | Apache 2.0 | Gemma Terms | qwen3 |
| Vendor tool-call claim | Explicit | Explicit | tie |
| Per-language German number | none | none | tie |
| Tokenizer efficiency on European languages | not studied | best-in-class per [Occiglot](https://occiglot.eu/posts/eu_tokenizer_perfomance/) | gemma3 |
| Community signal | thin | none (Mar 2025 release) | qwen3 |

The Occiglot tokenizer study finds Gemma's 256k-vocab tokenizer best-in-class
on European languages. Tokenizer efficiency means German text is *encoded*
efficiently — improves throughput and context-window economy — but it does
**not** predict the model *generates* idiomatic German.

In a tiebreak between two zero-evidence models, "smaller + cleaner license"
beats "potentially-better-tokenizer-but-no-output-evidence." There is no
scenario where reaching for `gemma3:4b` makes sense that `qwen3:4b` would not
be tried first. Strictly dominated → eliminated.

---

## 5. Recommendation cascade

Three local-model slots plus an OpenAI escape hatch. Every entry traces back
to evidence cited in §3.

### 5.1 Primary: `llama3.1:8b`

**Why:** The only candidate in the entire shortlist with **both** hard-filter
benchmark numbers measured and passing:

- BFCL 76.1 on parallel-multi tool calling ([Meta eval_details](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/eval_details.md))
- MMLU-DE 60.59 ([Meta eval_details](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/eval_details.md))

Vendor tool-call claim is explicit ([HF model card](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct)).
German is in the official 8-language list. 128K context. Llama 3.1 Community
license is acceptable for portfolio.

**Cost accepted:** Partial CPU offload at 4.9 GB on a 3.2 GiB-free 4 GB GPU.
Realistic latency 5-15 tok/s based on §1.3 estimates. If unacceptable in
step 11, fall back per §6 of the Sprint 1 plan.

**Why this overrides "VRAM fit" as a hard filter:** Plan §6 explicitly accepts
the OpenAI fallback if local performance is unacceptable. This bounds the cost
of "model is too slow" — we just switch providers. Latency is a *soft*
constraint, not a hard one. Once latency is soft, evidence quality wins the
ranking. Llama-3.1-8B has the most evidence.

### 5.2 Fast fallback: `llama3.2:3b`

**When to switch:** If `llama3.1:8b` latency is intolerable in step 11.

**Why this rank:** The **only** 3B candidate with a published per-language
German benchmark (MMLU-DE 53.3, [Meta MODEL_CARD](https://github.com/meta-llama/llama-models/blob/main/models/llama3_2/MODEL_CARD.md)).
Same chat-template family as llama3.1 — the engineering surface for getting
the tool template right is shared.

**Concerns:**
- BFCL **removed Llama-3.2 in November 2024** for using a prompt-style
  template ([CHANGELOG](https://github.com/ShishirPatil/gorilla/blob/main/berkeley-function-call-leaderboard/CHANGELOG.md)).
  This is a documented, structural concern for `langchain.agents.create_agent`
  integration. Mitigation: follow Meta's chat-template documentation precisely
  rather than relying on the prompt-style format BFCL flagged.
- Lower German quality than the primary (53.3 vs 60.59 MMLU-DE).

### 5.3 No-evidence fallback: `qwen3:4b`

**When to switch:** If both Llama options fail tool-calling integration in
step 11.

**Why this rank:** Apache 2.0, vendor tool-call claim explicit, no negative
signals from community or BFCL, fits VRAM with comfortable headroom (2.5 GB
in 3.2 GB free). Released April 2025 with explicit "expertise in agent
capabilities, enabling precise integration with external tools in both
thinking and unthinking modes" ([HF](https://huggingface.co/Qwen/Qwen3-4B)).

**Honest caveat:** **Zero measured numbers** on either hard filter. BFCL
submission exists ([CHANGELOG #1015](https://github.com/ShishirPatil/gorilla/blob/main/berkeley-function-call-leaderboard/CHANGELOG.md))
but the leaderboard is JS-rendered and the per-model number was not
retrievable. Aggregate Qwen3 multilingual (MMMLU 71.42 for 4B per the
[Qwen3 tech report](https://arxiv.org/html/2505.09388v1)) does not break out
per-language. This is a faith-based selection on top of a strong vendor claim.

### 5.4 Escape hatch: `LLM_PROVIDER=openai`

**When to use:** All three local models fail step 11 (tool-call integration
issues that cannot be fixed via template engineering, OR latency unacceptable
across the board).

**Cost accepted:** External service dependency, per-request cost, no offline
operation.

**Already wired:** `src/config.py:36-46` reads `LLM_PROVIDER` and routes to
either `ChatOllama` or `ChatOpenAI`. Plan §6 explicitly anticipates this
switch ("If this fails on `qwen2.5:7b`, document the observed failure and
switch `LLM_PROVIDER=openai` as the Sprint 1 baseline").

---

## 6. What changes if step 11 contradicts these recommendations

Three concrete failure modes the recommendation cascade must handle, and the
response in each case.

### 6.1 `llama3.1:8b` tool-calling fails on Q4_K_M (template registration issue)

**Detection:** Smoke test queries return "model does not support tools" or
empty `tool_calls`, similar to [continuedev #9639](https://github.com/continuedev/continue/issues/9639).

**Response:** Verify the Llama 3.1 chat template is registered correctly in
the Ollama Modelfile. If template engineering does not resolve the issue,
move to fast fallback.

### 6.2 `llama3.1:8b` latency intolerable

**Detection:** Tokens/sec under 5 sustained, or first-token latency over 30s.

**Response:** Move to fast fallback (`llama3.2:3b`). Document the observed
throughput in the step 11 evidence. If 3B German quality is also
insufficient (e.g., the gating German query produces wrong tool args because
the model misreads "Steigung 1.2"), move to escape hatch (OpenAI).

### 6.3 Llama-3.1-8B German quality insufficient on this prompt

**Detection:** Gating query "Berechne die Vorlauftemperatur bei -10°C mit
Steigung 1.2" triggers wrong tool, or correct tool with wrong args, or tool
result is summarized in English instead of German.

**Response:** Try `qwen3:4b` (no-evidence fallback) before OpenAI. The
hypothesis: if MMLU-DE 60.59 is insufficient on this prompt, perhaps Qwen3's
broader multilingual training (119 languages, 36T tokens per
[tech report](https://arxiv.org/html/2505.09388v1)) holds up better despite
the lack of per-language number.

---

## 7. Counter-evidence and honest gaps

Areas where the literature does not support a confident answer, surfaced so
the recommendation can be re-evaluated when better evidence becomes available.

### 7.1 Phi-3.5-mini has the best measured German numbers and is excluded

The hard filter on tool-calling (§4.1) excludes the model with the strongest
German evidence in the shortlist. This is a real cost of the chosen
methodology — if Sprint 3 reopens model selection with custom tool-template
engineering on the table, Phi-3.5-mini deserves another look.

### 7.2 Qwen3 might actually be excellent and we have no measured evidence

The Qwen3 tech report ([arXiv 2505.09388](https://arxiv.org/html/2505.09388v1))
publishes only aggregate multilingual numbers for the 4B model. Aggregate
MMMLU 71.42 is high; aggregate MGSM 67.74 is competitive. If the per-language
German number existed, Qwen3-4B might rank ahead of llama3.2:3b for the fast
fallback slot. We don't know.

### 7.3 BFCL is BF16, Ollama is Q4_K_M

All third-party tool-calling numbers are upper bounds. Real Q4_K_M
performance is plausibly worse by some unknown fraction. The
[LocalBench methodology](https://localbench.substack.com/p/gguf-benchmark-methodology)
addresses this with a tool-calling-via-KL-divergence measurement, but the
published tables for 3-8B models were not retrievable in this research.

### 7.4 No benchmark covers HVAC technical German

"Heizkennlinie", "Vorlauftemperatur", "Spreizung", "hydraulischer Abgleich" —
no published benchmark covers domain vocabulary tolerance in German
heating-engineering text. The [Occiglot tokenizer study](https://occiglot.eu/posts/eu_tokenizer_perfomance/)
addresses tokenization efficiency but not generation quality on technical
prose. This is the kind of gap that *only* step 11 empirical testing can fill.

### 7.5 Community evidence is anecdotal

GitHub issues and HuggingFace discussions (vllm#9454, ollama#8588,
continuedev#9639, HF Phi-3.5 discussion #7) are real signals but are
self-selected: people post when things break, not when they work. The pattern
that emerges (chat-template + quantization is where tool-calling breaks) is
robust because it's reproducible across vendors, but the specific "this model
+ this Ollama version + this LangChain version is broken" claims need
session-time verification, not literature trust.

---

## 8. What step 11 must verify empirically

Three concrete questions literature cannot answer for *this* prompt + tool
registry on *this* hardware. Step 11 evidence must address each.

### 8.1 Q4_K_M tool-call reliability for `llama3.1:8b` via Ollama + langchain create_agent

**Test:** Run the 5 plan §4.11 smoke queries. Record per-query: did the model
emit a structured tool-call? Did it call the *correct* tool? Did it pass
*correct* arguments?

**Pass criterion:** ≥4/5 queries trigger the right tool with correct args.

### 8.2 Idiomatic German for HVAC technical prose

**Test:** Gating query "Berechne die Vorlauftemperatur bei -10°C mit Steigung
1.2" must (a) trigger `heating_curve` tool, (b) pass `outdoor_temp_c=-10` and
`slope=1.2`, (c) summarize the result in German with correct domain
vocabulary.

**Pass criterion:** All three sub-criteria met. Native-speaker review of the
German response if available; otherwise spot-check for: correct tense, correct
declension on "Vorlauftemperatur", correct numeric formatting (German uses
comma decimal, e.g., "32,5°C").

### 8.3 Actual tokens/sec on this hardware

**Test:** Measure with `OLLAMA_DEBUG=1` or Ollama's `/api/generate` response
metadata. Record prompt eval rate and generation rate separately.

**Pass criterion:** Sustained ≥5 tok/s generation rate makes the model
usable interactively. Below 5 tok/s, fall back per §6.1.

---

## 9. Plan §6 update recommendation

This research recommends the following edits to
`dsm-docs/plans/2026-04-07_sprint1_langgraph_plan.md` §6 "Exit criteria",
to be applied in a separate turn (this doc is research-only).

### 9.1 Default model line

Current §6 implicitly references `qwen2.5:7b` as the gating model. Replace
with `llama3.1:8b` per §5.1 of this research.

### 9.2 Fallback ladder

Current §6 mentions only `LLM_PROVIDER=openai` as a fallback. Widen to:

> Fallback ladder if `llama3.1:8b` fails step 11:
> 1. `llama3.2:3b` (faster, lower German quality, same template family)
> 2. `qwen3:4b` (no measured evidence, vendor tool-call claim)
> 3. `LLM_PROVIDER=openai`

### 9.3 Reference

Add to §6:

> Model selection rationale: see
> `dsm-docs/research/2026-04-17_local-model-selection_research.md`.

The plan edit is **not** done in this turn; it is a separate Edit operation
gated on this research being approved.

---

## 10. Sources

### Vendor model cards (HuggingFace)

- [Qwen2.5-3B-Instruct](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct), [LICENSE](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct/blob/main/LICENSE)
- [Qwen2.5-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct)
- [Qwen3-4B](https://huggingface.co/Qwen/Qwen3-4B)
- [Llama-3.2-3B-Instruct](https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct)
- [Llama-3.1-8B-Instruct](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct)
- [Gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it)
- [Phi-3.5-mini-instruct](https://huggingface.co/microsoft/Phi-3.5-mini-instruct)

### Vendor blogs and announcements

- [Meta Llama 3.2 blog](https://ai.meta.com/blog/llama-3-2-connect-2024-vision-edge-mobile-devices/)
- [Qwen3 blog](https://qwenlm.github.io/blog/qwen3/)
- [Google Gemma 3 blog](https://blog.google/technology/developers/gemma-3/)
- [Alibaba Qwen2.5 Apsara announcement](https://www.alizila.com/alibaba-cloud-ai-qwen-full-stack-ai-infrastructure-2024-apsara-conference/)

### Vendor technical reports

- [Qwen3 Technical Report (arXiv 2505.09388)](https://arxiv.org/html/2505.09388v1)
- [Gemma 3 Technical Report (arXiv 2503.19786)](https://arxiv.org/html/2503.19786v1)
- [Qwen2.5 Technical Report (arXiv 2412.15115)](https://arxiv.org/pdf/2412.15115)
- [Llama 3.1 eval_details.md (Meta GitHub)](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/eval_details.md)
- [Llama 3.2 MODEL_CARD.md (Meta GitHub)](https://github.com/meta-llama/llama-models/blob/main/models/llama3_2/MODEL_CARD.md)

### Benchmarks and evaluation

- [Berkeley Function Calling Leaderboard (BFCL)](https://gorilla.cs.berkeley.edu/leaderboard.html)
- [BFCL paper (OpenReview)](https://openreview.net/forum?id=2GmDdhBdDk)
- [BFCL CHANGELOG](https://github.com/ShishirPatil/gorilla/blob/main/berkeley-function-call-leaderboard/CHANGELOG.md)
- [BFCL V4 Web Search blog](https://gorilla.cs.berkeley.edu/blogs/15_bfcl_v4_web_search.html)
- [Llama 3.1 BFCL 76.1 via FriendliAI](https://medium.com/friendliai/experience-meta-llama-3-1s-outstanding-performance-on-friendli-7fef3510f020)

### Quantization studies

- [llama.cpp quantize README (Q4_K_M perplexity table)](https://github.com/ggml-org/llama.cpp/blob/master/tools/quantize/README.md)
- [Red Hat half-million-eval study on quantized LLMs](https://developers.redhat.com/articles/2024/10/17/we-ran-over-half-million-evaluations-quantized-llms)
- [arXiv 2501.03035 on quantization and reasoning](https://arxiv.org/html/2501.03035v2)
- [LocalBench GGUF benchmark methodology](https://localbench.substack.com/p/gguf-benchmark-methodology)

### Multilingual / German evaluation

- [Occiglot EU tokenizer performance study](https://occiglot.eu/posts/eu_tokenizer_perfomance/)

### Community evidence (anecdotal)

- [vllm #9454: langchain function-call errors with Qwen2.5](https://github.com/vllm-project/vllm/issues/9454)
- [ollama #8588: Qwen not recognizing tools](https://github.com/ollama/ollama/issues/8588)
- [ollama #14745: Qwen prints tool call instead of executing](https://github.com/ollama/ollama/issues/14745)
- [continuedev #9639: Llama 3.1 Q4_K_M GGUF "model does not support tools"](https://github.com/continuedev/continue/issues/9639)
- [HF Phi-3.5-mini discussion #7: empty tool_calls](https://huggingface.co/microsoft/Phi-3.5-mini-instruct/discussions/7)

### Framework documentation

- [Qwen-Agent GitHub](https://github.com/QwenLM/Qwen-Agent)
- [Qwen function-calling docs](https://qwen.readthedocs.io/en/latest/framework/function_call.html)
- [Google AI Gemma function-calling docs](https://ai.google.dev/gemma/docs/capabilities/function-calling)

### Ollama library

- [qwen2.5:3b](https://ollama.com/library/qwen2.5:3b)
- [qwen2.5:7b](https://ollama.com/library/qwen2.5:7b)
- [llama3.2:3b](https://ollama.com/library/llama3.2:3b)
- [llama3.1:8b](https://ollama.com/library/llama3.1:8b)
- [qwen3:4b](https://ollama.com/library/qwen3:4b)
- [gemma3:4b](https://ollama.com/library/gemma3:4b)
- [phi3.5:3.8b](https://ollama.com/library/phi3.5:3.8b)
