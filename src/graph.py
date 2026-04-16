"""Agent graph construction.

Sprint 1 step 9. Wires get_chat_model, SYSTEM_PROMPT, and TOOLS into a
LangChain create_agent (replaces deprecated langgraph.prebuilt.create_react_agent
as of LangGraph V1.0). Multi-turn memory via InMemorySaver + a per-session
thread_id provided by the caller (e.g., app.py).
"""

from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent

from src.config import get_chat_model
from src.prompts import SYSTEM_PROMPT
from src.tools.registry import TOOLS


def build_agent(checkpointer=None):
    """Return a configured ReAct agent bound to the current env.

    Args:
        checkpointer: optional LangGraph checkpointer. Defaults to a
            fresh InMemorySaver (per-process memory). Pass a shared saver
            to reuse memory across build_agent() calls.

    Returns:
        Compiled LangGraph runnable (create_react_agent result).
    """
    return create_agent(
        model=get_chat_model(),
        tools=TOOLS,
        checkpointer=checkpointer or InMemorySaver(),
        system_prompt=SYSTEM_PROMPT,
    )