# /dsm-align persistent report

**Timestamp:** 2026-04-14T15:00:00+02:00
**DSM version:** v1.4.18
**Run mode:** post-change
**Project:** heating-systems-conversational-ai
**Project type:** Application (DSM 4.0), Spoke

---

## Report

/dsm-align post-change report:
- Project type: Application (DSM 4.0), Spoke
- Created: .claude/hooks/transcript-reminder.sh, .claude/hooks/validate-transcript-edit.sh, .claude/settings.json
- Already correct: _inbox/ + done/ + README.md, all 9 dsm-docs/ folders, .gitattributes, .claude/reasoning-lessons.md, .claude/dsm-ecosystem.md, CLAUDE.md @ reference, alignment delimiters
- Fixed: CLAUDE.md alignment section regenerated (template drift v1.4.5 → v1.4.18)
- Collisions: dsm-docs/inbox/ (empty) vs canonical _inbox/ at root
- Warnings: 2 (see below)
- CLAUDE.md alignment: Regenerated (template drift resolved)
- CLAUDE.md content: OK
- CLAUDE.md redundancy: OK
- CLAUDE.md paths: OK
- .gitattributes: OK
- Command sync: N/A (not DSM Central)
- Feedback pushed: none pending
- EC governance scaffold: N/A (not EC)
- Transcript hooks: [2 installed / 0 updated / 0 ok] · settings.json: created

## Warnings (full text)

1. Naming collision: `dsm-docs/inbox/` exists alongside canonical `_inbox/` at project root. The `dsm-docs/inbox/` directory is empty (contains only `done/`, which is also empty). Canonical DSM location is `_inbox/` at project root. Consider removing `dsm-docs/inbox/` to eliminate ambiguity. NOT auto-fixed per `/dsm-align` policy.

2. DSM version advanced from v1.4.5 to v1.4.18. Spoke actions surfaced from CHANGELOG:
   - [1.4.18 BL-343] Review DSM_0.2.B §8 (Infrastructure File Collaboration Protocol) for behavioral changes — applies immediately via @ reference.
   - [1.4.18 BL-346] Review DSM_6.0 §1.10 ("We Need to Talk" foundational principle).
   - [1.4.18 BL-356] MEMORY.md budget optimization in /dsm-wrap-up — run scripts/sync-commands.sh --deploy on DSM Central (not this spoke).
   - Additional CHANGELOG entries between v1.4.5 and v1.4.18 may contain further spoke actions; full review recommended.

## Collisions (full text)

1. `dsm-docs/inbox/` vs canonical `_inbox/` — see warning 1 above.

## Already correct

- `_inbox/` at project root with `done/` subfolder and `README.md`
- `dsm-docs/blog/` with `done/` and `journal.md`
- `dsm-docs/checkpoints/` with `done/` and `README.md`
- `dsm-docs/decisions/` (no done/ required, contains 2026-04-07 orchestration decision)
- `dsm-docs/feedback-to-dsm/` with `done/` and `README.md`
- `dsm-docs/guides/` (empty, no done/ required)
- `dsm-docs/handoffs/` with `done/` and `README.md`
- `dsm-docs/plans/` with `done/` and `README.md` (contains 2 active plans)
- `dsm-docs/research/` with `done/` and `README.md` (contains 3 research files)
- `.gitattributes` present with LF enforcement
- `.claude/reasoning-lessons.md` (populated from prior STAA sessions)
- `.claude/dsm-ecosystem.md` (populated: dsm-central, portfolio, heating-guide, heating-app)
- `.claude/CLAUDE.md` @ reference to DSM_0.2
- CLAUDE.md alignment delimiters present
- CLAUDE.md content: no type mismatches (App Development Protocol appropriate for DSM 4.0)
- CLAUDE.md path references: all valid

## Steps skipped

- Step 11 (Command file drift): not DSM Central
- Step 3-EC (EC governance scaffold): not External Contribution
- Step 2 (backlog→_inbox migration): `_inbox/` already at canonical location