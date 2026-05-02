"""Unit tests for src.tools.rag_search (no I/O, no model load).

Validates the @tool wrapper's shape, filter pass-through, and validation
behavior by monkeypatching `retrieve`. The real retrieval round-trip is
covered by tests/test_retrieval.py integration tests gated on data/chroma.
"""

from __future__ import annotations

import pytest
from haystack import Document

from src.tools import rag_search as rag_search_module
from src.tools.rag_search import VALID_PARTS, rag_search_tool


def _fake_retrieve_factory(captured: dict, docs: list[Document]):
    def fake_retrieve(query, part=None, top_k=5):
        captured["query"] = query
        captured["part"] = part
        captured["top_k"] = top_k
        return docs

    return fake_retrieve


def test_rag_search_tool_is_a_langchain_tool() -> None:
    assert hasattr(rag_search_tool, "name")
    assert hasattr(rag_search_tool, "description")
    assert hasattr(rag_search_tool, "invoke")
    assert hasattr(rag_search_tool, "args_schema")
    assert rag_search_tool.name == "rag_search_tool"


def test_rag_search_tool_returns_expected_shape(monkeypatch) -> None:
    captured: dict = {}
    fake_docs = [
        Document(
            content="DIN EN 12831 specifies the design heat load calculation.",
            meta={
                "source_doc": "01_Domain_Fundamentals.md",
                "section_header": "Design Heat Load",
                "part": "Part I: Domain Fundamentals - Heating Systems & Energy Technology",
            },
            score=0.91,
        ),
    ]
    monkeypatch.setattr(
        rag_search_module,
        "retrieve",
        _fake_retrieve_factory(captured, fake_docs),
    )

    result = rag_search_tool.invoke({"query": "What is DIN EN 12831?"})

    assert result["query"] == "What is DIN EN 12831?"
    assert result["part"] == ""
    assert len(result["hits"]) == 1
    hit = result["hits"][0]
    assert hit["content"].startswith("DIN EN 12831")
    assert hit["source_doc"] == "01_Domain_Fundamentals.md"
    assert hit["section_header"] == "Design Heat Load"
    assert hit["part"].startswith("Part I:")
    assert hit["score"] == 0.91


def test_rag_search_tool_passes_no_filter_for_empty_part(monkeypatch) -> None:
    captured: dict = {}
    monkeypatch.setattr(
        rag_search_module,
        "retrieve",
        _fake_retrieve_factory(captured, []),
    )

    rag_search_tool.invoke({"query": "MLOps", "part": ""})

    assert captured["part"] is None


def test_rag_search_tool_passes_part_filter_through(monkeypatch) -> None:
    captured: dict = {}
    monkeypatch.setattr(
        rag_search_module,
        "retrieve",
        _fake_retrieve_factory(captured, []),
    )

    rag_search_tool.invoke(
        {
            "query": "MLOps",
            "part": "Part III: Production Engineering & MLOps",
        }
    )

    assert captured["part"] == "Part III: Production Engineering & MLOps"


def test_rag_search_tool_rejects_unknown_part(monkeypatch) -> None:
    monkeypatch.setattr(
        rag_search_module,
        "retrieve",
        _fake_retrieve_factory({}, []),
    )

    with pytest.raises(ValueError, match="Unknown part"):
        rag_search_tool.invoke({"query": "anything", "part": "Part IX: Made Up"})


def test_rag_search_tool_returns_empty_hits_when_no_documents(monkeypatch) -> None:
    monkeypatch.setattr(
        rag_search_module,
        "retrieve",
        _fake_retrieve_factory({}, []),
    )

    result = rag_search_tool.invoke({"query": "no results expected"})
    assert result["hits"] == []


def test_valid_parts_includes_all_seven() -> None:
    assert len(VALID_PARTS) == 7
    assert "References" in VALID_PARTS
    assert "Part I: Domain Fundamentals - Heating Systems & Energy Technology" in VALID_PARTS
