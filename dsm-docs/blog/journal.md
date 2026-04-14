# Blog Journal

Append-only capture file for blog-worthy observations. Entries accumulate
across sessions and are extracted into materials files at project/epoch end.
Reference: DSM_0.1 Blog Artifacts (three-document pipeline).

## Entry Template

### [YYYY-MM-DD] {Title}
{Observation, story, pattern, or insight}

### [2026-04-14] When the spike IS the contribution pipeline

Back in Session 3 we landed on a hybrid LangGraph + Haystack architecture and
flagged a docs-PR opportunity on Haystack's `OllamaChatGenerator`, the source
accepts `tools=[...]` but the marketing docs do not mention it. Before drafting
anything upstream I asked `dsm-graph-explorer` for a contribution playbook,
since they had just navigated a similar "undocumented behavior in a beta
upstream" situation with FalkorDBLite.

Their response reframed something I had been treating as two separate tracks,
the Sprint 2 Haystack spike and the upstream contribution, as one pipeline:

1. **The spike is a capability experiment.** Its primary output is a pass/fail
   decision for our project (does `OllamaChatGenerator(tools=...)` actually
   work end-to-end with qwen2.5). That is the delivery job.
2. **The gap list is a side effect.** Anything we had to discover empirically
   that is not in the docs becomes a candidate contribution, no extra
   experiment needed. The experiment script plus a short deep-dive note
   become the evidence base.
3. **Issue before PR, especially for low-response-rate projects.** GE's
   FalkorDBLite issue has been open a month with no maintainer reply. If they
   had built the PR first, that month would have been sunk cost. For us,
   Haystack is more active so responsiveness should be better, but the
   heuristic stands: gauge interest before investing in a PR.
4. **"Broken" vs "undocumented" is a useful split.** If correct usage is not
   documented, that is a docs gap (contributable as docs). If the tool fails
   regardless of usage, that is a bug (contributable as an issue, or a patch
   if scoped). FalkorDBLite's editable-install gap sits right on the line and
   they left the call to the maintainer, which is the right move.

The second-order lesson is about DSM: this is the same "capability experiment
as contribution pipeline" pattern a second time, first in graph-explorer, now
about to happen here. Two data points is not yet a pattern to promote into
DSM core, but it is worth naming locally and watching for a third instance.

Captured as a method reference in
`dsm-docs/research/2026-04-14_upstream-contribution-playbook.md` for Sprint 2
pickup.
