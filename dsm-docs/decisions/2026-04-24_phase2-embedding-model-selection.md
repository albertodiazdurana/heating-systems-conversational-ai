# Phase 2 Embedding Model Selection — Decision

**Date:** 2026-04-24
**Session:** 10
**Phase:** Sprint 2 Phase 2
**Status:** Decided

## Context

Sprint 2 Phase 2 required a Gate 1 decision between benchmarked multilingual
embedding models for the heating-guide RAG subsystem. Full benchmark methodology
and results at `dsm-docs/research/2026-04-21_embedding-model-benchmark.md`.

## Decision

**Selected:** `BAAI/bge-m3`.

## Rationale

Retrieval discrimination gap (avg relevant − avg irrelevant cosine similarity)
is 0.26 for bge-m3 vs 0.10 for e5-base on the 6 EN/DE heating-domain
query-passage pairs. The gap metric, not absolute similarity, controls top-k
ranking in retrieval; bge-m3 separates relevant from irrelevant 2.6× more
sharply. Speed (3.2× slower CPU encoding) and download size (2.17 GB vs 1.06
GB) costs are acceptable at portfolio scale: ingestion is a one-time batch
(~55s for the ~350-chunk corpus), and runtime per-query embedding stays under
0.2s.

## Consequences

- **backbone §2 (tech-stack contract):** embeddings row updated from
  `intfloat/multilingual-e5-base` to `BAAI/bge-m3`.
- **backbone §4 (Sprint 2 MUST pipeline spec):** pipeline-step annotation
  updated.
- **backbone Bilingual handling paragraph:** "e5" reference updated.
- **pyproject.toml:** no change required. Both candidates run through
  `sentence-transformers>=5.4.1`, already pinned. The sprint plan's "locked
  into pyproject.toml" line is satisfied vacuously; the functional model lock
  lives in Phase 3 ingestion code (`src/rag/ingest.py`) via the model
  identifier string.
- **Phase 3 ingestion:** chunk budget is bounded by bge-m3's 8192-token limit,
  practically constrained by retrieval signal quality; chunking strategy
  decided at Phase 3 Gate 1.
- **Query prefix:** bge-m3 requires no prefix convention (e5-base's
  `"query: "` / `"passage: "` is not needed). One less API hazard in the
  ingestion and retrieval pipelines.

## Evidence summary

| Factor | e5-base | bge-m3 | Favors |
|---|---|---|---|
| Retrieval gap | 0.10 | 0.26 | bge-m3 |
| CPU encode speed | 20.7 texts/sec | 6.4 texts/sec | e5-base |
| Token limit | 512 | 8192 | bge-m3 |

Full table at benchmark doc §Decision inputs.

## Strongest counter-evidence (per DSM_0.2 §8.2.1)

Sources surveyed: benchmark doc §Results and §Speed trade-off; Session 5
methodology lesson 1 (tutorial-default convenience trail); Sprint 2 plan
Research Assessment row 2; bge-m3 and e5-base model cards.

- **CE1, absolute cosine similarity favors e5-base.** e5-base relevant avg
  0.8859 vs bge-m3 0.6765 (benchmark §Results). Higher absolute scores make
  threshold tuning more intuitive on first pass.
  *Why bge-m3 still wins:* retrieval ranks by relative score within a query's
  candidate set. The gap, not the ceiling, determines top-k vs noise;
  `RAG_SCORE_THRESHOLD` tuning is easier on a wider gap than a higher ceiling.

- **CE2, e5-base is 3.2× faster on CPU (20.7 vs 6.4 texts/sec).** WSL2 has no
  CUDA on this machine; ingestion and runtime both pay the speed penalty
  (benchmark §Speed trade-off).
  *Why bge-m3 still wins:* ingestion is a one-time ~55s batch per full
  reindex; per-query runtime stays under 0.2s, well inside conversational
  latency budget. The ingestion delta is paid once per reindex; the
  retrieval-quality gain is paid every query.

Download size (2.17 GB vs 1.06 GB) and the absence of e5-style prefix
ergonomics were surveyed and rejected as primary counter-evidence: size is
one-time and cache-absorbed; the absent prefix requirement on bge-m3 is an
ergonomic advantage, not a disadvantage.

## Open items rolled forward to Phase 3 Gate 1

- Chunking strategy (section-level vs paragraph-level vs header-aware hybrid),
  bge-m3's 8192-token ceiling opens but does not mandate larger chunks.
- `EMBEDDING_MODEL` constant location (`src/config.py` vs new
  `src/rag/constants.py`), decided when the ingestion module lands.
- `RAG_SCORE_THRESHOLD` default, benchmarked at retrieval time in Phase 4,
  not pre-committed here.

## References

- Benchmark: `dsm-docs/research/2026-04-21_embedding-model-benchmark.md`
- Sprint plan: `dsm-docs/plans/2026-04-18_sprint2_rag_haystack_plan.md` Phase 2
- Backbone: `dsm-docs/plans/2026-04-07_e2e_hybrid_backbone.md` §2
- Methodology guard: DSM_0.2 §8.2.1 counter-evidence surfacing (BL-385)
- Config-gate guard: DSM_0.2 §8.7 token-minimizing config recommendation
  (BL-402), applied as skip-by-match (demand = baseline)