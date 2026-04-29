# S10 Methodology Feedback — 2026-04-23

**Project:** heating-systems-conversational-ai
**Session:** 10
**DSM version at time of observation:** v1.7.0

---

## Observation: Skill silence is not agent silence

**Context.** At session start I executed `/dsm-align` manually and supplemented its output with an off-skill check: `diff -q` between `~/.claude/commands/dsm-go.md` + `dsm-wrap-up.md` and the tracked source in DSM Central. I promoted the drift finding into the skill's check-only report under `Command sync: Drifted: 2` and into the session report as `Spoke actions pending (v1.7.0 delta)` with a recommendation to run `sync-commands.sh --deploy`.

None of that is inside `/dsm-align`'s scope on a spoke. Step 11 starts with "Skip this step if the project is not DSM Central." The skill itself would have emitted nothing about command drift. I filled the silence with an invented action.

**Cost.** ~115 transcript lines (lines 33–147), 4 user correction turns, 2 agent defensive turns, 1 full `/dsm-align` re-run needed to falsify the claim empirically. The user's first correction ("implementing BL items is responsibility and scope of only dsm central") was the statement that would have prevented the entire detour at minute 0 if I had applied it as an active filter.

## Root causes

1. **Off-skill supplementation.** Ran checks adjacent to a skill's declared scope and bundled them into the skill's report. The correct read on a clean `/dsm-align` run is "aligned, no actions needed". I manufactured an action list by running off-skill checks.
2. **BL / spoke-action conflation.** Treated BL-413 and BL-414 as things this spoke fulfills. The BL is Central's implementation; the spoke-action annotation is the downstream instruction, sometimes user-scope (not spoke-scope).
3. **User-scope vs project-scope boundary blur.** `~/.claude/commands/` is a user-scope directory, shared across every DSM project on the machine. Drift there is once-per-machine-per-version, not per-spoke-session. Surfacing it inside a spoke's alignment report miscategorizes the concern.
4. **Auto-mode action bias.** Auto mode's "prefer action over planning" principle biased me toward offering to run `sync-commands.sh --deploy` from a spoke session, instead of faithfully reporting the skill's (silent) output.
5. **Skill Self-Reference Protocol violation (DSM_0.2 §8.6).** §8.6 requires reading the skill file before claiming its behavior. I claimed `/dsm-align` scope from memory, twice — once at the initial run and once when defending the deploy offer — until the user forced me to read the source.

## Proposal

Add a principle to DSM_0.2 §8.6 (or a sibling subsection):

> **Skill scope is authoritative.** A skill's declared scope defines its output. Checks adjacent to the skill's scope are separate findings and must be reported separately, not folded into the skill's report. **Silence from the skill on a concern is the skill's answer.** Before widening a skill's report with an adjacent check, ask: is this check part of the skill's documented steps? If not, either (a) run it as an out-of-band audit with its own label, or (b) file a BL to extend the skill.

This generalizes the existing §8.6 "read the skill before claiming behavior" rule to cover the adjacent failure mode: *augmenting* the skill's behavior rather than *misremembering* it. Both produce the same symptom (the skill appears to say something it didn't), but through different mechanisms.

## Effectiveness score

| Protocol area | Score (1-5) | Note |
|---|---|---|
| DSM_0.2 §8.6 Skill Self-Reference | 2 | Prevented memory-based claims about skill behavior once invoked. Did not prevent supplementing a correctly-invoked skill with off-scope checks. |
| DSM_0.2 §8.7 Token-Minimizing Config at Gate 1 | N/A | No Gate 1 in this detour; /dsm-align and session-report were not gated artifacts. |
| CLAUDE.md §1 Skill Self-Reference (project override) | 2 | Same observation as §8.6 |
| CLAUDE.md §1 Working Style "be concise in answers" | 2 | Responses defending the error were long and restated the wrong framing before converging. |

## Related session artifacts

- `.claude/last-align-report.md` (15:36 revision contains a correction paragraph)
- `.claude/session-transcript.md` lines 33–147 (full detour)
- `.claude/reasoning-lessons.md` (new [skill]-tagged entry from this session)
