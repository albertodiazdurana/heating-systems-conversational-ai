# /dsm-align persistent report

**Timestamp:** 2026-04-17T12:05:00+02:00
**DSM version:** v1.5.2
**Run mode:** post-change
**Project:** heating-systems-conversational-ai
**Project type:** Application (DSM 4.0)

---

## Report

/dsm-align post-change report:
- Project type: Application (DSM 4.0), Spoke
- Created: .claude/hooks/validate-rename-staging.sh
- Already correct: 8 dsm-docs/ folders, 6 done/ subfolders, 6 template files, _inbox/ scaffold, .gitattributes, .claude/dsm-ecosystem.md, .claude/reasoning-lessons.md, validate-transcript-edit.sh (byte-identical)
- Fixed: transcript-reminder.sh updated (BL-371 multi-entry registry support), settings.json merged (PreToolUse:Bash -> validate-rename-staging.sh), all hooks re-chmodded +x
- Collisions: none
- Warnings: 2
- CLAUDE.md alignment: OK (up to date with v1.5.2 base + DSM 4.0 addition)
- CLAUDE.md content: OK (App Development Protocol matches DSM 4.0)
- CLAUDE.md redundancy: OK
- CLAUDE.md paths: 1 stale path found (~/dsm-residential-energy referenced but missing from filesystem)
- .gitattributes: OK
- Command sync: N/A (not DSM Central)
- Feedback pushed: none pending
- EC governance scaffold: N/A (not EC)

## Warnings (full text)

1. CLAUDE.md `~/dsm-residential-energy/` (line 133) and ecosystem registry `heating-app` row reference a path that does not exist on the filesystem. This is the companion Streamlit app cited as the source for deterministic tool logic. Either restore the path, update both references to the correct location, or remove if no longer needed.

2. DSM version updated from v1.4.18 to v1.5.2. Spoke-action notes from CHANGELOG between v1.4.18 and v1.5.2:
   - **v1.5.1 (BL-370):** Run `/dsm-align` on next `/dsm-go` to install the new validate-rename-staging.sh hook. APPLIED by this run (script copied + settings.json merged).
   - **v1.5.2 (BL-373 F2):** None required.
   - **v1.5.0 and below (v1.4.19, v1.4.20, v1.5.0):** Read CHANGELOG to confirm no other spoke actions are pending.

## Collisions (full text)

None.

## Already correct

- All 8 canonical dsm-docs/ folders present (blog, checkpoints, decisions, feedback-to-dsm, guides, handoffs, plans, research)
- All 6 done/ subfolders present
- All 6 template files present (journal.md + 5 README.md files)
- _inbox/ exists at root with done/ and README.md
- .gitattributes contains LF enforcement
- .claude/dsm-ecosystem.md present with dsm-central, portfolio, heating-guide, heating-app entries
- .claude/reasoning-lessons.md present with header
- CLAUDE.md @ reference valid (resolves to existing DSM_0.2_Custom_Instructions_v1.1.md)
- CLAUDE.md alignment block matches v1.5.2 template (base + DSM 4.0 addition) byte-for-byte
- validate-transcript-edit.sh byte-identical to Central source
- No legacy feedback files (backlogs.md / methodology.md), no per-session feedback files outside done/, no consumed handoffs outside done/

## Steps skipped

- Step 11 skipped: not DSM Central
- Step 3-EC skipped: not External Contribution
- Step 6 (feedback push) skipped: no pushable entries (feedback-to-dsm/ contains only README + done/)