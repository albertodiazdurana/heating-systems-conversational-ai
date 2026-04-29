"""Unit tests for src.rag.ingest (deterministic path only).

The bge-m3 + Chroma round-trip is exercised by `scripts/ingest.py`, not
here, to avoid a 2.27 GB model download on every test run.
"""

from haystack import Document

from src.rag.ingest import _doc_id, with_doc_ids


def test_doc_id_is_deterministic() -> None:
    a = _doc_id("01_Domain_Fundamentals.md", 5)
    b = _doc_id("01_Domain_Fundamentals.md", 5)
    assert a == b


def test_doc_id_is_unique_per_source_chunk_pair() -> None:
    seen = set()
    for source in ["a.md", "b.md", "c.md"]:
        for index in range(50):
            seen.add(_doc_id(source, index))
    assert len(seen) == 3 * 50  # no collisions


def test_doc_id_format_is_16_hex_chars() -> None:
    doc_id = _doc_id("file.md", 0)
    assert len(doc_id) == 16
    assert all(c in "0123456789abcdef" for c in doc_id)


def test_with_doc_ids_returns_new_documents_with_stable_ids() -> None:
    docs = [
        Document(content="x", meta={"source_doc": "a.md", "chunk_index": 0}),
        Document(content="y", meta={"source_doc": "a.md", "chunk_index": 1}),
    ]
    result = with_doc_ids(docs)
    assert result[0].id == _doc_id("a.md", 0)
    assert result[1].id == _doc_id("a.md", 1)
    assert result[0].id != result[1].id


def test_with_doc_ids_does_not_mutate_input() -> None:
    docs = [Document(content="x", meta={"source_doc": "a.md", "chunk_index": 0})]
    original_id = docs[0].id
    _ = with_doc_ids(docs)
    assert docs[0].id == original_id


def test_with_doc_ids_is_idempotent() -> None:
    docs = [Document(content="x", meta={"source_doc": "a.md", "chunk_index": 0})]
    once = with_doc_ids(docs)
    twice = with_doc_ids(once)
    assert once[0].id == twice[0].id


def test_with_doc_ids_preserves_content_and_meta() -> None:
    docs = [
        Document(
            content="hello",
            meta={"source_doc": "a.md", "chunk_index": 0, "part": "Part I"},
        ),
    ]
    result = with_doc_ids(docs)
    assert result[0].content == "hello"
    assert result[0].meta["part"] == "Part I"
    assert result[0].meta["source_doc"] == "a.md"