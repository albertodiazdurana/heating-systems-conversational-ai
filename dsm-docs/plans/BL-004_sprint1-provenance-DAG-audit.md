# BL-004: Complete Sprint 1 Provenance in dsm_provenance_DAG

**Status:** Open
**Priority:** Low
**Date Created:** 2026-04-22
**Origin:** Session 9 — dsm_provenance_DAG.md created with Sprint 2 fully mapped;
Sprint 1 provenance partially mapped due to Sprint 1 artifacts not being in active context.
**Author:** albertodiazdurana

---

## Problem

`dsm-docs/plans/dsm_provenance_DAG.md` was initialized in S9 with Sprint 2
fully mapped (all research, decisions, experiments, external resources, and
edges confirmed from active session context). Sprint 1's backbone node (SP1)
is connected only where Sprint 2 also references Sprint 1 artifacts (model
selection, orchestration decision, hybrid best practices).

The following Sprint 1 provenance is unconfirmed or missing:

1. **`RES_CONVO` → SP1 edge:** the file
   `dsm-docs/research/done/2026-04-06_sprint1_conversation_engine_research.md`
   is in the registry but its content was not read in S9. Confirm what it
   covers and whether there are additional edges (e.g., does it also feed the
   system prompt design?).

2. **Tool-specific research:** Sprint 1 delivered three deterministic tools
   (`unit_converter`, `standard_lookup`, `heating_curve`). Check whether any
   research files or design notes document the tool logic sources (particularly
   `heating_curve` which is based on DIN EN 12831 / VDI 6030). If so, add
   nodes and edges.

3. **Streamlit UI research:** Sprint 1 included a Streamlit chat UI. Check
   whether any research or design files exist for it.

4. **BL-003 (`SqliteSaver` asyncio fix):** this was a bug fix, not a design
   artifact, but it produced an empirical finding about `MemorySaver` vs
   `SqliteSaver`. Check whether the finding has edges into the Sprint 1 plan
   or the backbone plan.

5. **E2E backbone §1-3:** `dsm-docs/plans/2026-04-07_e2e_hybrid_backbone.md`
   is in the DAG as a node (BB) but only §4 is mapped as a Sprint 2 input.
   Confirm whether §1-3 have edges into Sprint 1.

---

## Tasks

- [ ] Read `dsm-docs/research/done/2026-04-06_sprint1_conversation_engine_research.md`
      and confirm or correct the RES_CONVO → SP1 edge description
- [ ] Read `dsm-docs/plans/2026-04-07_sprint1_langgraph_plan.md` (the full plan)
      and check the References section for any research files not yet in the DAG
- [ ] Read `dsm-docs/plans/2026-04-07_e2e_hybrid_backbone.md` §1-3
      and determine whether additional edges exist to SP1
- [ ] Check `dsm-docs/decisions/` for any decision files other than
      `2026-04-07_orchestration-framework.md`
- [ ] For each new node found: add to Node Registry + Mermaid + Edge Registry
      in `dsm-docs/plans/dsm_provenance_DAG.md`
- [ ] Update "Pending: Sprint 1 provenance gap" section once complete;
      remove or mark resolved

---

## Acceptance criteria

- Every file referenced in Sprint 1's plan or its research references is a
  node in `dsm_provenance_DAG.md`
- Every "feeds / validates / frames" relationship is an edge in the Edge Registry
- The Mermaid diagram is regenerated with the completed Sprint 1 nodes
- The "Pending" section is updated or removed