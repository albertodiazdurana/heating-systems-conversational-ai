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

### [2026-05-01] Halt, then diagnose: what 0.75 vs 0.83 hid

<!--
DRAFT — first pass. Alternate titles to consider:
  - EXP-001 missed the threshold and that was the data
  - Reading the source after running the spike
-->

Sprint 2's closing experiment was EXP-001, a hit@5 retrieval evaluation
on a 12-query bilingual testset. The exit threshold was 0.80. First run:
0.75. Three misses out of twelve.

The plan had a §37 escalation rule wired in for exactly this case:
promote reranking from Sprint 3 stretch into Sprint 2 MUST. I reached
for it. Then I stopped, because the rule says escalate, but it does not
say which evidence justifies which escalation, and I had not yet looked
at the misses.

Reading the three failures: q04 was a cross-lingual abbreviation in
German that no reranker would obviously help with; q10 returned only
"intro" chunks for a chapter because every section's intro chunk is
high-recall by construction and crowded out the specific section
("14.4 Model Monitoring") the query actually wanted; q11 had been
tagged wrong in the testset, the "expected" doc was a near-paraphrase
of an also-correct doc that the retriever was returning. Two of
three had non-retrieval root causes. One was a chunking-policy
artifact, one was a labeling error.

Two targeted fixes landed before any escalation: B1, a retrieval-time
`exclude_intro=True` filter that owns the policy at the consuming
layer rather than rewriting the chunking step; B2, an
`accept_alternatives` field on the testset schema so paraphrase
doc-ids count as correct. Re-ran. 0.83. PASS, but only one of the
three first-run misses (q11) was fully resolved; q10 traded
intro-dominance for a residual chunking-granularity issue (14.4 is
short and gets outscored by neighbors), and q04 stayed broken. The
threshold passed because we changed the gate's interpretation of q11,
not because retrieval got fundamentally better.

Reranking stayed in Sprint 3 stretch. The two remaining misses (q04
cross-lingual, q10 chunking granularity) are now the citation if
Sprint 3 prioritizes it, because reranking is a real candidate for
*those* failure modes specifically. It was never a candidate for the
labeling error.

The first-order lesson is that plan-prescribed escalations are
contracts, not reflexes. The escalation rule existed so I would not
quietly fix-and-proceed past a missed threshold. The *halt* part of
the rule is what mattered, not the *promote reranking* part. Once
halted, the right next step is diagnose-then-decide, not
escalate-then-explain.

The second-order lesson is that the S9 rule "read §6 exit criteria
strictly, not pragmatically" held under live pressure. Strict reading
creates the halt. The halt creates the diagnosis window. The
diagnosis exposes whether escalation is genuinely needed or whether a
targeted fix is sufficient. Without the strict read, B1 and B2 would
have shipped as adjustments after a quiet pass; with it, they shipped
as documented gate decisions.

The reading-habit takeaway: when an empirical result misses a gate, I
want to read the failure cases in their full text before letting any
plan-side machinery fire. The plan is a useful constraint and a
useful prompt, but it cannot diagnose. Three failures in a small
testset is twelve minutes of reading, and twelve minutes is enough to
change which escalation is correct, or whether one is needed at all.

### [2026-05-08] Investigation-first: how a code gap became a docs gap

@anakin87 wrote "Thank you!" and merged at 07:57:58 UTC on 2026-05-08
(merge commit `9e0798aa`). Six days from issue file (2026-05-02) to
merge: a small docs PR, but the path it took says more about how to
contribute than the patch itself.

The lifecycle, as I experienced it. Filed
`deepset-ai/haystack-core-integrations#3263` describing what I thought
was a missing streaming-with-tools capability in Haystack's Ollama
chat generator. Three days later a maintainer responded; a couple of
volunteers offered to take the work. I declined the volunteer offers
and kept the contribution. Two PRs followed,
`deepset-ai/haystack-integrations#473` (the landing-page tool-calling
example) and `deepset-ai/haystack#11268` (the
`OllamaChatGenerator` reference section). One upstream issue,
`ollama/ollama-python#663`, peeled off because it belonged in
ollama-python, not in Haystack. Today PR #11268 merged; #473 and
ollama-python#663 are still open.

What changed during contribution. The original framing was "Haystack
is missing a feature." Reading
`haystack-core-integrations/integrations/ollama/.../chat_generator.py`
end-to-end, about 697 lines, showed the capability already worked at
runtime; what was missing was the example that lets a reader know
that. The "missing feature" collapsed into a missing documentation
section. The second reframe came when I drafted the issue body and
ran the example before filing: a plausible-looking
`Tool.from_function` call (taken from a memory of older docs) raised
on import, the real symbol is `create_tool_from_function`. Catching
that pre-flight took two minutes; filing it would have cost a public
correction. PR discipline followed the same shape, one example per
PR, deferred follow-ups (multi-tool variants, async, non-chat
generator coverage) kept out of scope. A separate Definition-of-Ready
audit, prompted by an end-of-session question, caught a missing
release note and an untemplated PR body before the maintainer's first
read.

Three repos, three reviewer dynamics. haystack-integrations#473 sits
quiet, no review yet. haystack#11268 saw an engaged maintainer who
left targeted review comments (remove the release note for a docs
change, drop a redundant tip section, copy the new section to the
2.28 versioned docs) and merged about a day later when I had
addressed them. ollama-python#663 stays open with no comments, as
expected for an upstream feature request without a sponsor. The same
contribution touched three review styles, three fork ergonomics,
three response cadences, and the only way to know which is which is
to be in all three at once.

Investigation-first, as credibility. Both of the reframes above came
from reading, not from speculation. The "code gap" became a "docs
gap" because the chat-generator source was already wired for tools
and streaming; the "Haystack PR" became an upstream issue because
`tool_choice` is a request-shape ollama-python doesn't currently
forward, not a Haystack-level omission. Filing either contribution
against the wrong target would have been wasted maintainer attention.
Filing both against the right target turned a one-line idea into a
small, well-scoped pipeline.

What I'd take into the next contribution. The artifact that matters
is the investigation, not the patch. The patch is small,
~50 lines of docs, ~10 minutes to write. The investigation, reading
the chat-generator source, running the example pre-flight, drafting
and verifying the behavioral claim against six adversarial prompts,
is what makes the patch land cleanly in six days instead of bouncing
through review for two weeks.
