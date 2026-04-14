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

### [2026-04-14] The pattern is in the tutorials, not in the papers

BL-001 asked whether anyone had published about the hybrid "agent framework +
RAG framework, one tool-call boundary" architecture we chose on 2026-04-07.
The strict-lens search returned four credible precedents: a 2025 Packt book
(Funderburk, Haystack 2.0 + LangGraph 1.0), a 2026 Medium enterprise guide
(Panta, LlamaIndex + LangGraph + LangChain) with code that is nearly
isomorphic to what we will write in Sprint 2, a multi-agent pattern post
(scrapegraphai, three-framework stack), and LlamaIndex's `QueryEngineTool`
primitive. So the pattern is not novel.

What surprised me is the shape of the gap. Four tutorial-level precedents,
zero arXiv papers, zero deepset or LangChain official-blog reference
architectures, zero named conference talks. The pattern propagates through
books, Medium posts, and YouTube-style tutorials but has no institutional
canonization. Every framework's marketing site pitches itself as complete:
Haystack ships an `Agent` component, LangGraph has Corrective RAG recipes,
LlamaIndex has its own agents. Cross-framework composition is anti-marketing
for each of them individually, so no vendor has an incentive to write the
reference piece.

This has two implications. First, our architecture is conventional among
practitioners even though it looks opinionated from any single framework's
documentation. Second, a worked "Haystack pipeline as LangGraph tool" doc in
deepset's tutorials or on their blog would be a defensible contribution
because that exact combination is not covered officially, even though the
Packt book covers it in paid chapters. That is a contribution shape (docs,
not code, not issue) to revisit in Sprint 2 or later.

The underlying lesson for my own reading habits: when assessing whether a
chosen architecture is idiosyncratic, searching framework vendor blogs
produces a biased null result, because vendors under-publish compositions
that de-center their product. Tutorial content and books are the honest
signal.
