# Feedback , Session 2 , Session Transcript Protocol decays after activation

**Date:** 2026-04-07
**Session:** 2
**Project:** utility_conversational_ai
**Severity:** High , the protocol fails silently and the workaround (user monitoring the file in VS Code) is itself evidence the protocol is unreliable.

## Observation

In Session 2, I (the agent) executed `/dsm-go` correctly, including Step 6's "Behavioral activation (mandatory, immediate)" of the Session Transcript Protocol. I wrote the initial thinking block during the session-start ritual. Then, across **four subsequent turns** (README discussion, GitHub repo creation, README draft, license file), I wrote zero entries to `.claude/session-transcript.md`. The user caught this and asked for root cause analysis.

This is not a one-off. It is a structural decay pattern: the protocol activates loudly at session start, then fades.

## Root cause analysis

### 1. No mechanical enforcement

The Session Transcript Protocol is instruction-only. There is no harness hook, no pre-tool-use validation, nothing that blocks a turn from completing without a transcript append. Compliance depends entirely on the agent remembering on every turn. Instruction-only protocols have a known decay curve in long sessions.

### 2. Competing instructions crowd it out

The system prompt contains multiple high-salience efficiency instructions:

- "Output efficiency , go straight to the point. Try the simplest approach first."
- "make all independent calls in parallel"
- "Be extra concise"
- "If you can say it in one sentence, don't use three"

When the agent plans a turn, these instructions create pressure toward minimal tool calls. The transcript append is a tool call that produces no visible result for the user, so under efficiency pressure it gets dropped first. The protocol asks the agent to do *more* work per turn (extra Edit/Write calls), which directly contradicts the efficiency framing.

### 3. Session-start framing presents activation as a ritual

`/dsm-go` Step 6 says:

> **Behavioral activation (mandatory, immediate):** From this point forward, follow the Session Transcript Protocol... This is not a checklist item; it is a behavioral mode that remains active for the entire session.
>
> **This activation applies to /dsm-go's own remaining steps (7, 8, 9, 10).** Immediately after creating the transcript header, append a thinking entry summarizing the session-start checks completed so far...

The disclaimer "This is not a checklist item" is doing exactly the work that suggests it *will* be treated as a checklist item, otherwise the disclaimer would not be necessary. The example then concretizes the activation as "append a thinking entry summarizing session-start checks", which the agent completes and then mentally ticks off. The activation is framed as a one-time ritual at the boundary of `/dsm-go` even though the prose says "remains active for the entire session".

### 4. No turn-boundary checkpoint

The protocol describes the *what* (append thinking before acting, append output after completing work) but provides no *checkpoint* (how to detect a missed append on the current turn). There is no instruction like:

- "Before responding to the user, verify the transcript has a thinking block for this turn"
- "If the last transcript line is older than the previous user message, you skipped an append , catch up retroactively"

Without a checkpoint, the agent has no signal that compliance has lapsed.

### 5. The IDE-monitoring workaround is evidence of unreliability

The CLAUDE.md note "The user keeps it open in VS Code to monitor agent thinking in real time" frames IDE monitoring as a *feature*. It is actually a *workaround*. If the protocol were mechanically reliable, monitoring would be unnecessary. The fact that the user has institutionalized monitoring is the strongest evidence that the protocol fails in practice. DSM should not document the workaround approvingly, it should fix the underlying decay.

### 6. Tool result ordering hides the omission from the agent

When the agent completes a turn and the next user message arrives, the agent's working context shows the previous turn's tool results, the user's new message, and system reminders. There is no prominent surface that says "your last turn did not append to session-transcript.md". The omission is invisible until the user surfaces it manually.

## Impact

- **Reasoning trail loss.** The transcript is supposed to be a persistent reasoning log. Across this session, four turns of reasoning (including the GitHub repo creation decisions) are missing. STAA-style transcript analysis on this session would underrepresent the agent's actual work.
- **User burden.** The user has to monitor the IDE file and call out the violation manually. This is exactly the kind of micromanagement the protocol was meant to remove.
- **Protocol erosion.** Each session where the protocol decays without consequence trains the agent (via in-context examples) that decay is acceptable. Future sessions will decay faster.

## Recommendations for DSM Central

### Short-term (instruction tweaks)

1. **Add a turn-boundary checkpoint to the protocol.** Replace "append thinking BEFORE acting" with: "At the start of every turn, your **first tool call** must be an Edit or Write to `.claude/session-transcript.md`. If your first tool call is not a transcript append, you have violated the protocol , stop, append, then continue."
2. **Add a self-detection rule.** "If you notice the last transcript timestamp is older than the previous user message, you skipped an append on the current turn. Append a retroactive `[RETROACTIVE]` thinking block summarizing the missed turn before doing anything else."
3. **Reframe IDE monitoring.** Remove the "user keeps it open to monitor" framing from CLAUDE.md templates. Replace with: "The transcript is the reasoning log. The user should not need to monitor it , if you find yourself needing user reminders, the protocol has failed."

### Medium-term (mechanical enforcement)

4. **Add a hook.** A `PreToolUse` hook on Edit/Write/Bash that checks whether `.claude/session-transcript.md` has been touched in the current turn (since the last user message). If not, block the tool call with a message like: "Append to session-transcript.md first." This converts the protocol from instruction-only to mechanically enforced.
5. **Add a `UserPromptSubmit` hook** that injects a reminder into the agent's context: "REMINDER: your first tool call this turn must append to .claude/session-transcript.md."

### Long-term (protocol redesign)

6. **Reconsider whether per-turn appends are the right granularity.** The protocol assumes the agent should narrate every turn. In practice, many turns are trivial (single-tool reads, confirmations) and the narration adds noise. A better protocol might be: "Append at decision points and after completing discrete units of work, not on every turn." This would make compliance natural rather than ritualistic.
7. **Decouple thinking from transcript.** Anthropic models have native thinking blocks. The Session Transcript Protocol predates ubiquitous thinking-mode availability. Consider whether the transcript should capture *summaries* of native thinking rather than re-derive thinking via Edit/Write tool calls. The current design fights against the model's native machinery.

## Self-assessment

Session 1 had a methodology failure (skipped the planning pipeline, score 2/10). Session 2 has a protocol-compliance failure (transcript decay across 4 turns). Both are instruction-following failures that the user had to catch manually. The pattern suggests that single-instruction protocols in CLAUDE.md / DSM_0.2 do not survive long sessions in this codebase , the agent needs either mechanical enforcement or a redesigned protocol that aligns with default model behavior instead of fighting it.

## Score

**Compliance: 2/10** , protocol activated correctly at session start, then dropped for 4 consecutive turns.
**Detection: 0/10** , the agent did not self-detect; the user had to surface the violation.
**Recovery: 7/10** , once surfaced, root cause analysis was thorough and retroactive append was performed.