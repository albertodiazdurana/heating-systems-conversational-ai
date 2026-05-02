# Haystack Ollama integration: tool-calling doc gap , issue draft

**Purpose:** draft GitHub issue text for Sprint 2 Phase 1 T6.
**Target repo:** `deepset-ai/haystack-core-integrations`
**Status:** draft, awaiting filing decision.
**Verification date:** 2026-04-29 (live deepset doc URLs); 2026-05-01 (code example empirically verified against pinned Haystack, two fixes applied: `Tool.from_function` → `create_tool_from_function` (the original was the wrong API name); added `temperature=0.0` + directive prompt so the example reliably emits tool_calls instead of free-form JSON-shaped text. Verification log: `/tmp/verify_haystack_ollama_doc_example.py`, observed `tool_calls=[ToolCall(tool_name='get_weather', arguments={'city': 'Berlin'}, ...)]`).
**Provenance (internal only):** evidence assembled in
`~/_projects/haystack-magic/dsm-docs/research/2026-04-29_ollama-tool-calling-doc-gap.md`.
This provenance line is repo-internal and is not part of the outgoing issue text.

---

## Filing notes

- **Suggested title:** Docs: surface tool-calling on the Ollama integration landing page
- **Suggested labels:** `documentation`; add `integrations:ollama` if that label exists in the repo.
- **Verified example (2026-05-01):** the code block in Section 3 was run locally
  against pinned Haystack + `llama3.1:8b` via Ollama. Two corrections applied:
  the public API is `create_tool_from_function`, not `Tool.from_function`; and
  `temperature=0.0` + a directive prompt are required for the example to
  reliably emit `tool_calls` instead of free-form JSON-shaped text in `.text`.
  Both corrections illustrate exactly the discoverability problem the issue
  raises, the failure modes a reader would hit are the failure modes worth
  surfacing in the docs.
- **Post-filing follow-up:** if maintainers welcome a docs PR, send a small one
  with the example slotted into the integration landing page source.

---

## Issue text

`--- Issue text begins ---`

### Observation

`OllamaChatGenerator` supports tool calling in code, but the documentation surfaces describe it unevenly:

- **Integration landing page** (`haystack.deepset.ai/integrations/ollama`): shows generation, chat, and embedding examples. No tool-calling example.
- **Component reference** (`docs.haystack.deepset.ai/docs/ollamachatgenerator`): has a "Tool Support" section with one mixed `Tool` + `Toolset` example. Does not cover streaming-with-tools or `tool_choice`.
- **API reference** (`docs.haystack.deepset.ai/reference/integrations-ollama`): shows the full constructor signature, including `tools: ToolsType | None = None`.

The capability is in the code path. The discoverability surface is the issue.

### Why it matters

A practitioner evaluating *"can I run tool calling on a local Ollama model in Haystack?"* lands on the integration page first. Finding no example, they tend to conclude the integration does not support it, and reach for an alternative orchestrator. That sends people away from work Haystack already does.

### Concrete suggestion

Add one tool-calling example to the integration landing page. Minimal shape:

```python
from haystack.tools import create_tool_from_function
from haystack_integrations.components.generators.ollama import OllamaChatGenerator
from haystack.dataclasses import ChatMessage

def get_weather(city: str) -> str:
    """Get current weather for a city."""
    return f"Sunny, 22°C in {city}"

weather_tool = create_tool_from_function(get_weather)

generator = OllamaChatGenerator(
    model="llama3.1:8b",
    generation_kwargs={"temperature": 0.0},
    tools=[weather_tool],
)

response = generator.run(
    messages=[ChatMessage.from_user(
        "What's the weather in Berlin? Use the get_weather tool."
    )]
)
print(response["replies"][0].tool_calls)
# -> [ToolCall(tool_name='get_weather', arguments={'city': 'Berlin'}, ...)]
```

This single addition closes the worst surface.

Optional follow-up on the component reference page: a streaming-with-tools snippet and a `tool_choice` example (if/when supported). Lower priority, separable.

Happy to send a docs PR if you can point me at the source for the integration landing page.

`--- Issue text ends ---`

---

## Word count

Issue body (Observation + Why it matters + Concrete suggestion, including the code block): ~260 words. Within the 250–350 target.
