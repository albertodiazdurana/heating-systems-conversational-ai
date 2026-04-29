# Haystack Ollama integration: tool-calling doc gap , issue draft

**Purpose:** draft GitHub issue text for Sprint 2 Phase 1 T6.
**Target repo:** `deepset-ai/haystack-core-integrations`
**Status:** draft, awaiting filing decision.
**Verification date:** 2026-04-29 (live deepset doc URLs verified on this date).
**Provenance (internal only):** evidence assembled in
`~/_projects/haystack-magic/dsm-docs/research/2026-04-29_ollama-tool-calling-doc-gap.md`.
This provenance line is repo-internal and is not part of the outgoing issue text.

---

## Filing notes

- **Suggested title:** Docs: surface tool-calling on the Ollama integration landing page
- **Suggested labels:** `documentation`; add `integrations:ollama` if that label exists in the repo.
- **Untested example:** the code block in Section 3 is illustrative, drawn from
  the public API reference signature. Run it locally before filing to confirm
  imports, model availability, and response shape.
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
from haystack.tools import Tool
from haystack_integrations.components.generators.ollama import OllamaChatGenerator
from haystack.dataclasses import ChatMessage

def get_weather(city: str) -> str:
    """Get current weather for a city."""
    return f"Sunny, 22°C in {city}"

weather_tool = Tool.from_function(get_weather)

generator = OllamaChatGenerator(model="llama3.1", tools=[weather_tool])

response = generator.run(
    messages=[ChatMessage.from_user("What's the weather in Berlin?")]
)
print(response["replies"][0].tool_calls)
```

This single addition closes the worst surface.

Optional follow-up on the component reference page: a streaming-with-tools snippet and a `tool_choice` example (if/when supported). Lower priority, separable.

Happy to send a docs PR if you can point me at the source for the integration landing page.

`--- Issue text ends ---`

---

## Word count

Issue body (Observation + Why it matters + Concrete suggestion, including the code block): ~260 words. Within the 250–350 target.
