### [2026-04-17] /dsm-align: alignment updated (warnings present)

**Type:** Notification
**Priority:** Medium
**Source:** /dsm-align

Run mode: post-change
Full report: `.claude/last-align-report.md`

Summary:
- Created: .claude/hooks/validate-rename-staging.sh (BL-370 hook)
- Fixed: transcript-reminder.sh updated to BL-371 multi-entry registry version, settings.json merged (PreToolUse:Bash entry), all hooks re-chmodded
- Warnings: 2 (DSM version jump v1.4.18 → v1.5.2 with BL-370 spoke action applied; ~/dsm-residential-energy missing from filesystem despite CLAUDE.md and ecosystem registry references)
- Collisions: 0
