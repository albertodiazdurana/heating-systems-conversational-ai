# Session 12 Checkpoint
**Date:** 2026-05-01
**Branch:** sprint-2/rag-pipeline (pre sprint-merge)
**Last commit:** a4f33a0 Sprint 2 Phase 5: EXP-001 retrieval evaluation + Haystack issue + boundary test

## Work completed this session
Sprint 2 closed. Phase 4 retrieval pipeline + `rag_search` hybrid tool (`01e92c7`). Phase 5 EXP-001 evaluation (hit@5 = 0.83 after B1+B2 targeted fixes from a 0.75 first run), Haystack issue #3263 filed with two pre-flight corrections, boundary test, decision record (`a4f33a0`). Cross-spoke inbox notifications to DSM Central and haystack-magic. Reasoning lessons +6 entries (S12 section).

## Pending next session
- **Sprint 3 kickoff:** sprint plan exists in `_reference/sprint-plan.md`; needs formalization into `dsm-docs/plans/` per the planning-pipeline rule. Sprint 3 scope per `_reference/`: evaluation framework + production polish.
- **Reranking decision input:** if Sprint 3 prioritizes reranking, cite the two EXP-001 remaining misses captured in `dsm-docs/decisions/2026-05-01_haystack-contribution-and-tool-shape.md` (q04 cross-lingual abbreviation, q10 chunking granularity).
- **Haystack issue #3263 follow-up:** monitor for maintainer response; per GE playbook the PR is deferred until response. Time-box ~2 weeks.
- **README §2 stale fix** (`pip install -e .` → `uv sync`): carried from S11; appropriate point is now Sprint 2 close PR or Sprint 3 opening commit.
- **`.venv.old-rc1/` cleanup:** safe to delete (S9 confirmed clean), trivial when convenient.
- **Spoke actions carryover from `/dsm-align` v1.6.x–v1.8.0:** see `.claude/last-align-report.md` (S10/S11 surfaces).

## Open branches
- `sprint-2/rag-pipeline` — closes this session via PR merge to `main` in `/dsm-wrap-up` Step 10. After merge, no Level-3 branches remain open.
