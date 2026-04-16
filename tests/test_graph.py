"""Smoke test for agent graph construction (no LLM invocation)."""

from src.graph import build_agent


def test_build_agent_default(monkeypatch):
    """With LLM_PROVIDER=ollama pinned, build_agent() returns a non-None compiled graph."""
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434")
    agent = build_agent()
    assert agent is not None