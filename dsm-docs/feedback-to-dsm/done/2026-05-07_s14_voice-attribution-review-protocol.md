**Pushed:** 2026-05-12 (Step 6 inbox push)

# Voice-Attribution Review Protocol

**Type:** Backlog Proposal
**Priority:** Medium
**Severity:** Medium
**Source:** heating-systems-conversational-ai
**Date:** 2026-05-07
**Session:** S14

## Summary

Propose a Voice-Attribution Review protocol covering all outbound user-attributed messages. Today, file-edit operations are gated through the tool-permission window where the user can review the diff before approving, but network-mediated operations (e.g., `gh pr comment`, `gh issue comment`, future Slack / email / DM tooling) post drafted content directly to the destination with no intermediate review gate. For content where the user is the byline, drafting and sending need separate gates so the user reviews the words before they go out.

## Problem Statement

Outbound communication drafted by the agent but attributed to the user falls into two mechanism classes:

1. **File-write-mediated content.** Commit messages, inbox notifications, feedback files, reasoning-lesson entries. The Edit / Write tool's permission window is the existing review gate; if the user inspects the diff they see the words before the file lands.
2. **Network-mediated content.** PR / issue comments, code-review replies, anything posted via `gh api`, future cross-repo notifications via Slack / email / DM tooling. The Bash tool's permission window asks the user to approve a command, but the comment body lives inside the command argument and is easy to skim past. There is no second gate between "approve the action" and "the words land on a public thread under your name."

The two classes have a shared failure mode: bundling approval of the *action* with approval of the *content*. The user authorizes "post a comment on PR #N" and the agent treats that as authorization for the comment body it drafted, but the user may have approved the action without re-reading the body. The asymmetry is sharper for network-mediated content because there is no diff window to focus attention on the words.

S14 surfaced a concrete instance. During the PR #11268 review-fix work, every file edit in `/tmp/haystack-fork` was gated one-at-a-time with concrete diffs surfaced and approved before the Edit ran. The PR comment at the end was bundled into a multi-step "Op 5: commit + push + PR comment" plan. The comment text was shown in the prior Pre-Generation Brief, but the user's "Authorize Op 5" approval covered all three sub-steps as a unit. The comment posted to a public thread under the user's GitHub byline before any second-pass review of the words.

The user surfaced the gap in the next turn: comments on public OSS threads are *the user's words*, not the agent's. The agent drafts, but the user owns the byline.

## Proposed Solution

### 1. Voice-Attribution Review gate (mechanism-aware)

Define a new gate in the Pre-Generation Brief sequence: when the agent drafts content that will appear with the user's name as byline, the content must be reviewed and approved separately from the action that delivers it.

The gate's enforcement differs by mechanism:

**File-write-mediated content.** The Edit / Write tool's permission window IS the review gate, but the agent must explicitly frame the user's review as "review the words, not just the action." Concretely: when drafting a commit message, an inbox-notification entry, a feedback file, or a reasoning-lesson entry, the agent surfaces the full text in conversation BEFORE the tool call, in addition to the tool-permission window's diff. The user has two opportunities to catch issues (the conversation-side draft and the diff window). The "two-pass" pattern reduces the chance the user approves the file write while skipping the words.

**Network-mediated content.** The Bash tool's permission window does not show a diff, so an additional explicit gate is required. The agent surfaces the full message body in conversation as a Gate 4 review step, asks for explicit approval of the body, and only then runs the network call (`gh pr comment`, `gh issue comment`, `gh api`, etc.). "Authorize the action" and "approve the body" must be separate, sequential approvals.

### 2. Scope (all outbound user-attributed messages)

The protocol covers any outbound communication where the byline is the user, regardless of channel:

- Public OSS comms: PR / issue comments, code-review replies, public thread comments
- Private external comms: Slack DMs, email, ticket replies (when those tools come online)
- Internal DSM artifacts: commit messages, inbox notifications, feedback files, reasoning-lesson entries (already file-write-gated, but covered here so the "review words, not just action" framing is consistent across mechanisms)
- Cross-repo notifications: spoke→Central inbox appends, hub→spoke notifications (file-write-mediated)

Excluded: agent-internal artifacts that the user does not byline (session transcripts written by the agent in agent voice, command outputs, debug traces).

### 3. Bundling rule

Multi-step plans must NOT bundle voice-attributed sends with adjacent actions. "Op 5: commit + push + PR comment" was a bundling violation because the network-mediated PR comment was treated as a sub-step of an action sequence rather than a separate Pre-Generation Brief stage with its own approval. The rule: if a plan includes a voice-attributed send, the plan presents the action gate (approve the send) and the content gate (approve the words) as distinct steps, not as a single approval covering both.

### 4. Canonicalize in DSM_0.2 governance

Add a new section to DSM_0.2 (proposed home: §6 inbox-push area, or as a sibling section to Cross-Repo Write Safety) defining:

- The Voice-Attribution Review gate (mechanism-aware).
- The two-pass rule for file-write-mediated content (surface text in conversation BEFORE the tool call, in addition to the diff window).
- The explicit-content-gate rule for network-mediated content (separate from the action approval).
- The bundling rule (voice-attributed sends are distinct gates, never sub-steps of an action sequence).

Update CLAUDE.md template to include a Voice-Attribution Review reinforcement block alongside the existing Cross-Repo Write Safety block.

## Origin

S14 (heating-systems-conversational-ai), 2026-05-07. PR `deepset-ai/haystack#11268` review-fix work. The 3 file-edit operations were gated one-at-a-time with concrete diffs surfaced; the PR comment at the end was bundled into a multi-step Op 5 plan and posted via `gh pr comment` without a separate body-approval gate. The user surfaced the asymmetry: the comment is "my words" on a public OSS thread under my byline, posting without review violates voice attribution.

This pattern is in the same protocol family as:

- **Cross-Repo Write Safety** (CLAUDE.md): a PR comment is a write to a third-party server; the existing rule's wording is path-centric and easy to misread as filesystem-only, and it does not differentiate file-write from network-mediated mechanisms.
- **S13 frame-capture / external-input safety lesson**: external content as observation by default. The inverse case is outbound content as user voice, also requires explicit gating.
- **S13 Read-Before-Draft for OSS PRs**: procedural pre-send hygiene for OSS contributions; Voice-Attribution Review is the post-draft, pre-send sibling.
- **S13 "adjacent items are user IP"**: drafted issue comments must not enumerate session-discovered next-step items as redirect scope. Same family: the agent drafts, but the user's voice owns the draft.

## Success Criteria

1. DSM_0.2 extended with a Voice-Attribution Review section defining the mechanism-aware gate, the two-pass rule, the explicit-content-gate rule, and the bundling rule.
2. CLAUDE.md template includes a Voice-Attribution Review reinforcement block (similar to the existing Cross-Repo Write Safety block).
3. At least one subsequent spoke session surfaces a network-mediated comment via the explicit-content-gate path (separate Gate 4 approval before the network call) intentionally, and the path works without ad-hoc improvisation.
4. The bundling rule is observed in multi-step plans involving voice-attributed sends: such sends are never sub-steps of an action sequence in the plan presented to the user.

## Tracking

- This file's lifecycle: queued for `/dsm-wrap-up` Step 6 push at end of S14 (medium severity, standard cadence per BL-006's severity-graded propagation pattern). After push, moves to `done/`.
- Sister proposals already in flight:
  - `dsm-docs/feedback-to-dsm/2026-05-07_s14_severity-graded-feedback-propagation.md` (BL-006: out-of-band path for high-severity findings).
  - `dsm-docs/feedback-to-dsm/done/2026-05-07_s13_external-input-frame-capture.md` (S13: external content as observation; absorbed into DSM Central inbox).
- Spoke-side guard: capture as reasoning lesson at `/dsm-wrap-up` Step 0 for in-session enforcement until DSM Central absorbs.
- DSM Central tracking: BL number to be assigned by DSM Central when the proposal is scoped.
