# Reasoning Lessons — Heating Systems Conversational AI

Lessons distilled from session transcript analysis (STAA). Entries are tagged
by source session and scope (`ecosystem` | `pattern` | `project`).

## Verification & Assertions

- [STAA] S1 [ecosystem]: Project type detection from folder structure alone is unreliable when `_reference/` contains substantive scope material. Read `_reference/` BEFORE finalizing project type in `/dsm-go`.
- [STAA] S1 [ecosystem]: When CLAUDE.md or `_reference/` cites external paths, verify with `ls` before quoting them in research or plan documents.
- [STAA] S3 [ecosystem]: Before treating a third-party framework feature as missing, read the source, not just the docs. "Undocumented" ≠ "unimplemented."
- [STAA] S3 [pattern]: When preliminary research recommends a framework, verify the comparison baseline matches the actual alternatives in scope. Comparing to the wrong alternative is a silent failure mode that survives review.
- [auto] S4 [ecosystem]: `BaseTool.handle_tool_error` is narrower than its name implies, it only catches `ToolException` subclasses, not generic `Exception`. Read the source before treating an opt-in recovery flag as universal. Verified empirically in `tests/test_tool_error_handling.py` (BL-002 edit 4).
- [auto] S4 [pattern]: Frame "assumed behavior" tests as empirical probes with three pre-enumerated outcome categories (PASS / expected fail / unexpected fail). Each failure mode becomes a documented finding, not a blocker. One probe delivered two cascading findings in this session (default propagation + narrow `handle_tool_error` scope).

## Pipeline Discipline

- [STAA] S1 [ecosystem]: Material in `_reference/` is preliminary input, not actionable. Pipeline is `_reference/` → `dsm-docs/research/` → `dsm-docs/plans/` → implementation. Never propose implementation directly from `_reference/`.
- [STAA] S1 [ecosystem]: Defer edits to CLAUDE.md Section 4 (project specifics) until research validates assumptions. Section 4 is downstream of the planning pipeline, not upstream.
- [STAA] S3 [pattern]: For experimental projects, framework choice should optimize for replaceability of subsystems, not for stack uniformity. State the project's experimental vs. production posture before choosing a framework.

## Decision Heuristics

- [STAA] S1 [pattern]: When recommending tech-stack defaults that touch core dependencies (LLM provider, framework), present options with tradeoffs rather than a single recommendation. Defaults reveal training-data bias.
- [STAA] S3 [pattern]: When a pivot decision requires both "validate option X" and "validate combination of X+Y," split into named parallel research tracks; converge at the plan-update stage.
- [STAA] S3 [pattern]: Before executing a pivot batch, enumerate surviving artifacts explicitly ("sunk cost is X; Y and Z survive because they are framework-agnostic"). Converts vague rework fear into a scoped inventory and exposes any hidden coupling.

## Batching & Efficiency

- [STAA] S1 [ecosystem]: When research surfaces multiple decision points, batch them into a numbered list for one user response rather than asking serially.
- [STAA] S3 [ecosystem]: When research output drives multiple downstream artifact changes, present them as a labeled batch (A/B/C…) for single-pass approval.

## Protocol Hygiene

- [STAA] S1 [ecosystem]: Session Transcript Protocol "read last 3 lines, anchor on last non-empty line" should be paired with a monotonic-timestamp check; backwards timestamps indicate protocol violation.
- [STAA] S1 [ecosystem]: When re-running or refining work already reported, append a delta block rather than re-emitting the original output block.
- [STAA] S3 [ecosystem]: Session Transcript Protocol violations are silent. The harness does not enforce appends; only a user reminder catches the lapse. Self-check at every output: "did I append a thinking block since the last user turn?" If no, append before output.
- [STAA] S3 [ecosystem]: `git mv` requires the source to be tracked. For files staged-but-not-committed or untracked, use plain `mv` then `git add` the new path.
- [auto] S4 [pattern]: When a deprecation warning surfaces on the FIRST pytest run of new code, halt and decide migration before committing. Shipping with the warning means the deprecated API spreads across modules and the later migration is a multi-file refactor instead of a two-line import swap.

## Cross-Repo & Governance

- [STAA] S3 [ecosystem]: Before initiating a cross-repo contribution (PR, issue, doc patch), check whether the target ecosystem has a contribution playbook. If not, request one via inbox before drafting.
- [S4] S4 [ecosystem]: Treat the capability experiment and the upstream contribution as ONE pipeline, not two tracks. The experiment's primary job is a pass/fail project decision; the docs/bug gaps surface as a side effect. The experiment script + a short deep-dive note are the evidence base for the contribution, no separate work needed. Follow issue-before-PR to gauge maintainer response; time-box the wait (~2 weeks for active projects). Source: graph-explorer FalkorDBLite playbook (2026-04-13 inbox).
- [auto] S5 [pattern]: Apply an explicit evidence-strength scale (third-party benchmark > vendor benchmark > vendor capability claim > anecdotal) when ranking candidate technologies. Treating "vendor claims X" as equal to "third-party benchmark scores model on X" distorts rankings toward easiest-to-find evidence. Caught a bad first ranking under user pushback; re-ranking on the scale put the most-evidenced candidate (llama3.1:8b: BFCL 76.1 + MMLU-DE 60.59) ahead of the convenient-fit candidate (qwen3:4b: zero measured numbers).
- [auto] S5 [pattern]: Constraints covered by a documented plan-level fallback (e.g., "OpenAI escape hatch if local fails") become *soft*, even when they look hard in isolation. Treating soft constraints as hard distorts ranking toward "cheap to satisfy." Pre-flight: for each criterion, is there a documented fallback? If yes, classify as soft.
- [auto] S5 [pattern]: At Pre-Generation Brief Gate 2, surface the strongest counter-evidence to your own recommendation BEFORE asking for approval. Procedural addition to the four-gate model. Caught two ranking errors this session via user pushback that should have been caught by the agent's own counter-evidence step.
- [auto] S5 [project]: Read §6 exit criteria boxes strictly, not pragmatically. When a smoke test fails one box (Q2 ValueError) but passes the gating box (Q5), the strict read is "NOT met." Closing on a partial-pass §6 sets a precedent of corner-cutting; the Sprint Boundary Checklist exists to catch this.
- [auto] S5 [pattern]: When multiple candidates have zero measured evidence on a criterion, tiebreakers MUST favor cleanly-dominant alternatives. "Documented-but-unranked" is a cop-out; if no scenario warrants reaching for X over Y, X is strictly dominated → eliminate. Caught under user pushback ("why not ranked?").
- [auto] S5 [pattern]: When a third-party tool emits its own bug-report URL, evaluate the supported-version envelope BEFORE filing upstream. Streamlit's "Please report this bug" on Python 3.11.0rc1 (release candidate from before 3.11.0 GA) deserves a venv upgrade test first. Filing on unsupported runtimes burns maintainer time on environment quirks.
- [auto] S5 [project]: Plans in `dsm-docs/plans/` may silently violate DSM_2.0.C Template 8 (no DSM tool audits plan-document structure). Before suggesting work on a sprint plan, verify it contains the Sprint Boundary Checklist + Phase Boundary Checklist + Branch Strategy + How to Resume sections. If missing, retro-fit before closing the sprint.
- [auto] S5 [ecosystem]: WSL `python` may resolve to a broken Windows pyenv shim (`/mnt/c/.../pyenv-win/shims/python` with `/bin/sh^M: bad interpreter`). Always use `.venv/bin/python` explicitly in scripts and docs; never bare `python` in WSL projects.