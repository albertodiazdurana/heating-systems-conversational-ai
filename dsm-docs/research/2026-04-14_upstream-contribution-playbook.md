# Upstream Contribution Playbook (adapted for Haystack `OllamaChatGenerator`)

**Purpose:** Method reference for the Sprint 2 Haystack contribution opportunity, distilled from `dsm-graph-explorer`'s FalkorDBLite playbook (2026-04-13 inbox response) and adapted to this project's context.
**Target outcome:** When the Sprint 2 Haystack spike runs, this document tells us how to turn spike results into an upstream artifact (docs PR, issue, or both).
**Status:** Done (captured reference; activate at Sprint 2 start)
**Date Completed:** 2026-04-14
**Source:** `dsm-graph-explorer` inbox response to our 2026-04-07 playbook request

---

## Core pattern: capability experiment as contribution pipeline

A capability experiment (DSM 4.0 §4) validates an external tool for project use. Its primary output is a pass/fail decision. When the tool has documentation or behavior gaps, the secondary output is a contribution opportunity, the experiment artifacts become the evidence base for an upstream issue or PR.

The pipeline:

```
capability experiment (runnable script)
        |
        v
deep-dive research note (gaps systematized)
        |
        v
gap triage (docs? bug? local workaround?)
        |
        v
issue first (gauge maintainer response)
        |
        v
PR (docs or fix), if issue lands or if time-boxed wait expires
```

This is the second time we have seen this pattern in the ecosystem (first: graph-explorer x FalkorDBLite, now: this project x Haystack). Not yet a DSM-core pattern; worth tracking for a third data point.

## Applying it here: Haystack `OllamaChatGenerator` tool-calling

**Known on entry:** source code accepts `tools=[...]` (confirmed at `haystack-core-integrations/.../ollama/chat_generator.py`), marketing docs are silent. Expected path is a **docs PR with a working example**.

### Step 1: Spike as capability experiment

Write a standalone script (Sprint 2 early) that:

- Instantiates `OllamaChatGenerator(model="qwen2.5:7b", tools=[...])` with two or three real tool definitions (reuse our unit_converter, standard_lookup, heating_curve signatures)
- Runs 3-5 representative queries: pure chit-chat, tool-call-required, ambiguous, bilingual (EN + DE)
- Records per-query: did the generator emit a tool-call message; was the tool call well-formed; did the subsequent turn incorporate the tool output
- Outputs a plain-text pass/fail log + any stack traces

Location: `src/experiments/exp_haystack_tools.py` or similar. Primary job: inform the Sprint 2 architecture decision.

### Step 2: Deep-dive note

Whatever the spike result:

- **Works end-to-end:** write a short note (`dsm-docs/research/YYYY-MM-DD_haystack-ollama-tools-spike.md`) covering what the full working pattern is, any quirks (message-format gotchas, streaming caveats, function-schema translation details), and why this was worth documenting upstream.
- **Works with caveats:** same note, caveats section foregrounded.
- **Does not work:** note becomes the issue reproduction case, not a docs PR prep doc.

### Step 3: Gap triage

For each empirically discovered behavior not in the docs:

- **Documentation gap:** correct usage exists but is not findable. Upstream as docs (PR or issue with suggested wording). Example: tool-parameter type coercion rules.
- **Bug:** correct usage still fails. Upstream as issue with reproduction. Example: tool-call message dropped on streaming mode.
- **Local-only:** our specific integration pattern (e.g., wrapping as a LangChain `@tool`). Keep local. The *existence* of a hybrid integration need may still be worth surfacing as a separate doc.

Heuristic: if the gap would catch the next user doing the same thing, it is worth contributing.

### Step 4: Issue first

Haystack is more active than FalkorDBLite, so response times should be measured in days not months, but the heuristic still applies: open an issue before writing a PR.

Issue content:

- Exact version (`haystack-ai` + `ollama-haystack` + Ollama server + model)
- Minimal reproducible example (10-30 lines)
- What we expected vs what we found
- Proposed fix or docs wording (makes it easy for the maintainer to say yes)
- A line noting we are happy to submit a docs PR / fix PR if this direction is accepted

For our case, if the spike passes and we think the docs should show `tools=[...]` usage, frame the issue as "suggestion: add tool-calling example to OllamaChatGenerator docs" with a draft example attached.

### Step 5: PR (docs or fix)

- **Docs PR:** the spike script becomes the cookbook example. Place wherever the repo convention puts examples (likely `integrations/ollama/examples/` or a docs site MDX page). One clean working example beats a long prose explainer.
- **Fix PR:** only if the issue response was positive AND the fix is bounded AND we have bandwidth.

### Step 6: Blog capture

Journal entry capturing the narrative: spike motivation, what we found, what we contributed, maintainer interaction. Already started in `dsm-docs/blog/journal.md` (2026-04-14 entry).

## Decision heuristics inherited from graph-explorer

- **Contribute the *need*, not just the workaround.** Our fixture patterns are local; the fact that fixtures are needed at all may be upstream-worthy.
- **Specific suggestions beat vague asks.** "Docs need improvement" goes nowhere; "add this cookbook example" gives the maintainer a one-click yes.
- **Time-box the issue-before-PR wait.** GE waited a month. We should wait ~2 weeks on a more active project, then proceed with the PR anyway as a publicly visible reference.
- **Maintainer non-response is not a dead end.** A publicly open issue or unmerged PR still serves future users who search the repo.

## Pass-through to Sprint 2 plan

Referenced from `dsm-docs/decisions/2026-04-07_orchestration-framework.md` under "Contribution goal". When Sprint 2 starts, the plan doc should add a "contribution subtask" section pointing here.

## References

- `~/_projects/heating-systems-conversational-ai/_inbox/done/2026-04-13_dsm-graph-explorer_contribution-playbook.md` (original GE response; moved to done/ on 2026-04-14 after capture)
- `dsm-docs/decisions/2026-04-07_orchestration-framework.md` (contribution framing, §"Contribution goal")
- `dsm-docs/plans/2026-04-07_e2e_hybrid_backbone.md` (Sprint 2 Haystack scope)
- DSM 4.0 §4 (capability experiments)
