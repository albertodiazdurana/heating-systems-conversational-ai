"""Empirical probe: create_agent recovery when a tool raises (BL-002 edit 4).

Empirical findings (langchain 1.2.15):
1. create_agent does NOT catch tool exceptions by default, contradicting
   plan §5.4's original assumption.
2. BaseTool.handle_tool_error only catches ToolException subclasses;
   generic Exception (incl. ValueError) bypasses the flag and propagates.

Canonical mitigation pathway demonstrated here: tool raises ToolException,
with handle_tool_error=True the tool's error is returned as a ToolMessage
the model can respond to, and agent.invoke() completes cleanly.

Production note: Sprint 1 tools raise ValueError (standard_lookup, etc.)
which will propagate to app.py's try/except. Converting to ToolException
for per-tool model-visible recovery is a deferred decision.
"""

from langchain.agents import create_agent
from langchain_core.language_models.fake_chat_models import (
    FakeMessagesListChatModel,
)
from langchain_core.messages import AIMessage
from langchain_core.tools import ToolException, tool


class _BindableFakeModel(FakeMessagesListChatModel):
    """FakeMessagesListChatModel with a no-op bind_tools.

    create_agent calls bind_tools during setup to register the tools; the
    base fake raises NotImplementedError. Since this model is scripted,
    binding is a no-op (responses are returned regardless of tool schema).
    """

    def bind_tools(self, tools, **kwargs):
        return self


@tool
def flaky_tool(x: int) -> int:
    """Stub tool that always raises a ToolException, to probe agent error handling."""
    raise ToolException("boom")


flaky_tool.handle_tool_error = True


def test_agent_recovers_from_tool_exception():
    """With ToolException + handle_tool_error=True, create_agent.invoke() completes cleanly.

    Scripted model: call tool on turn 1, return text on turn 2.
    Expectation: agent.invoke() returns normally with an AIMessage final.
    """
    model = _BindableFakeModel(
        responses=[
            AIMessage(
                content="",
                tool_calls=[
                    {"name": "flaky_tool", "args": {"x": 1}, "id": "call_1"}
                ],
            ),
            AIMessage(content="The tool failed; unable to complete the request."),
        ]
    )
    agent = create_agent(model=model, tools=[flaky_tool])

    result = agent.invoke({"messages": [("user", "run the tool")]})

    final = result["messages"][-1]
    assert isinstance(final, AIMessage)
    assert final.content