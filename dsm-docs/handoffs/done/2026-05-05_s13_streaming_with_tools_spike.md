**Date Completed:** 2026-05-07
**Outcome Reference:** Consumed at session 14 start

# S13 Spike: streaming + tool calls (OllamaChatGenerator)

**Date:** 2026-05-06T14:42:21+00:00
**Model:** `llama3.1:8b`
**Base URL:** `http://localhost:11434`
**Result:** PASS

## Setup

- `OllamaChatGenerator(temperature=0.0, tools=[get_weather], streaming_callback=cb)`
- Single user message: "What's the weather in Berlin? Use the get_weather tool."

## Chunk timeline

Total chunks fired: **2**

| # | text preview | tool_delta |
|---|---|---|
| 1 | `` | True |
| 2 | `` | False |

## Final reconstructed ChatMessage

- `role`: `ChatRole.ASSISTANT`
- `text`: `None`
- `tool_calls` length: 1
- `tool_calls[0].tool_name`: `get_weather`
- `tool_calls[0].arguments`: `{'city': 'Berlin'}`
- `meta.finish_reason`: `stop`

## Use

Evidence base for the planned doc PR adding a `### Streaming with Tools`
section to `ollamachatgenerator.mdx` in `deepset-ai/haystack`.
