# /dsm-align persistent report

**Timestamp:** 2026-04-21T13:08:00+02:00
**DSM version:** v1.6.3
**Run mode:** check-only
**Project:** heating-systems-conversational-ai
**Project type:** Application (DSM 4.0), Spoke

---

## Report

/dsm-align check-only report:
- Project type: Application (Spoke)
- Created: none
- Already correct: 26 (8 dsm-docs folders, 6 done/ subfolders, 5 READMEs, journal.md, _inbox, .gitattributes, .claude/dsm-ecosystem.md, .claude/reasoning-lessons.md, CLAUDE.md @ reference, CLAUDE.md alignment delimiters)
- Fixed: none (hooks chmod +x re-applied idempotently to 3 files)
- Collisions: none
- Warnings: 1 (Sprint 1 plan uses customized section numbering; not a violation but does not match strict Template 8 regex)
- CLAUDE.md alignment: OK (up to date)
- CLAUDE.md content: OK
- CLAUDE.md redundancy: OK
- CLAUDE.md paths: OK
- .gitattributes: OK (LF enforcement present)
- Command sync: N/A (not DSM Central)
- Feedback pushed: none pending
- EC governance scaffold: N/A (not EC)

## Warnings (full text)

1. Sprint plan `dsm-docs/plans/2026-04-07_sprint1_langgraph_plan.md` uses customized Template 8 section numbering (e.g., `## 3.5 Phase Boundary Checklist`, `## 6.5 Sprint Boundary Checklist`). Strict BL-378 regex (`^## Phase Boundary Checklist`) does not match. Sections ARE present; this is a soft warning only, no action required. Sprint 2 plan `dsm-docs/plans/2026-04-18_sprint2_rag_haystack_plan.md` passes strict audit (all 5 sections matched).

## Collisions (full text)

None.

## Already correct

- `_inbox/` at project root (with `done/`, `README.md`)
- `dsm-docs/blog/` (with `done/`, `journal.md`)
- `dsm-docs/checkpoints/` (with `done/`, `README.md`)
- `dsm-docs/decisions/`
- `dsm-docs/feedback-to-dsm/` (with `done/`, `README.md`, no legacy files)
- `dsm-docs/guides/`
- `dsm-docs/handoffs/` (with `done/`, `README.md`, no consumed handoffs outside done/)
- `dsm-docs/plans/` (with `done/`, `README.md`)
- `dsm-docs/research/` (with `done/`, `README.md`)
- `.gitattributes` with `* text=auto eol=lf`
- `.claude/session-transcript.md`
- `.claude/dsm-ecosystem.md` (4 entries: dsm-central, portfolio, heating-guide, heating-apps)
- `.claude/reasoning-lessons.md`
- CLAUDE.md `@` reference to DSM_0.2_Custom_Instructions_v1.1.md (valid)
- CLAUDE.md alignment section delimiters present (lines 3-106), content matches template
- No pending feedback files, no legacy feedback files
- Transcript hooks: 3 scripts byte-identical to Central source, chmod +x re-applied

## Steps skipped

- Step 11 skipped: not DSM Central (no scripts/commands/ directory)
- Step 3-EC skipped: not External Contribution
- Step 6 feedback push: no pending entries (all feedback files already moved to done/ in Session 8 wrap-up)
