# Feedback: Cross-repo PR Definition of Ready not formalized

**Date:** 2026-05-07
**Source session:** Heating Systems S13
**Scope:** ecosystem (applies to any DSM spoke that contributes via PR to external public repos)
**Type:** lesson + proposed protocol addition

## Observed pattern

S13 produced three external-repo artifacts: PR `deepset-ai/haystack-integrations#473`, PR `deepset-ai/haystack#11268`, and upstream issue `ollama/ollama-python#663`. The PRs were opened against repos with formal contribution requirements (deepset/haystack has `CONTRIBUTING.md`, `.github/pull_request_template.md`, and a `release-notes-required` CI check) but the spoke's local protocol did NOT prompt the agent to read those before drafting.

The contribution went through cross-repo write-safety gates and a Pre-Generation Brief Protocol four-gate review. None of those caught:

- Missing release note YAML (deepset's CONTRIBUTING.md mandates one; CI fails without it).
- PR body using free-form description instead of the project's 5-section template.
- A behavioral claim ("text and tool deltas mutually exclusive within a single generation step") inferred from one directive prompt without a falsification spike.

A user audit ("how do we know what we have pushed to the PRs is correct? what was our Definition of Ready?") surfaced the gap mid-session. All three items were then retroactively fixed: hatch installed, release note generated via `hatch run release-note ...`, PR body rewritten to template, backfill spike with 6 prompts confirmed the mutual-exclusion claim.

## Why this is ecosystem-scoped, not project-scoped

The pattern is not specific to the heating-systems spoke or the deepset target. ANY DSM spoke that opens a PR against a heavily-maintained public OSS project (haystack, langgraph, langchain, llamaindex, mlflow, etc.) faces the same shape of gap. The local Cross-Repo Write Safety protocol only gates *that* the agent presents content before writing; it does NOT gate *what* the agent should know about the target's contribution requirements before drafting the content.

## Proposed protocol addition

Add a `Read-Before-Draft` step to the cross-repo PR pipeline (as a Pre-Generation Brief Protocol Gate 0, or as a sub-step of the existing collaborative-definition gate). Before drafting any PR body, fetch and inspect:

1. `<target-repo>/CONTRIBUTING.md` and any nested contribution guides (e.g., `<target>/docs-website/CONTRIBUTING.md`)
2. `<target-repo>/.github/pull_request_template.md` if present
3. `<target-repo>/.github/workflows/*.yml` files whose names suggest PR gates (test-*, lint-*, check-*, *required*)
4. The target repo's recent merged PRs of similar shape (1-2 examples) to observe the maintainer's actual taste

Output of the Read-Before-Draft step should be a checklist the agent applies during drafting:

- [ ] PR title format requirements (conventional commits / specific prefixes)
- [ ] PR body structure (free-form vs templated; if templated, exact section list)
- [ ] Release note / changelog requirement (and how to generate one)
- [ ] Required CI checks the PR will face
- [ ] Code-of-conduct / CLA requirements
- [ ] Test-evidence expectations

The agent presents this checklist to the user as part of the Pre-Generation Brief, before drafting the PR body. The PR body is then drafted *against* this checklist, not against an internal default.

## Cost

The Read-Before-Draft step adds 5-10 minutes per first-time-target. Subsequent PRs to the same target reuse the cached checklist. Worth it: in S13, the audit + retroactive fix took ~25 minutes; doing it preemptively would have taken 10.

## Suggested DSM artifact

A new section in DSM_0.2 (or its module on cross-repo work) titled "Read-Before-Draft for OSS contributions," capturing the four sources (CONTRIBUTING.md, PR template, workflows, recent merged PRs) and the six checklist categories above. Optionally, a `/dsm-pr-readiness` skill that automates fetching the four sources and produces the checklist.

## References

- S13 transcript: in spoke at `.claude/session-transcript.md`
- The audit moment: ~16:00 user prompt "how do we know that what we have pushed to the PRs is correct?"
- The retroactive fix sequence: ~16:08-16:13 (release note via hatch + PR body rewrite + push)
- Reasoning-lessons-S13 entry: `[auto] S13 [pattern]: Before opening a PR on a heavily-developed OSS project, READ the project's CONTRIBUTING.md...`
