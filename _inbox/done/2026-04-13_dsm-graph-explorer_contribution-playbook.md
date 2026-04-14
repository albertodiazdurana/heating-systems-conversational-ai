### [2026-04-13] dsm-graph-explorer: Open Source Contribution Playbook

**Type:** Knowledge Transfer
**Priority:** Medium
**Source:** dsm-graph-explorer (DSM spoke)
**In response to:** 2026-04-07 playbook request

---

## Context

GE's contribution experience comes from FalkorDBLite, a lightweight graph
database we adopted in Sprint 9 (Epoch 3). Our capability experiment EXP-005
and a deep-dive research phase uncovered 5 documentation gaps in the upstream
project. Issue #85 is open on GitHub; PR is pending maintainer response.

**Caveat:** This contribution is still in progress. The issue is open but we
have not yet received maintainer feedback or submitted a PR. Take the playbook
as "what we did and why," not as a validated end-to-end success story.

---

## Answers to Your Questions

### 1. Which tool, what gap?

**FalkorDBLite** (Python graph database, BSD license, beta).

Five documentation gaps found:

1. **Import path confusion** — Package is `falkordblite`, but the import is
   `from redislite.falkordb_client import FalkorDB`. Heritage from
   RedisLite/RedisGraph lineage, not documented anywhere.
2. **Testing patterns** — Session-scoped DB fixture + per-test graph isolation
   via UUID naming + `g.delete()` cleanup. We validated across 18+ tests;
   official docs have no testing guidance.
3. **Complete working example** — Graph creation, parameterized queries,
   persistence, multi-graph isolation, and index creation in a single script.
4. **Editable installs** — `pip install -e .` fails silently, only
   `pip install .` works. Not documented.
5. **Python 3.12+ requirement** — Not prominently documented. Catches users
   upgrading from 3.10/3.11.

### 2. Playbook: undocumented behavior → upstream contribution

Our sequence:

1. **Experiment first** — EXP-005 was a capability experiment (DSM 4.0 Section
   4) to validate FalkorDBLite for our use case. The experiment was not
   designed to find documentation gaps; it found them as a side effect.
2. **Deep-dive research** — After the experiment, we wrote a comprehensive
   research document (`epoch-3-falkordblite-deep-dive.md`) covering
   installation, API, Cypher subset, persistence, testing, and limitations.
   This is where the gaps became systematic rather than anecdotal.
3. **Gap identification** — Compared our research findings against the
   official docs. Anything we had to discover empirically that was not in the
   docs was a candidate gap.
4. **Issue first, PR later** — Opened GitHub issue #85 listing all 5 gaps
   with specific suggestions. Rationale: gauge maintainer responsiveness
   before investing time in a PR. A non-responsive maintainer means the PR
   effort may be wasted.
5. **Blog capture** — Documented the narrative ("when your experiment becomes
   upstream documentation") in the blog journal for later extraction.

**How we decided what was worth contributing vs keeping local:**

If the gap would catch the next user who tries the same thing, it is worth
contributing. All 5 of our gaps met this bar. Local workarounds (like our
specific fixture patterns) are not upstream material, but the *existence* of
the need for fixtures is.

**How we separated "broken" from "undocumented":**

If the tool works when you use it correctly but the correct usage is not
documented, that is a docs gap. If the tool fails regardless of usage, that
is a bug. Gap #4 (editable installs) is borderline: it is arguably a build
system bug, but at minimum the limitation should be documented. We listed it
as a documentation gap and left the "bug or design choice" determination to
the maintainers.

### 3. Maintainer interaction

- **Issue opened:** Session 34 (2026-03-13)
- **Response as of today:** None yet (1 month)
- **Strategy:** We went issue-first. For a beta project with low activity,
  this is lower-risk than a surprise PR. If the maintainer responds
  positively, we will submit a documentation PR. If no response after
  ~2 months, we may submit the PR anyway (merged or not, it is publicly
  visible as a reference).
- **Pattern that works:** Specific, actionable suggestions rather than vague
  "docs need improvement." Each gap in our issue includes what we expected,
  what we found, and what the docs should say.

### 4. Reusable artifacts

All of these are in the dsm-graph-explorer repo:

| Artifact | Path | What it is |
|----------|------|------------|
| Deep-dive research | `dsm-docs/research/epoch-3-falkordblite-deep-dive.md` | Comprehensive technical reference |
| Capability experiment | `data/experiments/exp005_falkordb_integration.py` | Runnable validation script |
| Blog journal entry | `dsm-docs/blog/epoch-3/journal.md` (search "Contribution-Ready") | Narrative + 5 gaps listed |
| Decision record | `dsm-docs/decisions/DEC-006-graph-database-selection.md` | Why we chose FalkorDBLite |

No formal checklist or template yet. If the contribution completes
successfully, we plan to write one as part of the blog deliverable.

### 5. DSM alignment

The pattern is **capability experiment as contribution pipeline**:

- DSM 4.0 Section 4 defines capability experiments as validation of external
  tools/APIs for project use. The experiment's primary output is a pass/fail
  decision for the project.
- The secondary output, when the tool has documentation gaps, is a
  contribution opportunity. The experiment script + research doc become the
  evidence base for an upstream issue or PR.
- This is not formalized in DSM_0.2 yet. If your Haystack contribution
  succeeds, writing it back to DSM Central as a pattern ("experiment →
  research → upstream contribution") would be valuable. GE's experience would
  be the second data point.

---

## Recommendation for Your Haystack Spike

Based on our experience:

1. Run the spike as a capability experiment first. Document what works and
   what does not, systematically.
2. If `OllamaChatGenerator` supports `tools=[...]` in practice but the docs
   do not mention it: that is a documentation gap, same pattern as ours.
3. If it does not work: that is a feature gap or bug. Open an issue with your
   repro case.
4. Either way, open an issue before a PR. Haystack is a larger, more active
   project than FalkorDBLite, so maintainer responsiveness should be better.
5. Your decision record + spike results become the evidence base, just as our
   deep-dive + EXP-005 did.

Good luck with Sprint 2.