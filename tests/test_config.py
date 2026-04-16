"""Smoke tests for src.config factory (no LLM invocation)."""

import pytest
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from src.config import get_chat_model


def test_ollama_default(monkeypatch):
    """LLM_PROVIDER unset -> defaults to ollama; OLLAMA_MODEL is passed through."""
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.setenv("OLLAMA_MODEL", "test-model")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = get_chat_model()
    assert isinstance(model, ChatOllama)
    assert model.model == "test-model"


def test_ollama_explicit(monkeypatch):
    """LLM_PROVIDER=ollama explicitly -> ChatOllama."""
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    assert isinstance(get_chat_model(), ChatOllama)


def test_openai(monkeypatch):
    """LLM_PROVIDER=openai with a non-empty API key -> ChatOpenAI."""
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-dummy")
    assert isinstance(get_chat_model(), ChatOpenAI)


def test_openai_missing_key(monkeypatch):
    """LLM_PROVIDER=openai with OPENAI_API_KEY unset -> ValueError."""
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        get_chat_model()


def test_unknown_provider(monkeypatch):
    """LLM_PROVIDER set to anything other than ollama/openai -> ValueError."""
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    with pytest.raises(ValueError, match="Unknown LLM_PROVIDER"):
        get_chat_model()