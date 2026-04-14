# BL-002 — Apply Sprint Plans Groundedness Assessment Edits

**Status:** Open
**Priority:** Medium (precedes Sprint 1 implementation resume beyond gate 1 Step 2)
**Date Created:** 2026-04-14
**Origin:** Follow-on to parallel session 4.1 (BL-001 + groundedness assessment)
**Input:** `dsm-docs/research/2026-04-14_sprint-plans-groundedness-assessment.md` §"Recommended plan edits"
**Intended execution:** Main session, short turn (plan-hygiene edits; no new research or code)
**Author:** albertodiazdurana (with Claude)

## Scope

Apply the six recommended edits from the groundedness assessment to Sprint 1 and backbone plans:

| # | File | Section | Edit | Effort |
|---|---|---|---|---|
| 1 | `dsm-docs/plans/2026-04-07_sprint1_langgraph_plan.md` | §6 exit criteria | Promote DE tool-call smoke query ("Berechne die Vorlauftemperatur bei -10°C mit Steigung 1.2") from informal smoke test to a gating exit criterion | 1 line |
| 2 | `dsm-docs/plans/2026-04-07_e2e_hybrid_backbone.md` + Sprint 2 plan | Sprint 2 §MUST | Add Gate-1 embedding-model micro-benchmark (e5-base vs bge-m3 vs mpnet on 5-10 EN/DE heating queries) | 1 paragraph |
| 3 | `dsm-docs/plans/2026-04-07_e2e_hybrid_backbone.md` | §2 stack table | Add one-sentence Chroma rationale (zero-ops local persistence; one-component swap to Qdrant/Weaviate if scale demands) | 1 line |
| 4 | `dsm-docs/plans/2026-04-07_sprint1_langgraph_plan.md` | §5.4 + test list (§3) | Mark error-handling as assumed-pending-verification; add `test_tool_error_handling` to the test file list | 2 lines + 1 test item |
| 5 | `dsm-docs/plans/2026-04-07_e2e_hybrid_backbone.md` (Sprint 2 scope) | Sprint 2 Gate 1 | Add deliberate monolithic-vs-specialized RAG tool choice (a/b/c options) with coherence cross-reference to Sprint 1 §5.1 | 1 paragraph |
| 6 | `dsm-docs/plans/2026-04-07_e2e_hybrid_backbone.md` + Sprint 2 plan | WON'T lists | Make reranker deferral explicit (deliberate scope choice, one-component addition tracked as Sprint 3 stretch) | 1 line each |

## Out of scope

- Executing the embedding-model micro-benchmark (edit 2 adds the task to Sprint 2; the benchmark itself is Sprint 2 work, not this BL)
- Resolving the monolithic-vs-specialized RAG tool choice (edit 5 adds the gate decision to Sprint 2; the decision itself is Sprint 2 Gate 1, not this BL)
- Changes to `dsm-docs/decisions/2026-04-07_orchestration-framework.md` (assessment explicitly says decision stands)
- Changes to Sprint 1 agent-construction steps (Sprint 1 is already mid-gate-1; non-plan changes happen in code, not in plan docs)

## Exit criteria

- Six edits applied across the sprint 1 and backbone plan files
- No change to orchestration decision record
- Sprint 1 and backbone plans remain internally coherent and cross-reference each other where relevant
- BL status updated to Implemented / Date Completed set
- This BL moved to `dsm-docs/plans/done/`

## Execution order (suggested)

Hygiene edits first (fast, low-risk, each a single line or two):
- Edit 1 (Sprint 1 §6 DE tool-call gating)
- Edit 3 (backbone §2 Chroma rationale)
- Edit 4 (Sprint 1 §5.4 error-handling marker + test list item)
- Edit 6 (backbone + Sprint 2 WON'T reranker line)

Then the two substantive edits (each adds a paragraph):
- Edit 2 (Sprint 2 §MUST embedding-model benchmark)
- Edit 5 (Sprint 2 Gate 1 monolithic-vs-specialized RAG tool decision)

Final verification pass: re-read both plans end-to-end to confirm coherence.

## Notes

- "Sprint 2 plan" does not yet exist as a separate file; the backbone plan currently carries Sprint 2 scope. Where the edit table says "Sprint 2 plan" the edit target is the Sprint 2 sections inside `2026-04-07_e2e_hybrid_backbone.md` unless a separate Sprint 2 plan file is written first (not required for this BL).
- Edit 1 (DE tool-call gating) overlaps with the user's reinforcement at end of session-4 ("smoke test §11 should explicitly include a DE tool-call test as a gating exit criterion"). Both refer to the same change.

## References

- `dsm-docs/research/2026-04-14_sprint-plans-groundedness-assessment.md` — source of the six edits
- `dsm-docs/research/2026-04-14_hybrid-architecture-precedents.md` — source of edits 5 and 6
- `dsm-docs/plans/BL-001_hybrid-agent-rag-architecture-precedents.md` — parent BL
