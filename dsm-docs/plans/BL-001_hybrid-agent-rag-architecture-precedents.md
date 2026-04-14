# BACKLOG-001 — Hybrid Agent + RAG Architecture: Precedent Research

**Status:** Implemented by parallel session #4.1
**Priority:** Medium (informs Sprint 2 scoping; does not block Sprint 1)
**Date Created:** 2026-04-14
**Date Completed:** 2026-04-14
**Deliverable:** `dsm-docs/research/2026-04-14_hybrid-architecture-precedents.md`
**Outcome summary:** 4 strict-lens precedents found (Funderburk Packt book 2025; Panta Medium 2026; scrapegraphai multi-agent post; LlamaIndex `QueryEngineTool` canonical) + 1 near-miss (Elastic/LangGraph direct-node). Pattern is established in published tutorials with a consistent boundary contract (`RAG-framework.query_engine` → LangChain `@tool` → LangGraph `ToolNode`) but lacks academic or official-vendor canonization. Not novel-ish; no full decision-record addendum needed, only a one-paragraph validation-criteria note added to `dsm-docs/decisions/2026-04-07_orchestration-framework.md`. Journal entry added.
**Origin:** Session 4 follow-up to `dsm-docs/decisions/2026-04-07_orchestration-framework.md`
**Author:** albertodiazdurana (with Claude)
**Intended execution:** Parallel DSM session (`/dsm-parallel-session-go`); read-only research with bounded writes

## Research question

Are there published precedents (articles, blog posts, OSS repos, conference talks) for hybrid LLM architectures using **one framework as the agent layer** and a **different framework as the RAG subsystem**, integrated through a **single tool-call boundary**? If so, what do their boundary contracts look like, and what tradeoffs do they report?

The orchestration decision (2026-04-07) chose this pattern (LangGraph agent + Haystack RAG behind a LangChain `@tool`) on internal reasoning about loose coupling and "each framework where strongest." We do not yet know whether this pattern is common, rare, or essentially novel in published work. The answer informs:

- Sprint 2 scoping (can we lean on existing examples, or are we writing the reference?)
- Whether the integration pattern itself is contributable upstream (companion to the `OllamaChatGenerator` docs PR opportunity)
- Validation criteria in the orchestration decision record

## Method

### Lens (apply in order)

1. **Strict lens (primary):** agent-framework + RAG-framework with one tool-call boundary, where the two frameworks are clearly separable (different vendors, different abstractions, different state models).
2. **Lenient lens (fallback if strict yields fewer than 3 precedents):** any hybrid LLM-stack integration with documented loose-coupling rationale, including framework + custom-RAG, framework + commercial RAG service, or two RAG-only frameworks composed.

### Targeted sources

- arXiv: search "agent RAG architecture", "hybrid LLM framework", "tool-augmented retrieval"
- Vendor blogs: deepset (Haystack), LangChain, LlamaIndex, AnyScale, Together AI
- GitHub topic + repo search: `langgraph haystack`, `langchain llamaindex agent`, repos with both `agents/` and `rag/` top-level directories
- Newsletters / publications: Towards Data Science, Substack ML newsletters (Latent Space, AI Engineer)
- Cookbooks: Anthropic, OpenAI, Cohere
- Conference talks 2025-2026: NeurIPS, AI Engineer Summit, EMNLP, RAG-focused workshops, PyData

### Per-precedent capture (when one is found)

For each candidate, record:

- Source (link, author, date)
- Stack (which framework on which layer)
- Boundary contract (function signature, message format, state ownership)
- Reported pros / cons / lessons
- Whether the project is production, demo, or pedagogical

### Soft scope cap

~2 hours of research time / ~10 sources substantively reviewed. If still under threshold for a confident finding, narrow the lens or pivot to "why is this rare" framing.

## Success criteria

- ≥3 substantive precedents under the strict lens, OR
- ≥5 under the lenient lens, OR
- Confident "novel-ish" finding (zero strict precedents, ≤2 lenient, with reasoned hypothesis why: e.g., framework lock-in default, learning cost, lack of pedagogical materials, opinionated framework prescriptions)

## Outputs

- `dsm-docs/research/2026-04-XX_hybrid-architecture-precedents.md` — main deliverable (Status: Done on completion)
- `dsm-docs/blog/journal.md` — one entry capturing what was learned (narrative + lesson)
- **If novel-ish:** addendum to `dsm-docs/decisions/2026-04-07_orchestration-framework.md` Validation criteria section noting "no clear precedent found; pattern is contributable as a reference example"
- **This BL:** moved to `dsm-docs/plans/done/` with Status: Done and Date Completed on completion (`/dsm-backlog-done` if available)

## Out of scope

- Implementing anything (this is research-only)
- Re-opening the orchestration decision (the decision stands; this research informs future positioning)
- Comparing framework features in general (already covered in `dsm-docs/research/2026-04-07_haystack-vs-langgraph-deepened.md`)

## Parallel-session safety

- Read-research; writes confined to: the new research doc, the blog journal entry, optionally the decision-record addendum, and this BL's status update
- No edits to source code, pyproject.toml, or Sprint 1/2 plan files
- Cross-repo writes: none expected
- Branch: shared session branch (`session-4/2026-04-14`) per `/dsm-parallel-session-go` convention

## References

- `dsm-docs/decisions/2026-04-07_orchestration-framework.md` — the architecture under research
- `dsm-docs/research/2026-04-07_haystack-vs-langgraph-deepened.md` — prior framework comparison (input)
- `dsm-docs/research/2026-04-07_hybrid-langgraph-haystack-best-practices.md` — prior best-practices research (input)
- `dsm-docs/plans/2026-04-07_e2e_hybrid_backbone.md` — current backbone plan
