"""Unit + integration tests for src.rag.retrieval.

Deterministic tests (no model load, no Chroma I/O) cover pipeline shape and
filter-payload construction via monkeypatching. Integration tests are
gated on `data/chroma/` existing, they run against the real persistent
store populated by `scripts/ingest.py` and exercise bge-m3 + ChromaEmbeddingRetriever
end-to-end.

The integration tests skip silently in CI / fresh checkouts where the
store is absent. Locally, `uv run python scripts/ingest.py` populates
the store and unblocks them.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from haystack import Pipeline

from src.rag import retrieval
from src.rag.retrieval import (
    DEFAULT_TOP_K,
    build_retrieval_pipeline,
    retrieve,
)

CHROMA_DIR = Path("data/chroma")
needs_real_store = pytest.mark.skipif(
    not CHROMA_DIR.exists(),
    reason="Requires populated Chroma store at data/chroma (run scripts/ingest.py).",
)


def test_build_retrieval_pipeline_has_expected_components() -> None:
    pipeline = build_retrieval_pipeline()
    assert isinstance(pipeline, Pipeline)
    component_names = set(pipeline.graph.nodes)
    assert component_names == {"text_embedder", "retriever"}


def test_build_retrieval_pipeline_connects_embedder_to_retriever() -> None:
    pipeline = build_retrieval_pipeline()
    edges = list(pipeline.graph.edges(data=True))
    assert len(edges) == 1
    src, dst, _ = edges[0]
    assert src == "text_embedder"
    assert dst == "retriever"


def test_retrieve_payload_has_no_filter_when_part_is_none(monkeypatch) -> None:
    captured: dict = {}

    class FakePipeline:
        def run(self, payload):
            captured.update(payload)
            return {"retriever": {"documents": []}}

    monkeypatch.setattr(retrieval, "_get_cached_pipeline", lambda: FakePipeline())
    retrieve(query="What is DIN EN 12831?", part=None, top_k=3)

    assert captured["text_embedder"] == {"text": "What is DIN EN 12831?"}
    assert "filters" not in captured["retriever"]
    assert captured["retriever"]["top_k"] == 3


def test_retrieve_payload_includes_filter_when_part_provided(monkeypatch) -> None:
    captured: dict = {}

    class FakePipeline:
        def run(self, payload):
            captured.update(payload)
            return {"retriever": {"documents": []}}

    monkeypatch.setattr(retrieval, "_get_cached_pipeline", lambda: FakePipeline())
    retrieve(query="MLOps stack", part="Part III: Production Engineering & MLOps")

    assert captured["retriever"]["filters"] == {
        "field": "meta.part",
        "operator": "==",
        "value": "Part III: Production Engineering & MLOps",
    }
    assert captured["retriever"]["top_k"] == DEFAULT_TOP_K


def test_retrieve_default_top_k_is_five() -> None:
    assert DEFAULT_TOP_K == 5


@needs_real_store
def test_retrieve_returns_documents_for_real_query() -> None:
    docs = retrieve(query="What is DIN EN 12831?", top_k=5)
    assert len(docs) >= 1
    assert any(d.meta.get("source_doc") == "01_Domain_Fundamentals.md" for d in docs)
    for d in docs:
        assert d.score is not None


@needs_real_store
def test_retrieve_with_part_filter_restricts_to_that_part() -> None:
    target = "References"
    docs = retrieve(query="bibliography", part=target, top_k=5)
    assert len(docs) >= 1
    for d in docs:
        assert d.meta.get("part") == target
