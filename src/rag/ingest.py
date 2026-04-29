"""Haystack ingestion pipeline for the heating-guide knowledge base.

Sprint 2 Phase 3 thread 2. Builds a Pipeline that embeds Haystack Documents
with `BAAI/bge-m3` (Phase 2 winner per
`dsm-docs/decisions/2026-04-24_phase2-embedding-model-selection.md`) and
writes them to a persistent Chroma store.

Idempotency: `with_doc_ids` returns new Documents whose `id` is
sha256("<source_doc>::<chunk_index>") truncated to 16 hex chars. Combined
with `DuplicatePolicy.OVERWRITE` on the writer, re-running ingest on the
same corpus produces no duplicates. We use `dataclasses.replace` rather
than mutating `.id` directly per Haystack's custom-components guidance.

Distance metric: cosine. Phase 2's micro-benchmark used cosine similarity
(decision record §"Retrieval discrimination gap"); bge-m3 outputs are
unit-normalized, so cosine is the natural metric.

Public API:
    build_ingestion_pipeline: () -> haystack.Pipeline
    with_doc_ids: list[Document] -> list[Document]  (returns new instances)
    get_document_store: () -> ChromaDocumentStore
"""

from __future__ import annotations

import dataclasses
import hashlib

from haystack import Document, Pipeline
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack.components.writers import DocumentWriter
from haystack.document_stores.types import DuplicatePolicy
from haystack_integrations.document_stores.chroma import ChromaDocumentStore

DEFAULT_PERSIST_PATH = "data/chroma"
DEFAULT_EMBEDDING_MODEL = "BAAI/bge-m3"
DEFAULT_COLLECTION = "heating_guide"


def _doc_id(source_doc: str, chunk_index: int) -> str:
    """Deterministic 16-char hex id from source filename + chunk index."""
    raw = f"{source_doc}::{chunk_index}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def with_doc_ids(documents: list[Document]) -> list[Document]:
    """Return new Documents whose `id` is derived from source_doc + chunk_index.

    Uses `dataclasses.replace` rather than mutating `.id` to comply with
    Haystack's custom-components guidance. Input documents are not modified.

    Args:
        documents: Haystack Documents produced by `split_markdown_file`.
            Each must have `meta["source_doc"]` and `meta["chunk_index"]`.

    Returns:
        New list of Documents in the same order, each with a stable `id`.

    Raises:
        KeyError: a document is missing one of the required meta keys.
    """
    return [
        dataclasses.replace(
            doc,
            id=_doc_id(doc.meta["source_doc"], doc.meta["chunk_index"]),
        )
        for doc in documents
    ]


def get_document_store(
    persist_path: str = DEFAULT_PERSIST_PATH,
    collection_name: str = DEFAULT_COLLECTION,
) -> ChromaDocumentStore:
    """Return a ChromaDocumentStore configured for cosine retrieval."""
    return ChromaDocumentStore(
        collection_name=collection_name,
        persist_path=persist_path,
        distance_function="cosine",
    )


def build_ingestion_pipeline(
    persist_path: str = DEFAULT_PERSIST_PATH,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    collection_name: str = DEFAULT_COLLECTION,
) -> Pipeline:
    """Build a Haystack Pipeline that embeds and writes Documents to Chroma.

    Args:
        persist_path: filesystem path for the persistent Chroma store.
        embedding_model: SentenceTransformers model id; defaults to bge-m3.
        collection_name: Chroma collection name.

    Returns:
        A Haystack Pipeline with two connected components:
            "embedder": SentenceTransformersDocumentEmbedder
            "writer":   DocumentWriter (OVERWRITE policy)

        Pipeline input: {"embedder": {"documents": [...]}}.
    """
    document_store = get_document_store(persist_path, collection_name)
    embedder = SentenceTransformersDocumentEmbedder(model=embedding_model)
    writer = DocumentWriter(
        document_store=document_store,
        policy=DuplicatePolicy.OVERWRITE,
    )

    pipeline = Pipeline()
    pipeline.add_component("embedder", embedder)
    pipeline.add_component("writer", writer)
    pipeline.connect("embedder.documents", "writer.documents")
    return pipeline