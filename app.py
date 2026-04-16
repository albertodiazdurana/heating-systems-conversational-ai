"""Streamlit chat UI for the heating systems assistant.

Sprint 1 step 10. Features:
- Per-session thread_id (uuid4) in st.session_state for checkpointer routing.
- Chat history in st.session_state.messages, parallel to the checkpointer.
- Tool-call rendering via st.expander (manual parse of AIMessage.tool_calls
  and matching ToolMessage results).
- Top-level try/except, primary Sprint 1 safety net (plan §5.4).
- Sidebar: 5 suggested queries (plan step 11) + provider/model indicator.

Run: uv run streamlit run app.py
"""

import os
import uuid

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from src.config import load_env
from src.graph import build_agent

load_env()

SUGGESTED_QUERIES = [
    "Convert 24 kW to kcal/h",
    "What's DIN EN 12831?",
    "Heating curve flow temp at -5°C with slope 1.0",
    "Wie kalt war der Winter?",
    "Berechne die Vorlauftemperatur bei -10°C mit Steigung 1.2",
]

ERROR_MESSAGE = "Sorry, an error occurred. / Es ist ein Fehler aufgetreten."


@st.cache_resource
def get_agent():
    return build_agent()


def init_session():
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "pending_input" not in st.session_state:
        st.session_state.pending_input = None


def _extract_turn_tool_calls(result_messages, user_text):
    """Collect tool_calls + results from the most recent turn.

    agent.invoke returns the FULL thread (previous turns replayed from the
    checkpointer). We slice from the last HumanMessage whose content matches
    user_text; iterating end-to-start makes repeated identical prompts pick
    the latest one.
    """
    turn_start = next(
        (
            i + 1
            for i in range(len(result_messages) - 1, -1, -1)
            if isinstance(result_messages[i], HumanMessage)
            and result_messages[i].content == user_text
        ),
        len(result_messages),
    )
    turn_msgs = result_messages[turn_start:]
    tool_results = {
        m.tool_call_id: str(m.content)
        for m in turn_msgs
        if isinstance(m, ToolMessage)
    }
    flat = []
    for m in turn_msgs:
        if isinstance(m, AIMessage) and m.tool_calls:
            for call in m.tool_calls:
                flat.append(
                    {
                        "name": call["name"],
                        "args": call.get("args", {}),
                        "result": tool_results.get(call.get("id")),
                    }
                )
    return flat


def handle_user_input(user_text):
    agent = get_agent()
    cfg = {"configurable": {"thread_id": st.session_state.thread_id}}
    st.session_state.messages.append({"role": "user", "content": user_text})
    try:
        result = agent.invoke({"messages": [("user", user_text)]}, config=cfg)
    except Exception as e:
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": ERROR_MESSAGE,
                "error": str(e),
            }
        )
        return
    final = result["messages"][-1]
    final_text = final.content if isinstance(final, AIMessage) else str(final)
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": final_text,
            "tool_calls": _extract_turn_tool_calls(result["messages"], user_text),
        }
    )


def _model_caption():
    provider = os.getenv("LLM_PROVIDER", "ollama")
    model_name = (
        os.getenv("OLLAMA_MODEL", "llama3.1:8b")
        if provider == "ollama"
        else os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    )
    return f"Provider: `{provider}` · Model: `{model_name}` · temperature=0"


def render_history():
    for entry in st.session_state.messages:
        with st.chat_message(entry["role"]):
            st.markdown(entry["content"])
            for tc in entry.get("tool_calls", []):
                with st.expander(f"🔧 {tc['name']}"):
                    st.markdown("**Arguments**")
                    st.json(tc["args"])
                    if tc["result"] is not None:
                        st.markdown("**Result**")
                        st.code(tc["result"])
            if entry.get("error"):
                with st.expander("Error details"):
                    st.code(entry["error"])


st.set_page_config(page_title="Heating Systems Assistant", page_icon="🔥")
st.title("🔥 Heating Systems Assistant")
st.caption("German residential heating · bilingual (EN/DE)")

init_session()

with st.sidebar:
    st.markdown("### Suggested queries")
    for q in SUGGESTED_QUERIES:
        if st.button(q, use_container_width=True):
            st.session_state.pending_input = q
    st.divider()
    st.caption(_model_caption())

render_history()

typed = st.chat_input("Ask about heating systems…")
user_input = st.session_state.pending_input or typed
st.session_state.pending_input = None
if user_input:
    handle_user_input(user_input)
    st.rerun()