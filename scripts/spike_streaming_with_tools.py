"""S13 spike: OllamaChatGenerator streaming + tool calls combined.

Empirical evidence base for the planned doc PR adding a "Streaming with
Tools" section to ollamachatgenerator.mdx in deepset-ai/haystack.

Verifies:
1. streaming_callback fires for each chunk during the run
2. final ChatMessage on replies[0] reconstructs tool_calls correctly
3. tool_calls[0].tool_name == "get_weather"
4. tool_calls[0].arguments contains the expected city

Run: .venv/bin/python scripts/spike_streaming_with_tools.py

Reads OLLAMA_MODEL from env (default llama3.1:8b). Requires
'ollama pull llama3.1:8b' and the daemon reachable at OLLAMA_BASE_URL
(default http://localhost:11434). Writes evidence to
dsm-docs/handoffs/2026-05-05_s13_streaming_with_tools_spike.md.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from haystack.dataclasses import ChatMessage  # noqa: E402
from haystack.dataclasses.streaming_chunk import StreamingChunk  # noqa: E402
from haystack.tools import create_tool_from_function  # noqa: E402
from haystack_integrations.components.generators.ollama import (  # noqa: E402
    OllamaChatGenerator,
)


def get_weather(city: str) -> str:
    """Get current weather for a city."""
    return f"Sunny, 22°C in {city}"


def main() -> int:
    model = os.environ.get("OLLAMA_MODEL", "llama3.1:8b")
    base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

    chunks: list[StreamingChunk] = []

    def callback(chunk: StreamingChunk) -> None:
        chunks.append(chunk)
        text_preview = (chunk.content or "").replace("\n", "\\n")[:60]
        tool_delta = bool(chunk.tool_calls) if chunk.tool_calls is not None else False
        print(
            f"  chunk #{len(chunks):>3}  "
            f"text={text_preview!r:<64}  tool_delta={tool_delta}"
        )

    weather_tool = create_tool_from_function(get_weather)

    generator = OllamaChatGenerator(
        model=model,
        url=base_url,
        generation_kwargs={"temperature": 0.0},
        tools=[weather_tool],
        streaming_callback=callback,
    )

    print(f"=== Spike: streaming + tool calls on {model} ===")
    print(f"base_url: {base_url}")
    print(f"prompt: 'What's the weather in Berlin? Use the get_weather tool.'")
    print()
    print("Streaming chunks:")

    response = generator.run(
        messages=[
            ChatMessage.from_user(
                "What's the weather in Berlin? Use the get_weather tool."
            )
        ]
    )

    final_message: ChatMessage = response["replies"][0]

    print()
    print("=== Final reconstructed ChatMessage ===")
    print(f"role: {final_message.role}")
    print(f"text: {final_message.text!r}")
    print(f"tool_calls: {final_message.tool_calls}")
    print(f"meta keys: {list(final_message.meta.keys())}")
    if "finish_reason" in final_message.meta:
        print(f"finish_reason: {final_message.meta['finish_reason']}")

    # Verdict
    print()
    print("=== Verdict ===")
    chunks_fired = len(chunks) > 0
    tool_calls = final_message.tool_calls or []
    tool_name_ok = bool(tool_calls) and tool_calls[0].tool_name == "get_weather"
    args = tool_calls[0].arguments if tool_calls else {}
    city_ok = "berlin" in str(args).lower()

    print(f"  chunks fired: {len(chunks)} ({'PASS' if chunks_fired else 'FAIL'})")
    print(
        f"  tool_calls reconstructed: {len(tool_calls)} "
        f"({'PASS' if tool_calls else 'FAIL'})"
    )
    print(f"  tool name == get_weather: {'PASS' if tool_name_ok else 'FAIL'}")
    print(f"  argument contains 'berlin': {'PASS' if city_ok else 'FAIL'}")

    overall = chunks_fired and tool_calls and tool_name_ok and city_ok
    print(f"  overall: {'PASS' if overall else 'FAIL'}")

    # Evidence file
    evidence_path = (
        REPO_ROOT / "dsm-docs/handoffs/2026-05-05_s13_streaming_with_tools_spike.md"
    )
    write_evidence(evidence_path, model, base_url, chunks, final_message, overall)
    print()
    print(f"Evidence written to: {evidence_path.relative_to(REPO_ROOT)}")

    return 0 if overall else 1


def write_evidence(
    path: Path,
    model: str,
    base_url: str,
    chunks: list[StreamingChunk],
    final_message: ChatMessage,
    overall: bool,
) -> None:
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    tool_calls = final_message.tool_calls or []

    lines = [
        "# S13 Spike: streaming + tool calls (OllamaChatGenerator)",
        "",
        f"**Date:** {timestamp}",
        f"**Model:** `{model}`",
        f"**Base URL:** `{base_url}`",
        f"**Result:** {'PASS' if overall else 'FAIL'}",
        "",
        "## Setup",
        "",
        "- `OllamaChatGenerator(temperature=0.0, tools=[get_weather], streaming_callback=cb)`",
        "- Single user message: \"What's the weather in Berlin? Use the get_weather tool.\"",
        "",
        "## Chunk timeline",
        "",
        f"Total chunks fired: **{len(chunks)}**",
        "",
        "| # | text preview | tool_delta |",
        "|---|---|---|",
    ]
    for i, chunk in enumerate(chunks, start=1):
        text_preview = (chunk.content or "").replace("\n", "\\n").replace("|", "\\|")[:50]
        tool_delta = bool(chunk.tool_calls) if chunk.tool_calls is not None else False
        lines.append(f"| {i} | `{text_preview}` | {tool_delta} |")

    lines.extend(
        [
            "",
            "## Final reconstructed ChatMessage",
            "",
            f"- `role`: `{final_message.role}`",
            f"- `text`: `{final_message.text!r}`",
            f"- `tool_calls` length: {len(tool_calls)}",
        ]
    )
    for i, tc in enumerate(tool_calls):
        lines.extend(
            [
                f"- `tool_calls[{i}].tool_name`: `{tc.tool_name}`",
                f"- `tool_calls[{i}].arguments`: `{tc.arguments}`",
            ]
        )

    if "finish_reason" in final_message.meta:
        lines.append(f"- `meta.finish_reason`: `{final_message.meta['finish_reason']}`")

    lines.extend(
        [
            "",
            "## Use",
            "",
            "Evidence base for the planned doc PR adding a `### Streaming with Tools`",
            "section to `ollamachatgenerator.mdx` in `deepset-ai/haystack`.",
            "",
        ]
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


if __name__ == "__main__":
    sys.exit(main())
