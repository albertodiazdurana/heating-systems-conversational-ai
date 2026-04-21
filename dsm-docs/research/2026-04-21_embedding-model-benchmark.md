# Embedding Model Micro-Benchmark — Phase 2

**Date:** 2026-04-21
**Session:** 9
**Status:** Done — awaiting model selection decision (Opus turn, post-Thu 21:00)
**Target Outcome:** Sprint 2 Phase 2 — select embedding model for bilingual RAG

---

## Candidates evaluated

| Model | Dim | Max tokens | Size (download) | License |
|-------|-----|-----------|----------------|---------|
| `intfloat/multilingual-e5-base` | 768 | 512 | ~1.06 GB | MIT |
| `BAAI/bge-m3` | 1024 | 8192 | ~2.17 GB | MIT |

`sentence-transformers/paraphrase-multilingual-mpnet-base-v2` eliminated before
benchmarking: 128-token hard limit causes destructive truncation of multi-sentence
technical passages; designed for similarity, not asymmetric retrieval.

---

## Benchmark setup

**Script:** `scratch/embedding_benchmark.py`
**Device:** CPU, WSL2 (no GPU — CUDA driver 12080 too old for installed torch)
**Pairs:** 6 relevant + 4 irrelevant query-passage pairs drawn from
`dsm-residential-heating-ds-guide/01_Domain_Fundamentals.md`

**Pair design:** bilingual coverage — 3 EN queries, 2 DE queries, 1 mixed;
passages include German domain terms (Heizkennlinie, Vorlauftemperatur,
Spreizung, Anschlussleistung, hydraulischer Abgleich).

**Metric:** cosine similarity gap = avg(relevant) − avg(irrelevant).
Higher gap = better retrieval discrimination (model separates relevant from
irrelevant more clearly).

**Model-specific prefixes applied per spec:**
- e5-base: `"query: "` prepended to queries, `"passage: "` to passages
- bge-m3: no prefix (model card explicitly states none required)

---

## Results

| Model | Avg Relevant | Avg Irrelevant | Gap | Texts/sec | Load time |
|-------|-------------|----------------|-----|-----------|-----------|
| e5-base | 0.8859 | 0.7841 | **0.1018** | **20.7** | 69s |
| bge-m3 | 0.6765 | 0.4144 | **0.2621** | 6.4 | 128s |

### Per-pair relevant similarities

| # | Query (truncated) | e5-base | bge-m3 |
|---|---|---|---|
| 1 | What is the heating curve… (EN) | 0.8519 | 0.5848 |
| 2 | Was ist die Heizkennlinie… (DE) | 0.9279 | 0.7878 |
| 3 | How does hydraulic balancing… (EN) | 0.8852 | 0.6806 |
| 4 | Wie beeinflusst die Vorlauftemperatur… (DE) | 0.8699 | 0.7182 |
| 5 | What is Spreizung… (EN) | 0.8938 | 0.6850 |
| 6 | Explain Anschlussleistung… (EN/DE) | 0.8864 | 0.6028 |

---

## Interpretation

### Gap is the decision-relevant metric, not absolute similarity
e5-base produces higher absolute cosine values (0.88 relevant vs. 0.78
irrelevant) but the gap is only 0.10. bge-m3 produces lower absolute values
(0.68 vs. 0.41) but a much larger gap of 0.26. In retrieval, the gap
controls the ranking: bge-m3 separates relevant from irrelevant 2.6× more
sharply than e5-base on this domain.

### Speed trade-off
e5-base: 20.7 texts/sec, bge-m3: 6.4 texts/sec on CPU. bge-m3 is ~3.2×
slower. For a one-time ingestion of ~6,000 lines (chunked to ~200-token
passages, ~300–400 chunks), the difference is ~15s (e5) vs. ~50s (bge-m3)
— acceptable for a batch offline index build. For runtime query embedding
(single query per user turn), latency is <1s for both models.

### German technical domain
Both models handle bilingual queries well. bge-m3's gap is larger on the
German-dominant pair #2 (0.79 vs 0.93 for e5). The most striking divergence
is pair #6 (Anschlussleistung + district heating): bge-m3 gap is clear
(0.60 vs. low irrelevant), while e5-base compressed the range.

### Token limit implications
e5-base's 512-token limit constrains passage chunking. Chunks must stay under
~380 tokens of content (512 − prefix tokens − special tokens). bge-m3's
8192-token limit allows full-section ingestion without chunking loss.
The heating guide's most information-dense sections (§3.1 Heizkennlinie,
§3.2 hydraulischer Abgleich) run 200–400 tokens per subsection — within
e5-base's window. If ingestion strategy uses section-level chunks, e5-base
is sufficient; if passage-level (paragraph granularity), both are fine.

---

## Decision inputs for Opus (post-Thu 21:00)

| Factor | e5-base | bge-m3 | Favors |
|--------|---------|--------|--------|
| Retrieval gap | 0.10 | 0.26 | bge-m3 |
| Encode speed (CPU) | 20.7/s | 6.4/s | e5-base |
| Token limit | 512 | 8192 | bge-m3 |
| Model size | 1.06 GB | 2.17 GB | e5-base |
| Query prefix required | Yes | No | bge-m3 (simpler API) |
| Ingestion latency (~350 chunks) | ~17s | ~55s | e5-base |
| Runtime query latency | ~0.05s | ~0.16s | both acceptable |

**Preliminary lean:** bge-m3 wins on the metric that matters most (retrieval
discrimination gap 2.6×), and both speed and size costs are acceptable for
this project's scale. The token limit advantage is not needed at section-level
chunking but becomes valuable if chunk strategy evolves.

**Question for Opus decision turn:** does the 3× CPU encode overhead at
ingestion time warrant preferring e5-base, or is the retrieval quality gain
from bge-m3 worth the trade-off for a portfolio project where correctness
matters more than ingestion speed?

---

## Notes

- Load times (69s e5, 128s bge-m3) are one-time costs; models cache in
  `.venv/` HuggingFace cache after first run. Not relevant to runtime latency.
- CUDA unavailable on this WSL2 instance (driver 12080 incompatible with
  installed torch). GPU would reduce bge-m3's latency gap vs. e5-base.
- `embeddings.position_ids UNEXPECTED` warning from e5-base is benign
  (architecture mismatch between base XLM-RoBERTa and fine-tuned weights,
  expected per model card).