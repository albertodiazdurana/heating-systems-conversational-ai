# BL-006: Escalate the severity-graded ecosystem-feedback propagation pattern to DSM Central

**Status:** In progress (S14 — feedback file drafted at `dsm-docs/feedback-to-dsm/2026-05-07_s14_severity-graded-feedback-propagation.md`, queued for /dsm-wrap-up Step 6 push)
**Priority:** Medium
**Date Created:** 2026-05-07
**Origin:** STAA S13 lesson #6 (severity-graded ecosystem feedback propagation), user direction at /dsm-staa close
**Author:** Alberto Diaz-Durana (with AI assistance)

---

## Trigger

Active immediately. Should be drafted and pushed in S14 (or earlier if a parallel session has bandwidth).

## Problem Statement

The current `/dsm-wrap-up` Step 6 inbox-push mechanism propagates feedback files in `dsm-docs/feedback-to-dsm/` to DSM Central only at session wrap-up. This is the right cadence for low/medium-severity feedback (BL ideas, protocol observations, minor proposals) but is too slow for high-severity findings.

S13 surfaced a concrete instance: the frame-capture / soft-prompt-injection feedback (proposed DSM_0.2.C §3.1 + DSM_6.0 §1.13) is a safety-class governance gap that affects all spokes. Waiting for the next wrap-up to push it would have delayed DSM Central's BL scoping by an entire session cycle. The S13 mitigation was an out-of-band inbox push during a post-wrap-up turn (Option B): write the canonical feedback file locally + append a summary notification to `~/dsm-agentic-ai-data-science-methodology/_inbox/{spoke}.md` immediately + commit the file via chore branch after user inspection.

That mitigation was ad-hoc. The pattern needs to be canonicalized so future spokes apply it consistently when they encounter high-severity findings between wrap-ups.

## Proposed Solution

Send an ecosystem feedback file to DSM Central proposing the severity-graded propagation pattern as a formal addition to the inbox-push mechanism. The feedback should propose:

1. **Severity triage rule.** Define classification: feedback file gets a `**Severity:**` field with values `low` / `medium` / `high`. High = safety, governance, alignment, or any finding where waiting one session cycle would cost the ecosystem something irreversible (e.g., other spokes shipping with the same gap).

2. **Out-of-band push protocol (Option B).** For high-severity feedback, the originating spoke should:
   - Write the canonical feedback file to `dsm-docs/feedback-to-dsm/` (uncommitted, held for user inspection if mid-session).
   - Append a summary notification to `~/dsm-agentic-ai-data-science-methodology/_inbox/{spoke}.md` immediately, pointing to the canonical file path on the originating spoke and including a one-paragraph severity rationale.
   - Commit the canonical file via a chore branch (`chore/s{N}-{topic}-feedback`) + PR + merge after user approval.
   - Continue queuing low/medium feedback for the next /dsm-wrap-up Step 6 push.

3. **Inbox lifecycle.** DSM Central's inbox-processing skills should be aware that out-of-band entries may arrive between wrap-ups; the existing inbox-lifecycle protocol ("after processing, move to done/") handles this naturally, but the entry's severity field should drive scheduling priority for BL scoping.

4. **Canonicalize in DSM_0.2 governance.** The /dsm-wrap-up Step 6 description should be extended to mention severity triage and the out-of-band path; the protocol should explicitly NOT require a wrap-up before high-severity feedback can propagate.

## Success Criteria

- [ ] Feedback file written to `dsm-docs/feedback-to-dsm/2026-05-{DD}_s14_severity-graded-feedback-propagation.md` (or the actual S14 date).
- [ ] Summary notification appended to DSM Central inbox (out-of-band push, demonstrating the pattern itself in action).
- [ ] Canonical file committed via chore branch + PR + merge.
- [ ] Spoke reasoning lesson #6 (severity-graded propagation) marked as "active pending DSM Central absorption" in the lessons file; once DSM Central absorbs the pattern into /dsm-wrap-up Step 6 and inbox-lifecycle protocol, retire the spoke lesson in favor of the canonical home.

## Inputs Available When Drafted

- STAA S13 lesson #6 (the severity-graded propagation rule, in `.claude/reasoning-lessons.md` Cross-Repo & Governance, last STAA entry).
- S13 frame-capture feedback file at `dsm-docs/feedback-to-dsm/done/2026-05-07_s13_external-input-frame-capture.md` (working example of out-of-band push as Option B in practice).
- S13 OSS PR DoR feedback file at `dsm-docs/feedback-to-dsm/done/2026-05-07_s13_oss-pr-definition-of-ready.md` (working example of standard Step 6 push for medium-severity feedback).
- S13 checkpoint at `dsm-docs/checkpoints/2026-05-07_s13_checkpoint.md`.

## Test Plan

- [ ] Severity classification rule is concrete and testable (not "use judgment"); high-severity criteria enumerate the specific failure modes that justify out-of-band push.
- [ ] Out-of-band protocol is reproducible (any spoke could follow it without re-deriving the steps).
- [ ] Backwards-compatible: existing low/medium feedback files in spokes' `feedback-to-dsm/` continue to flow through wrap-up Step 6 unchanged.
- [ ] Demonstrates the pattern in action: this BL's feedback file should itself use the out-of-band push path, since proposing a new propagation pattern via the slow path would be a tells-vs-does mismatch.

## Revert Procedure

Standard `git revert` on the chore PR. The feedback file is advisory; DSM Central can decline or modify the proposal without spoke-side consequences. The spoke reasoning lesson stays active until DSM Central absorbs OR rejects the pattern.

---

**Author:** Alberto Diaz-Durana (with AI assistance)
