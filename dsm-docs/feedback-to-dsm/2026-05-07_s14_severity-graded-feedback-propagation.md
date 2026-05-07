# Severity-graded ecosystem-feedback propagation

**Type:** Backlog Proposal
**Priority:** Medium
**Severity:** Medium
**Source:** heating-systems-conversational-ai
**Date:** 2026-05-07
**Session:** S14
**Spoke BL:** dsm-docs/plans/BL-006_escalate-high-severity-feedback-pattern-to-dsm-central.md

## Summary

Propose a severity-graded propagation pattern for spoke-to-Central ecosystem feedback. Today, all spoke feedback in `dsm-docs/feedback-to-dsm/` is pushed to DSM Central via `/dsm-wrap-up` Step 6 inbox-push, regardless of severity. This is the right cadence for low/medium-severity items (BL ideas, methodology observations, minor proposals) but is too slow for safety-class findings that all spokes need to know about quickly. S13 surfaced a concrete instance and operationalized an out-of-band path ad hoc; this proposal canonicalizes the pattern.

## Problem Statement

`/dsm-wrap-up` Step 6 propagates feedback to DSM Central only at session wrap-up. For most feedback this cadence is appropriate, the next wrap-up is rarely more than a few days out, and DSM Central scopes the resulting BLs against its own backlog priority.

For high-severity findings (safety, governance, alignment, frame-capture / soft-prompt-injection failure modes), waiting one session cycle has real cost: other spokes may ship work that reproduces the same gap before DSM Central absorbs the lesson. S13 surfaced this with the frame-capture / soft-prompt-injection feedback (proposed DSM_0.2.C §3.1 + DSM_6.0 §1.13), a safety-class governance gap affecting all spokes. The S13 mitigation was an out-of-band inbox push during a post-wrap-up turn ("Option B"): write the canonical feedback file locally + append a summary notification to `~/dsm-agentic-ai-data-science-methodology/_inbox/{spoke}.md` immediately + commit the canonical file via chore branch after user inspection.

That mitigation was ad hoc. The pattern needs to be canonicalized so future spokes apply it consistently when they encounter high-severity findings between wrap-ups.

## Proposed Solution

Four pieces:

### 1. Severity triage rule

Each feedback file gains a `**Severity:**` field with values `low` / `medium` / `high`.

- `low` / `medium`: BL ideas, protocol observations, minor proposals, methodology scores. Standard `/dsm-wrap-up` Step 6 cadence.
- `high`: safety, governance, alignment, or any finding where waiting one session cycle would cost the ecosystem something irreversible (e.g., other spokes shipping with the same gap; user-impacting safety regressions).

The triage question for the agent: "would waiting until the next wrap-up cost the ecosystem something irreversible?" If yes, classify high.

### 2. Out-of-band push protocol (Option B)

For `high`-severity feedback, the originating spoke should:

1. Write the canonical feedback file to `dsm-docs/feedback-to-dsm/` (uncommitted, held for user inspection if mid-session).
2. Append a summary notification to `{dsm-central}/_inbox/{spoke-name}.md` immediately, pointing to the canonical file path on the originating spoke and including a one-paragraph severity rationale.
3. Commit the canonical file via a chore branch (`chore/s{N}-{topic}-feedback`) + PR + merge after user approval.

For `low` / `medium`-severity feedback: continue queuing for the next `/dsm-wrap-up` Step 6 push (no change from current behavior).

### 3. Inbox lifecycle awareness

DSM Central's inbox-processing skills should be aware that out-of-band entries may arrive between wrap-ups. The existing inbox lifecycle (after processing, move to `done/`) handles this naturally, but the entry's severity field should drive scheduling priority for BL scoping. High-severity entries jump the queue; low/medium follow normal scheduling.

### 4. Canonicalize in DSM_0.2 governance

The `/dsm-wrap-up` Step 6 description should be extended to mention severity triage and the out-of-band path. The protocol should explicitly NOT require a wrap-up before high-severity feedback can propagate. A short addition to DSM_0.2 §6 (Inbox-push) referencing the severity field and out-of-band path suffices.

## Origin

S13 (heating-systems-conversational-ai) frame-capture / soft-prompt-injection user audit. The feedback artifact (`dsm-docs/feedback-to-dsm/done/2026-05-07_s13_external-input-frame-capture.md`) was written using the ad-hoc Option B path, with an inbox notification appended at `{dsm-central}/_inbox/heating-systems-conversational-ai.md` on 2026-05-07. The pattern worked, the user inspected the canonical file mid-session and the inbox notification reached DSM Central before S13 closed.

The reasoning lesson from that session captures the triage rule informally: "Severity-graded ecosystem feedback propagation. Low/medium-severity feedback files queue for /dsm-wrap-up Step 6 inbox push at the next wrap-up. HIGH-severity feedback (safety, governance, alignment) needs out-of-band DSM Central inbox push between wrap-ups so DSM Central can begin BL scoping ahead of the next spoke session." This proposal lifts that lesson into canonical protocol.

## Success Criteria

1. DSM_0.2 §6 (or wherever `/dsm-wrap-up` Step 6 is canonically described) extended to reference severity triage and the out-of-band path.
2. The `/dsm-align` template feedback README mentions the `Severity:` field as part of the per-session feedback file schema.
3. At least one subsequent spoke session uses the pattern intentionally (high-severity classification + Option B push) and the path works without ad-hoc improvisation.

## Tracking

- Spoke-side BL: `dsm-docs/plans/BL-006_escalate-high-severity-feedback-pattern-to-dsm-central.md` (Status: In progress as of S14).
- This feedback file's lifecycle: queued for `/dsm-wrap-up` Step 6 push at end of S14. After push, moves to `done/`.
- DSM Central tracking: BL number to be assigned by DSM Central when the proposal is scoped.
