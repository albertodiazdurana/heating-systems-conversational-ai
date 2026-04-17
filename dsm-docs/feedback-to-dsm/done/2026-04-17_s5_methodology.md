# Methodology Feedback — Session 5

**Date:** 2026-04-17
**Session:** 5 (Heating Systems Conversational AI)
**Type:** Methodology Observation
**Priority:** Medium

---

## Lesson 1: Evidence-strength scale for technology selection

### Context

Sprint 1 step 11 needed a default LLM. The Sprint 1 plan and prior research
doc (`2026-04-07_langgraph-best-practices.md §4`) recommended `qwen2.5:7b` /
`llama3.1:8b` based on a survey of *what 2026 tutorials default to* (LangChain
forum, Ollama tutorials, Haystack source defaults). The user flagged this
"convenience trail" as a methodological gap before Sprint 1 step 11 ran.

### Pattern observed

When the agent re-did the model selection as a Phase 0.5 research artifact, it
introduced an explicit **evidence-strength scale** applied uniformly across
candidates:

| Evidence strength | Example |
|---|---|
| **Strong** | Third-party published benchmark with method + score |
| **Medium** | Vendor's own published benchmark in a technical report |
| **Weak** | Vendor model-card capability claim without a number |
| **Anecdotal** | Community reproduction in GitHub issues / HF discussions |
| **None** | No information found in primary sources |

The first ranking treated "vendor claims tool-calling support" the same as
"third-party benchmark scores model on tool-calling at X." Wrong. The
re-ranking, weighted by evidence strength, produced a different and
better-defended result (the only candidate with both hard-filter benchmarks
*measured* and passing won the primary slot, even though it lost the
"convenient hardware fit" tiebreaker).

### Why this is generalizable beyond model selection

The same vendor-claim-vs-benchmark gap appears in every technology-selection
exercise: framework choice, vector-store selection, embeddings model,
deployment target, observability stack. The pattern that emerged in this
session:

1. **List candidates** (don't pre-filter)
2. **Define hard criteria** (operational, not aspirational)
3. **For each candidate × criterion cell, classify evidence strength explicitly** before scoring
4. **Eliminate strictly-dominated candidates** (B is dominated by A iff A ≥ B on every measurable criterion at the same cost)
5. **Surface zero-evidence candidates honestly** (don't promote them to "fits well" just because they look good on paper)
6. **Recommend a cascade**, not a single choice (primary → fallback → escape hatch)

### Suggestion for DSM

Add an **Evidence-Strength Scale** subsection to DSM_0.2 Module D (Phase 0.5:
Research and Grounding), or to the Plan Pipeline section that governs
tech-stack decisions. The scale itself is small (5 levels), but the
methodological commitment to apply it uniformly is the value-add.

The pattern would integrate naturally with the existing `take-a-bite` and
`earn-your-assertions` principles: take-a-bite limits the scope of any one
candidate's evaluation; earn-your-assertions demands citations; the
evidence-strength scale makes the citation *quality* visible.

### Cited as evidence

The full applied case is in
[`dsm-docs/research/2026-04-17_local-model-selection_research.md`](../research/2026-04-17_local-model-selection_research.md)
(607 lines, 35+ cited sources). §0 of that doc spells out the scale; §3
applies it to a 7×6 candidate grid; §4 documents four strict-domination
eliminations; §5 produces the cascade.

---

## Lesson 2: "Latency is hard" vs "latency is bounded by an escape hatch"

### Context

Same Sprint 1 step 11 model selection. The agent's first ranking treated
"VRAM fit" as a hard filter, which pushed `qwen3:4b` (fits cleanly) to the
primary slot over `llama3.1:8b` (partial CPU offload, slower).

### Pattern observed

The user's pushback ("I want a different ranking based on the evidence")
forced the agent to re-examine which constraints were *actually* hard.

The plan's exit criteria explicitly accepted an OpenAI fallback if local
performance was unacceptable. That meant:

- **Latency bounded by escape hatch:** "model is too slow" has a well-defined
  fallback (switch provider). Cost = soft.
- **Tool-call failure bounded by escape hatch:** same.
- **License failure NOT bounded by escape hatch:** non-commercial license =
  hard-cost, no escape. Cost = hard.
- **Wrong-language output NOT bounded by escape hatch:** OpenAI English
  default does not solve a German-quality problem. Cost = hard.

Once the constraints were re-classified, the ranking inverted: evidence
quality (which was strongest for `llama3.1:8b`) won over hardware fit (which
was best for `qwen3:4b`).

### Suggestion for DSM

When a plan defines a fallback or escape hatch, the **constraints it covers
become soft**, even if they look hard in isolation. Treating soft constraints
as hard distorts the ranking toward "cheap to satisfy" rather than "best
evidence." A pre-flight check during research synthesis: *for each criterion,
is there a documented fallback in the plan? If yes, classify as soft.*

This pairs with the evidence-strength scale (Lesson 1): together they prevent
the "popular tutorial default + fits the hardware = primary recommendation"
failure mode that the prior research had fallen into.

---

## Lesson 3: Pre-Generation Brief gates work, but agents need to apply them to themselves

### Context

This session's user explicitly asked for the four-gate model (definition →
concept → implementation → run) at multiple decision points. The agent used
it cleanly when *generating artifacts* (research doc: Gate 1 brief, Gate 2
section walkthrough, Gate 3 diff review). But the agent's first model ranking
(Gate 2 walkthrough of the research doc) was internally inconsistent — and
only the user's pushback ("I want a different ranking") triggered a Gate 2
revision.

### Pattern observed

The four-gate model controls when *files* are written. It does *not* control
when *recommendations* shift. Once at Gate 2, the agent presented a
recommendation as if it were the conclusion of evidence analysis, not a
proposal for review. The Gate 2 framing should be: "Here's what I'd recommend
based on the evidence; here's the evidence; here's the reasoning chain.
Pushback expected."

When the user did push back, the agent re-ran the analysis correctly. But
without the pushback, it would have shipped the wrong recommendation in the
research doc.

### Suggestion for DSM

The Pre-Generation Brief Protocol could add an explicit micro-step at Gate 2:
"**Surface the strongest counter-evidence to your own recommendation before
asking for approval.**" In this session that would have been: "Note that the
recommendation favors a model that does NOT fit cleanly in VRAM; the cleaner-
fit alternatives have weaker evidence; pushback on the trade-off welcome."

This is adjacent to the existing Critical Thinking principle but is procedural
rather than dispositional: it forces the counter-evidence into the *Gate 2
output* rather than relying on the agent to volunteer it.

---

## Source

This session: 2026-04-17, branch `session-5/2026-04-17`. Research doc:
`dsm-docs/research/2026-04-17_local-model-selection_research.md`
(commit `52c19cb`). Plan update: commit `1f373f2`.
