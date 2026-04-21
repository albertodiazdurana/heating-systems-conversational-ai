"""
Sprint 2 Phase 1 spike: Haystack tool-calling with Ollama.

Tests whether Haystack's Tool API works with llama3.1:8b locally,
which determines whether the RAG subsystem can be wrapped as a @tool
behind the existing LangGraph agent boundary.

Outcome classifications:
  A - Full: tool call issued by model, result returned correctly
  B - Partial: generator works, but model does not emit tool calls
              (model capability gap or prompt format issue)
  C - Broken: generator fails to connect or crashes

Run:
  uv run python scratch/haystack_ollama_tools_spike.py
"""

import sys

# ── Versions ──────────────────────────────────────────────────────────────────
import haystack
import haystack_integrations

print("=" * 60)
print("Haystack Ollama Tools Spike")
print("=" * 60)
print(f"haystack:               {haystack.__version__}")

try:
    from importlib.metadata import version as pkg_version
    print(f"ollama-haystack:        {pkg_version('ollama-haystack')}")
except Exception:
    print("ollama-haystack:        (installed, version lookup failed)")

print()

# ── Domain tool definition ─────────────────────────────────────────────────────
from haystack.tools import create_tool_from_function


def compute_flow_temperature(outdoor_temp: float, heating_curve_slope: float = 1.5) -> dict:
    """
    Compute the required heating circuit flow temperature (Vorlauftemperatur)
    given the current outdoor temperature and heating curve slope (Heizkennlinie).

    Uses the simplified linear heating curve formula common in German residential
    heating systems (DIN EN 12831 context).

    Args:
        outdoor_temp: Current outdoor temperature in °C (typically -20 to +20).
        heating_curve_slope: Slope of the heating curve (Steilheit), dimensionless.
                             Typical range 0.5–2.5. Default 1.5.

    Returns:
        dict with keys: flow_temp (float, °C), outdoor_temp (float, °C),
        heating_curve_slope (float).
    """
    # Simplified linear formula: flow_temp = 70 - slope * outdoor_temp
    # (reference point: 20°C flow at +20°C outdoor, design point varies)
    design_flow = 70.0
    flow_temp = design_flow - heating_curve_slope * outdoor_temp
    # Clamp to physical range
    flow_temp = max(20.0, min(90.0, flow_temp))
    return {
        "flow_temp": round(flow_temp, 1),
        "outdoor_temp": outdoor_temp,
        "heating_curve_slope": heating_curve_slope,
    }


heating_tool = create_tool_from_function(compute_flow_temperature)
print(f"Tool name:              {heating_tool.name}")
print(f"Tool description:       {heating_tool.description[:60]}...")
print(f"Tool parameters schema: {list(heating_tool.parameters.get('properties', {}).keys())}")
print()

# ── Section 1: Basic connectivity (no tools) ──────────────────────────────────
print("─" * 60)
print("Section 1: Basic connectivity (no tools)")
print("─" * 60)

from haystack_integrations.components.generators.ollama import OllamaChatGenerator
from haystack.dataclasses import ChatMessage

generator_basic = OllamaChatGenerator(
    model="llama3.1:8b",
    url="http://localhost:11434",
    generation_kwargs={"temperature": 0.0},
    timeout=60,
)

try:
    messages = [ChatMessage.from_user("What is the capital of Germany? Answer in one word.")]
    response = generator_basic.run(messages=messages)
    replies = response.get("replies", [])
    if replies:
        text = replies[0].text or ""
        print(f"Basic response: {text.strip()[:100]}")
        section1_ok = True
    else:
        print("ERROR: No replies returned")
        section1_ok = False
except Exception as e:
    print(f"ERROR in Section 1: {e}")
    section1_ok = False
    print("OUTCOME: C — generator cannot connect to Ollama")
    sys.exit(1)

print()

# ── Section 2: Tool-calling round-trip ────────────────────────────────────────
print("─" * 60)
print("Section 2: Tool-calling round-trip")
print("─" * 60)

generator_tools = OllamaChatGenerator(
    model="llama3.1:8b",
    url="http://localhost:11434",
    generation_kwargs={"temperature": 0.0},
    timeout=60,
    tools=[heating_tool],
)

user_query = (
    "It is -5°C outside. "
    "What flow temperature does my heating system need? "
    "Use the compute_flow_temperature tool with the outdoor temperature."
)

messages = [ChatMessage.from_user(user_query)]

try:
    response = generator_tools.run(messages=messages)
    replies = response.get("replies", [])

    if not replies:
        print("ERROR: No replies returned")
        print("OUTCOME: B — generator worked but returned empty response")
        sys.exit(0)

    reply = replies[0]
    print(f"Reply role:    {reply.role}")

    # Check whether the model issued a tool call
    tool_calls = reply.tool_calls or []
    print(f"Tool calls:    {len(tool_calls)}")

    if not tool_calls:
        text = reply.text or ""
        print(f"Text reply:    {text.strip()[:200]}")
        print()
        print("OUTCOME: B — model responded in text instead of issuing a tool call.")
        print("         Possible causes: llama3.1:8b tool-calling format mismatch,")
        print("         prompt not triggering function call, or model capability gap.")
        sys.exit(0)

    # Process the tool call
    tc = tool_calls[0]
    print(f"Tool called:   {tc.tool_name}")
    print(f"Arguments:     {tc.arguments}")

    # Execute the tool manually (simulating what a Haystack Pipeline would do)
    tool_result = heating_tool.invoke(**tc.arguments)
    print(f"Tool result:   {tool_result}")

    # Feed result back to the model
    messages_with_result = messages + [
        reply,  # assistant message containing the tool call
        ChatMessage.from_tool(
            tool_result=str(tool_result),
            origin=tc,
        ),
    ]

    final_response = generator_tools.run(messages=messages_with_result)
    final_replies = final_response.get("replies", [])
    if final_replies:
        final_text = final_replies[0].text or ""
        print(f"Final answer:  {final_text.strip()[:300]}")
    else:
        print("WARNING: No final reply after tool result injection")

    print()
    print("OUTCOME: A — full tool-calling round-trip successful.")
    print("         Haystack Tool + OllamaChatGenerator work with llama3.1:8b.")
    print("         The RAG subsystem can be wrapped as a @tool behind LangGraph.")

except Exception as e:
    print(f"ERROR in Section 2: {e}")
    import traceback
    traceback.print_exc()
    print()
    print("OUTCOME: C — tool-calling section crashed.")

print()
print("=" * 60)
print("Spike complete.")
print("=" * 60)
