# /dsm-align persistent report

**Timestamp:** 2026-04-18T12:25:00+02:00
**DSM version:** v1.5.4 (from ~/dsm-agentic-ai-data-science-methodology/CHANGELOG.md)
**Run mode:** check-only
**Project:** heating-systems-conversational-ai
**Project type:** Application (DSM 4.0)

---

## Report

/dsm-align check-only report:
- Project type: Application (DSM 4.0) [primary markers: pyproject.toml with [project], src/, tests/, app.py] — no classification change from recorded type
- Created: none
- Already correct: 8 dsm-docs/ folders, 6 template files, 3 hook scripts (byte-identical, re-chmod'd), settings.json hooks wiring, _inbox/README.md, .gitattributes (LF enforced), .claude/ state files
- Fixed: none
- Collisions: none
- Warnings: 3 (see below)
- CLAUDE.md alignment: OK (delimiters present at lines 3/106, section 17.1 template unchanged in v1.5.3 to v1.5.4)
- CLAUDE.md content: OK (project-specific sections match Application type)
- CLAUDE.md redundancy: OK
- CLAUDE.md paths: OK (_reference/, _reference/sprint-plan.md, external heating-guide, external heating-apps all present)
- .gitattributes: OK (`* text=auto eol=lf` present)
- Command sync: N/A (not DSM Central)
- Feedback pushed: none pending (no session-scoped or technical.md entries without `Pushed:` marker)
- EC governance scaffold: N/A (not EC)

## Warnings (full text)

1. Sprint plan `dsm-docs/plans/2026-04-07_sprint1_langgraph_plan.md` uses numbered prefixes on Template 8 sections (e.g., `## 0.5 Research Assessment`, `## 3.5 Phase Boundary Checklist`, `## 6.5 Sprint Boundary Checklist`). Sections are present but do not match the strict audit regex of Step 3a. Informational; the retro-fit adapted Template 8 onto the existing numbered structure per MEMORY.md Session 5.
2. Plan `dsm-docs/plans/BL-003_streamlit-boot-asyncio-invalidstate.md` has `**Status:** Done` but is still in `dsm-docs/plans/` rather than `dsm-docs/plans/done/`. Lifecycle reminder: closed BLs should be moved to `done/`.
3. Plan `dsm-docs/plans/2026-04-07_sprint1_langgraph_plan.md` shows `**Status:** In execution (Session 5)` but Sprint 1 closed at Session 6 (7/7 per MEMORY.md). Stale status line; consider updating to `Done` or moving the plan to `done/`.

## Collisions (full text)

None.

## Already correct

- dsm-docs/ canonical subfolders (blog, checkpoints, decisions, feedback-to-dsm, guides, handoffs, plans, research)
- `done/` subfolders where required (blog, checkpoints, feedback-to-dsm, handoffs, plans, research)
- Template files: journal.md, checkpoints/README.md, feedback-to-dsm/README.md, handoffs/README.md, plans/README.md, research/README.md
- `_inbox/` with done/ and README.md
- `.gitattributes` with LF enforcement
- CLAUDE.md `@` reference to DSM_0.2 (line 1)
- CLAUDE.md BEGIN/END alignment delimiters
- Project-type-appropriate CLAUDE.md sections (App Development Protocol present for Application)
- External path references resolve (heating-guide, heating-apps both exist)
- `.claude/session-transcript.md`, `.claude/reasoning-lessons.md`, `.claude/dsm-ecosystem.md` present
- Hook scripts byte-identical with Central source and executable: transcript-reminder.sh, validate-transcript-edit.sh, validate-rename-staging.sh
- `.claude/settings.json` hooks wiring matches template (PreToolUse x2, UserPromptSubmit x1)
- Feedback files: no legacy `backlogs.md`/`methodology.md`; no unpushed per-session files

## Steps skipped

- Step 11 skipped: not DSM Central (no `scripts/commands/`)
- Step 3-EC skipped: not External Contribution
- Step 6 no action: no pushable feedback entries

## Version change

- Previous marker: v1.5.2 (dated 2026-04-18)
- Current Central version: v1.5.4
- Delta: v1.5.3 (BL-376 mirror tags, spoke action: none) + v1.5.4 (BL-377 parallel-session fix, spoke action: none; BL-379 Project Type Detection broadening, spoke action: run `/dsm-align` to re-evaluate — applied by this run, detection confirmed Application unchanged)
