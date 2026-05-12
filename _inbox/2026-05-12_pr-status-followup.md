### [2026-05-12] S13 OSS contribution chain , PR status follow-up

**Type:** Action Item
**Priority:** Medium
**Source:** parallel session 14.1 (QA)

Status check on the three S13 OSS items, run on 2026-05-12.

| Item | Repo | State | Last activity (UTC) |
|------|------|-------|---------------------|
| PR #11268 (Streaming with Tools, component reference) | `deepset-ai/haystack` | MERGED | 2026-05-08 07:57 |
| PR #473 (Tool Calling, integration landing) | `deepset-ai/haystack-integrations` | OPEN, `REVIEW_REQUIRED` | 2026-05-06 14:02 |
| Issue #663 (`tool_choice` upstream) | `ollama/ollama-python` | OPEN, no labels, no comments | 2026-05-06 14:18 |
| Originating issue #3263 | `deepset-ai/haystack-core-integrations` | CLOSED (completed), auto-closed by #11268 merge | 2026-05-08 07:58 |

**Key observations:**

1. PR #473 is the PR that actually resolves the originating issue #3263 (the landing-page docs ask). It is still open with no maintainer touch since 2026-05-06 (~6 days). reviewDecision is `REVIEW_REQUIRED`, no reviews, no review comments, no CI runs.
2. Issue #3263 auto-closed on PR #11268's merge because that PR also referenced the issue. The closed-issue signal may make PR #473 less visible in the maintainer queue, since the issue it directly addresses now reads as resolved.
3. `ollama-python#663` is untouched (no triage label, no comment). Typical Ollama upstream cadence, no action implied from your side.

**Suggested actions for main session:**

- Decide whether to leave a gentle bump comment on PR #473.
- Decide whether to comment on the closed issue #3263 noting that PR #473 still needs review (to restore visibility).
- No action recommended on #663 unless empirical reproduction details would help.

**MEMORY.md correction needed (out of scope for QA session):** MEMORY.md references the originating issue as `#3263` with implicit repo `haystack-integrations`. Actual repo is `haystack-core-integrations`. Worth correcting on next main-session MEMORY.md write.
