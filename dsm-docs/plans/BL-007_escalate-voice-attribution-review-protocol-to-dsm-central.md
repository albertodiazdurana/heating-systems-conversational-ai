# BL-007: Escalate the Voice-Attribution Review protocol to DSM Central

**Status:** In progress (S14 — feedback file drafted at `dsm-docs/feedback-to-dsm/2026-05-07_s14_voice-attribution-review-protocol.md`, queued for /dsm-wrap-up Step 6 push)
**Priority:** Medium
**Date Created:** 2026-05-07
**Origin:** S14 PR #11268 review-fix incident, user direction after agent posted PR comment without separate body-approval gate
**Author:** Alberto Diaz-Durana (with AI assistance)

---

## Trigger

Active immediately. Drafted and queued for push in S14.

## Problem Statement

Outbound communication drafted by the agent but attributed to the user falls into two mechanism classes with asymmetric review-gate coverage:

1. **File-write-mediated content** (commit messages, inbox notifications, feedback files, reasoning-lesson entries). The Edit / Write tool's permission window is the existing review gate. If the user inspects the diff, they see the words before the file lands. Failure mode: the user approves the file write while skipping a careful read of the words.
2. **Network-mediated content** (`gh pr comment`, `gh issue comment`, `gh api`, future Slack / email / DM tooling). The Bash tool's permission window asks the user to approve the command, but the comment body lives inside the command argument and is easy to skim past. There is no diff window. Failure mode: the user approves the action and the words go out unread.

S14 surfaced a concrete instance. PR `deepset-ai/haystack#11268` review-fix work gated every file edit in `/tmp/haystack-fork` one-at-a-time with concrete diffs surfaced and approved before the Edit ran. The PR comment at the end was bundled into a multi-step "Op 5: commit + push + PR comment" plan; the comment text was visible in the prior brief, but `Authorize Op 5` covered all three sub-steps as a unit. The comment posted to a public OSS thread under the user's GitHub byline before any second-pass review of the words.

User surfaced the gap: comments on public OSS threads are *the user's words*, not the agent's. The agent drafts; the user owns the byline. The current Cross-Repo Write Safety rule's wording is path-centric and easy to misread as filesystem-only, missing the network-mediated case entirely.

## Proposed Solution

See `dsm-docs/feedback-to-dsm/2026-05-07_s14_voice-attribution-review-protocol.md` for the full proposal. Summary:

1. **Voice-Attribution Review gate (mechanism-aware).** New gate in the Pre-Generation Brief sequence; enforcement differs by mechanism (file-write-mediated vs network-mediated).
2. **Two-pass rule for file-write-mediated content.** Surface text in conversation BEFORE the tool call, in addition to the diff window. "Review the words, not just the action."
3. **Explicit content gate for network-mediated content.** Surface the full body, await explicit body-approval, then run the network call. Separate from action approval.
4. **Bundling rule.** Multi-step plans must NOT include voice-attributed sends as sub-steps of an action sequence.
5. **Scope.** All outbound user-attributed messages (public OSS, private external, internal DSM artifacts that bear the user's byline). Agent-internal artifacts (session transcripts, command outputs) excluded.
6. **Canonicalize** in DSM_0.2 (proposed home: §6 inbox-push area, or as a sibling section to Cross-Repo Write Safety) and CLAUDE.md template.

## Push cadence

Medium severity per BL-006's severity-graded propagation pattern. Standard `/dsm-wrap-up` Step 6 inbox-push at end of S14. No out-of-band push (the proposal is governance, not safety-class).

## Spoke-side guard until DSM Central absorbs

Reasoning lesson active in `.claude/reasoning-lessons.md` under "Cross-Repo & Governance" (`[auto] S14 [ecosystem]: Voice-Attribution Review (mechanism-aware)...`). Provides in-session enforcement until DSM Central scopes the BL and the canonical protocol absorbs the lesson.

## Success Criteria

1. DSM_0.2 extended with a Voice-Attribution Review section defining the mechanism-aware gate, the two-pass rule, the explicit-content-gate rule, and the bundling rule.
2. CLAUDE.md template includes a Voice-Attribution Review reinforcement block (similar to the existing Cross-Repo Write Safety block).
3. At least one subsequent spoke session surfaces a network-mediated comment via the explicit-content-gate path intentionally, and the path works without ad-hoc improvisation.
4. The bundling rule is observed in multi-step plans: voice-attributed sends are never sub-steps of an action sequence in the plan presented to the user.

## Tracking

- Sister BL: BL-006 (severity-graded feedback propagation, also In progress S14).
- Related reasoning lessons: S13 frame-capture / external-input safety; S13 Read-Before-Draft for OSS PRs; S13 "adjacent items are user IP".
- DSM Central tracking: BL number to be assigned by DSM Central when the proposal is scoped.
