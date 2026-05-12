### [2026-05-12] Allow QA parallel sessions to write to `_inbox/` as a communication channel between sessions

**Type:** Methodology Observation (route to DSM Central as feedback)
**Priority:** Medium
**Source:** parallel session 14.1 (QA)

**Problem statement:**

Per `dsm-parallel-session-go.md` Step 3, QA parallel sessions are scoped to:

> Writes allowed to: `.claude/` (findings, notes, analysis output) and `dsm-docs/research/{date}_{topic}.md` when DSM_0.2 §10 Web Research Capture Protocol applies.

This makes `_inbox/` out of scope for QA sessions. In practice, QA sessions are exactly the sessions that produce small, actionable findings the main session should pick up next, status checks, audit results, scoped reviews. The natural delivery channel for "note for the main session to act on" is `_inbox/`, which DSM_3 §6.4 already defines as the transit point for inter-session/inter-project communication.

Current workaround paths:

- Write to `.claude/inbox-pending.md` (in-scope) and have the main session manually rename + move into `_inbox/`. Adds a hop, no semantic value.
- Ask the user for a one-time scope expansion (the path taken in 14.1). Forces an extra round-trip on a routine action.

Neither path is a real fix; both add friction to the canonical communication channel.

**Proposed solution:**

Amend `dsm-parallel-session-go.md` Step 3 (QA type scope) to:

> Writes allowed to: `.claude/`, `_inbox/{date}_{topic}.md` (for findings the main session should act on), and `dsm-docs/research/{date}_{topic}.md` when DSM_0.2 §10 Web Research Capture Protocol applies.

Rationale: `_inbox/` is append-only from a parallel session's perspective (entries are added, not modified or removed; the main session owns the lifecycle and moves entries to `_inbox/done/`). It does not introduce a shared-write conflict surface. The "do not modify shared or central files" rule still applies to existing `_inbox/` entries , parallel sessions add new files, they never edit existing ones.

Optional follow-on: extend the same allowance to BL parallel sessions if a BL session produces a finding that warrants a separate inbox entry. (Lower priority; BL sessions usually deliver work in their declared scope and the BL file update is the communication channel.)

**Action requested:**

Route to DSM Central as feedback. The change is local to `dsm-parallel-session-go.md` Step 3 (and the "Behavioral Rules" QA bullet referencing the same scope). No downstream skill is affected; commit booking, registry promotion, wrap-up flow are all unchanged.

**Source incident:** Session 14, parallel session 14.1, user requested an inbox-routed status report on S13 OSS PRs; QA scope blocked the write, required explicit Option-B override.
