@/home/berto/dsm-agentic-ai-data-science-methodology/DSM_0.2_Custom_Instructions_v1.1.md

<!-- BEGIN DSM_0.2 ALIGNMENT - do not edit manually, managed by /dsm-align -->
## 1. DSM_0.2 Alignment (managed by /dsm-align)

**Project type:** Application (DSM 4.0)
**Participation pattern:** Spoke

### Session Transcript Protocol (reinforces inherited protocol)
- Append thinking to `.claude/session-transcript.md` BEFORE acting
- Output summary AFTER completing work
- Conversation text = results only
- Use Session Transcript Delimiter Format for every block:
  <------------Start Thinking / HH:MM------------>
  <------------Start Output / HH:MM------------>
  <------------Start User / HH:MM------------>
- HH:MM is 24-hour local time when the block begins; no end delimiter needed
- Append technique: read last 3 lines, use last non-empty line as anchor.
  NEVER match earlier content for mid-file insertion.
- Per-turn enforcement: a `UserPromptSubmit` hook in `.claude/settings.json`
  injects a reminder every turn. The hook enforces *occurrence*; the
  existing `validate-transcript-edit.sh` PreToolUse hook enforces *shape*.
  IDE monitoring and session-start behavioral activation are user
  affordances, not enforcement. The hook is the mechanism.
- Turn-boundary self-check: every turn begins with a transcript append. If
  your first tool call this turn was not a transcript append, the protocol
  was violated. This includes pure-reasoning turns (decision analysis,
  recommendation, trade-off comparison) that would otherwise touch no files,
  the transcript append is the one required tool call. The only exemption
  is content-trivial turns (one-word acknowledgments, single-fact
  confirmations with no new reasoning). Recover by appending a
  `[RETROACTIVE]` entry with the current HH:MM (never backdate) and a note
  explaining the gap; do not edit history.
- Process narration: thinking blocks narrate reasoning as it unfolds,
  including considered-and-rejected paths, doubts, loops, and reversals.
  Clean post-hoc summaries hide inefficiency signals that are the primary
  input to reasoning-efficiency analysis. Brevity is not the goal,
  auditability is.
- Unconditional activation: if `.claude/session-transcript.md` exists in
  the project, the protocol is active. No skill needs to activate it. The
  presence of the file is the activation signal. This rule is independent
  of `/dsm-go` Step 6 and applies to continuation sessions that defer
  from `/dsm-light-go` to `/dsm-go` mid-flight.
- Heredoc anti-pattern: when appending to the transcript via Bash, never
  use single-quoted heredoc (`<< 'EOF'`) if the content contains shell
  expansions like `$(date +%H:%M)`. Capture the timestamp into a variable
  first and use unquoted heredoc, or prefer the Edit-tool append path
  (read last 3 lines, anchor on last non-empty line).

### Pre-Generation Brief Protocol (reinforces inherited protocol)
- Four-gate model: collaborative definition (confirm threads → dependencies → packaging) → concept (explain) → implementation (diff review) → run (when applicable)
- Each gate requires explicit user approval; gates are independent
- What/why/how thinking block: before Gate 1, answer what the artifact is, why it is needed, and how it will be built, in the session transcript thinking block
- Skill self-reference: before claiming any behavior of a DSM skill (`/dsm-go`, `/dsm-wrap-up`, `/dsm-align`, etc.), read `scripts/commands/{skill-name}.md` or `~/.claude/commands/{skill-name}.md`. Do not answer "does skill X do Y?" from memory.

### Inbox Lifecycle (reinforces inherited protocol)
- After processing an inbox entry, move it to `_inbox/done/`
- Do not mark entries as "Status: Processed" while keeping them in place

### Actionable Work Items (reinforces DSM_3 planning pipeline)
- Only items in `dsm-docs/plans/` (and legacy `plan/backlog/`) are actionable work items.
- Material found elsewhere (`_reference/`, `docs/`, README, inbox, sprint plan drafts) is INPUT to the planning pipeline, not a substitute for it.
- Before suggesting implementation of anything that looks like a plan, verify that a formal BL exists in `dsm-docs/plans/`. If not, route through research → formalize → plan first.

### Punctuation
Use "," instead of "—" for connecting phrases in any language.

### Code Output Standards (reinforces Earn Your Assertions)
- Show actual values: shapes, metrics, counts, paths
- No generic confirmations: avoid "Done!", "Success!", "Data loaded successfully!"
- When uncertain, state the uncertainty; do not guess or fabricate
- Read the relevant source (file, definition, documentation) before answering questions about it; do not answer from partial knowledge
- Let results speak for themselves

### Tool Output Restraint (reinforces Take a Bite)
- Generate only what you can meaningfully process in the next step
- Comprehensive tool reports are reference material, not the analysis itself
- Run tools because the output serves the task, not because the tool is available

### Working Style (reinforces Take a Bite, Critical Thinking)
- Confirm understanding before proceeding
- Be concise in answers
- Do not generate files before providing description and receiving approval

### Cross-Repo Write Safety (reinforces Destructive Action Protocol)
- First write to any path outside this repository in a session requires explicit user confirmation
- Present the content and target path before writing; do not write cross-repo silently
- Subsequent writes to the same cross-repo target in the same session do not need re-confirmation

### Plan Mode for Significant Changes (reinforces Earn Your Assertions)
- Before implementing significant features: explore codebase, identify patterns, present plan
- Do not write or edit files until the plan is approved by the user
- This is a read-only exploration phase, not an implementation phase

### Session Wrap-Up (reinforces Know Your Context)
- When the user says "wrap up" or the session ends, use `/dsm-wrap-up`
- Before wrap-up, cross-reference sprint plan if one exists (verify all deliverables accounted for)
- At minimum: commit pending changes, push to remote, update MEMORY.md
- Create a handoff document if complex work remains pending

### App Development Protocol (reinforces inherited protocol)
- Explain why before each action
- Create files via Write/Edit tools; user approves via permission window
- Wait for user confirmation before proceeding to next step
- Build incrementally: imports → constants → one function → test → next function
<!-- END DSM_0.2 ALIGNMENT -->

## 2. Participation Pattern

Spoke project in the DSM ecosystem. Governance artifacts route through DSM Central.

## 3. Project Type

Application project (DSM 4.0). LangGraph-based conversational AI with Python backend, Streamlit UI, ChromaDB vector store, and MLflow evaluation.

## 4. Project Specific

**Project:** Heating Systems Conversational Assistant
**Objective:** LangGraph-based conversational AI for residential heating domain, RAG over existing 6K-line documentation. Portfolio project targeting AI Engineer roles in energy/utility sector.
**Alignment:** Agentic workflows, LLM reasoning, RAG pipelines, evaluation frameworks, prompt engineering, German C1+

### Structure

```
_reference/          # Sprint plans and interaction design documents
src/                 # Application code (LangGraph, tools, RAG pipeline)
tests/               # pytest test suite
```

### Knowledge Base (external, read-only)

- `/home/berto/_projects/dsm-residential-heating-ds-guide/` — 6 markdown documents (~5,800 lines) covering German heating standards, ML/DS applications, MLOps, technical stack, applied scenarios
- `/home/berto/_projects/dsm-residential-energy-apps/` — Companion Streamlit app (heating curve simulator, DIN EN 12831, VDI 6030), source for deterministic tool logic

### Tech Stack

| Component | Technology |
|-----------|-----------|
| Orchestration | LangGraph |
| LLM | OpenAI / Ollama (configurable) |
| Vector store | ChromaDB |
| Embeddings | HuggingFace multilingual-e5 or OpenAI |
| UI | Streamlit |
| Evaluation | MLflow |
| Testing | pytest |
| Deployment | Docker |

### Sprint Plan

3 sprints defined in `_reference/sprint-plan.md`:
1. Conversation engine + deterministic tools + Streamlit chat UI
2. RAG pipeline + knowledge retrieval over heating guide
3. Evaluation framework + production polish

### Domain Context

German residential heating systems. Key domain terms: Heizkennlinie (heating curve), Vorlauftemperatur (flow temperature), Spreizung (temperature spread), hydraulischer Abgleich (hydraulic balancing). Agent must handle bilingual (EN/DE) queries and respond in the user's language.
