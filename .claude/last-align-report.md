# /dsm-align persistent report

**Timestamp:** 2026-04-18T09:37:00+02:00
**DSM version:** v1.5.2 (from ~/dsm-agentic-ai-data-science-methodology/CHANGELOG.md)
**Run mode:** check-only
**Project:** heating-systems-conversational-ai
**Project type:** Application (DSM 4.0), Spoke

---

## Report

/dsm-align check-only report:
- Project type: Application (DSM 4.0), Spoke
- Created: none
- Already correct: 8/8 dsm-docs folders + done/ + templates; _inbox/ + done/ + README; .gitattributes; .claude/reasoning-lessons.md; .claude/dsm-ecosystem.md; CLAUDE.md @ reference; alignment delimiters
- Fixed: none
- Collisions: none
- Warnings: 1 (consumed handoffs still in dsm-docs/handoffs/, see below)
- CLAUDE.md alignment: present (delimiters found); deep drift check skipped (no DSM version change since last align)
- CLAUDE.md content: OK (last checked 2026-04-17)
- CLAUDE.md redundancy: OK
- CLAUDE.md paths: OK
- .gitattributes: OK (LF enforced)
- Command sync: N/A (not DSM Central)
- Feedback pushed: none pending (feedback-to-dsm/ contains only README + done/)
- EC governance scaffold: N/A (not EC)
- Transcript hooks: 0 installed / 0 updated / 3 already_ok; settings.json: already ok
- DSM version change: none (v1.5.2 → v1.5.2; no spoke actions to surface)

## Warnings (full text)

1. Consumed handoffs found outside `done/`: `dsm-docs/handoffs/2026-04-17_s5_step11_smoke_test_evidence.md` and `dsm-docs/handoffs/2026-04-17_s5_step11_smoke_test_results.md` are from Session 5 and should be moved to `dsm-docs/handoffs/done/`. `/dsm-go` Step 3 will handle this automatically on session start.

## Collisions (full text)

None.

## Already correct

- All 8 canonical dsm-docs/ folders (blog, checkpoints, decisions, feedback-to-dsm, guides, handoffs, plans, research)
- All 7 done/ subfolders (blog, checkpoints, feedback-to-dsm, handoffs, plans, research, _inbox)
- All 6 README template files
- `_inbox/` + `_inbox/README.md` + `_inbox/done/`
- `.gitattributes` with LF enforcement
- `.claude/reasoning-lessons.md` with header (Verification & Assertions category primed)
- `.claude/dsm-ecosystem.md` with dsm-central entry pointing to ~/dsm-agentic-ai-data-science-methodology
- CLAUDE.md `@` reference → DSM_0.2_Custom_Instructions_v1.1.md valid
- CLAUDE.md alignment delimiters present (BEGIN/END markers)
- 3 transcript hooks present, byte-identical to source, executable bit applied
- settings.json hook entries already merged

## Steps skipped

- Step 11 skipped: not DSM Central
- Step 6 (feedback push): nothing to push (folder empty)
- Step 13 spoke-action surfacing: no version change (1.5.2 → 1.5.2)