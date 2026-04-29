"""Configuration: env loading + chat-model factory.

Sprint 1 step 7. Keeps LLM-provider wiring out of graph.py.

Functions:
    load_env: call once at app entry (app.py) to load .env into os.environ.
    get_chat_model: factory returning ChatOllama or ChatOpenAI based on
        LLM_PROVIDER. Reads os.environ directly; does not call load_env.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI


def load_env() -> None:
    """Load .env into os.environ (idempotent, does not override existing vars)."""
    load_dotenv()


def get_chat_model() -> BaseChatModel:
    """Return the configured chat model based on LLM_PROVIDER.

    Env vars:
        LLM_PROVIDER: "ollama" (default) or "openai"
        OLLAMA_MODEL, OLLAMA_BASE_URL: used when provider is "ollama"
        OPENAI_MODEL, OPENAI_API_KEY: used when provider is "openai"

    Raises:
        ValueError: unknown provider, or openai provider with empty
            OPENAI_API_KEY.
    """
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    if provider == "ollama":
        return ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=0,
        )
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            api_key=api_key,
            temperature=0,
        )
    raise ValueError(
        f"Unknown LLM_PROVIDER: {provider!r}. Expected 'ollama' or 'openai'."
    )


def get_kb_source_dir() -> Path:
    """Return the knowledge-base source directory.

    Env var:
        KB_SOURCE_DIR: path to the directory holding the heating-guide MD files.
            Defaults to the sibling `dsm-residential-heating-ds-guide` repo.

    Raises:
        FileNotFoundError: configured path does not exist.
    """
    default = Path.home() / "_projects" / "dsm-residential-heating-ds-guide"
    path = Path(os.getenv("KB_SOURCE_DIR", str(default)))
    if not path.is_dir():
        raise FileNotFoundError(
            f"KB_SOURCE_DIR points to {path}, which is not a directory."
        )
    return path