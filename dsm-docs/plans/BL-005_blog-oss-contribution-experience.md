# BL-005: Blog post on OSS contribution & Take-AI-Bite experience

**Status:** Proposed (deferred, trigger-driven)
**Priority:** Low (until trigger fires)
**Date Created:** 2026-05-05
**Origin:** S13 user request after PR #11268 opened
**Author:** Alberto Diaz-Durana (with AI assistance)

---

## Trigger

Activate this BL only when ONE of the following events fires. Until then, do not draft.

- `deepset-ai/haystack-integrations#473` (Tool Calling on Ollama landing page) gets merged.
- `deepset-ai/haystack#11268` (Streaming with Tools on OllamaChatGenerator reference) gets merged.
- (Lower-priority trigger) `ollama/ollama-python#663` (tool_choice upstream feature request) gets a maintainer response or labeled action.

## Problem Statement

The S13 OSS contribution chain (issue #3263 → PR #473 → PR #11268 → upstream issue #663) is the user's first hands-on round trip through the OSS contribution lifecycle inside the Take-AI-Bite workflow. The narrative is portfolio-relevant and methodologically interesting, but is only worth telling once a PR actually lands; an unmerged-PR blog post would be premature.

## Proposed Solution

When the trigger fires, draft a blog journal entry (or, if scope warrants, a longer post) capturing the user's first-person impressions on:

- **The OSS contribution lifecycle as experienced.** Issue filed, maintainer response in 4 days, two unsolicited volunteers offering to take the PR, the issue author's first-refusal call, the volunteer-acknowledgment etiquette without redirecting newly-discovered scope.
- **The role of Take-AI-Bite in shaping the contribution.** Research-driven scoping (read the source, not just the docs), empirical pre-flight (issue drafts must run before filing, two errors caught), maintained PR discipline (single example per PR, deferred follow-ups, no scope-creep).
- **Multi-repo ecosystem reality.** Same contribution touched three repos (`haystack-integrations`, `haystack`, `ollama-python`); each had a different reviewer dynamic, fork ergonomics, and review cadence.
- **Investigation-first credibility.** Reading `chat_generator.py` (697 lines) showed the streaming-with-tools "gap" was already supported in code; what looked like a code feature request collapsed into a documentation gap. The same investigation flipped tool_choice from "Haystack PR" to "ollama-python upstream issue."

## Success Criteria

- [ ] Trigger has fired (≥1 PR merged).
- [ ] Entry drafted, reviewed by user, landed in `dsm-docs/blog/journal.md` (or as a standalone post if scope warrants).
- [ ] Voice matches existing journal entries (lesson-flavored, narrative, ~30-80 lines).
- [ ] Concrete artifact references included (PR numbers, issue numbers, commit SHAs of the merged PR, the spike script).

## Inputs Available When Triggered

Snapshot when this BL fires (most are stable; PR/issue thread snapshots may evolve):

- Issue thread `deepset-ai/haystack-core-integrations#3263` (4 comments at time of BL creation)
- PR `deepset-ai/haystack-integrations#473` and PR `deepset-ai/haystack#11268`
- Upstream issue `ollama/ollama-python#663`
- `scripts/spike_streaming_with_tools.py` and `dsm-docs/handoffs/2026-05-05_s13_streaming_with_tools_spike.md` (empirical evidence base)
- Reasoning lessons: S5 "issue-before-PR / read-the-source," S12 "pre-flight verification before filing," S12 "auto-mode does not collapse cross-scope gates," S12 "cross-repo target rescope re-triggers per target"
- S13 session transcript

## Test Plan

- [ ] Voice matches existing entries (no marketing tone, no AI-vocabulary tells; pass through `/humanizer` if needed).
- [ ] No volunteer @-mentions in the public post (consistent with the S13 etiquette decision).
- [ ] No leakage of session-discovered adjacent items (async streaming-with-tools, multi-tool patterns, OllamaGenerator coverage) — these remain user IP unless explicitly chosen for follow-up work.
- [ ] Date convention follows existing `### [YYYY-MM-DD] {Title}` shape in `dsm-docs/blog/journal.md`.

## Revert Procedure

Not applicable; deliverable is a single addition to `dsm-docs/blog/journal.md`. Standard `git revert` if needed.

---

**Author:** Alberto Diaz-Durana (with AI assistance)
