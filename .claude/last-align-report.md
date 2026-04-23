# /dsm-align persistent report

**Timestamp:** 2026-04-23T15:36:00+02:00
**DSM version:** v1.7.0 (from ~/dsm-agentic-ai-data-science-methodology/CHANGELOG.md latest heading)
**Run mode:** check-only
**Project:** heating-systems-conversational-ai
**Project type:** Application (DSM 4.0)

---

## Report

/dsm-align check-only report:
- Project type: Application (DSM 4.0) — unchanged from CLAUDE.md record
- Created: none
- Already correct: 8 dsm-docs/ folders, all done/ subdirs, 7 template files, _inbox/, .gitattributes LF enforcement, @ reference, alignment section matches v1.7.0 base + DSM 4.0 addition, .claude/ metadata files, 3 hooks byte-identical to Central (re-chmod +x applied idempotently), settings.json contains all template hook commands
- Fixed: none
- Collisions: none
- Warnings: 1 (Sprint 1 plan regex false-positive, see below)
- CLAUDE.md alignment: OK (matches v1.7.0 template)
- CLAUDE.md content: OK (App Development Protocol matches Application type; no Notebook protocol drift)
- CLAUDE.md redundancy: not scanned
- CLAUDE.md paths: not scanned
- .gitattributes: OK
- Command sync: N/A (not DSM Central)
- Feedback pushed: none pending (all per-session files already in done/)
- EC governance scaffold: N/A (not EC)
- Transcript hooks: 0 installed / 0 updated / 3 ok · settings.json: already ok

## Warnings (full text)

1. **Sprint plan regex false-positive:** `dsm-docs/plans/2026-04-07_sprint1_langgraph_plan.md` reports "missing Deliverables, Phases, Phase Boundary Checklist, Sprint Boundary Checklist" under the Step 3a regex `^##\s+$section`. Inspection shows all four sections ARE present, but under numbered headings:
   - `## 3.5 Phase Boundary Checklist (intra-sprint, per Template 8)`
   - `## 6.5 Sprint Boundary Checklist (per Template 8, customized for Sprint 1)`
   - `## 4. Build order (10 steps)` (equivalent to Phases)
   - `## 1. Scope` + `## 6. Exit criteria` (equivalent to Deliverables)

   The plan header explicitly records "Template 8 retro-fit 2026-04-17" and section 0 is "Template compliance note". The regex caveat in Step 3a docs the known limitation. This is informational; no action required. Sprint 2 plan (current active) passes the audit cleanly.

## Collisions (full text)

None.

## Already correct

- 8 canonical dsm-docs/ folders
- All done/ subdirectories where required
- 7 template files
- .gitattributes with LF enforcement
- .claude/CLAUDE.md @ reference (resolves to existing DSM_0.2 v1.1)
- Alignment delimiters (lines 3 and 106) + section content matches v1.7.0 base + DSM 4.0 addition
- .claude/dsm-ecosystem.md, .claude/reasoning-lessons.md, .claude/session-transcript.md present
- All 3 hook scripts byte-identical to Central source, executable (re-chmod applied defensively)
- .claude/settings.json contains all template hook commands (PreToolUse, UserPromptSubmit)
- No pending feedback files (all per-session feedback already in done/)
- Sprint 2 plan has all Template 8 sections under canonical headings

## Steps skipped

- Step 8b (redundancy scan): not run (low-priority, no drift suspected)
- Step 8c (path validation): not run (no CLAUDE.md edits since last align)
- Step 11 (command drift): N/A (not DSM Central) — per skill source, Step 11 is DSM-Central-scoped and detective-only; does not deploy
- Step 12b (inbox notification): triggered by warnings present (see next write)

## Note on spoke actions (correction from 15:20 report)

The previous report (15:20) surfaced `~/.claude/commands/` command drift as if it were a spoke-action gap for this project. That was incorrect on two counts: (a) /dsm-align Step 11 is DSM-Central-scoped; it is skipped on spokes, and (b) /dsm-align does not run `sync-commands.sh --deploy` anywhere — Step 11 only reports drift on Central, leaving deploy to the user. Runtime command drift at `~/.claude/commands/` is a user-scope concern (once-per-machine-per-version) and is neither detected nor managed by /dsm-align running in a spoke. Nothing to act on from this project.

v1.6.3 → v1.7.0 spoke-action annotations in Central's CHANGELOG are either:
- Review-style (BL-409 §8.8 at next Gate 1, BL-385/386/387/344/345 review carryover) — applied behaviorally at the next relevant moment, no file change
- User-scope deploys (BL-413/414) — handled by the user at Central level when they choose, not by a spoke session
