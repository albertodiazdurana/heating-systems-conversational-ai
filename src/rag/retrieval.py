"""Haystack retrieval pipeline for the heating-guide knowledge base.

Sprint 2 Phase 4 thread 1. Builds a query-time Pipeline that embeds a
natural-language query with `BAAI/bge-m3` (matching the ingest-time
embedder per the Phase 2 decision record) and runs cosine similarity
search over the persistent Chroma store populated by `scripts/ingest.py`.

Idempotency / safety: the pipeline is built once per process and cached.
Building does NOT download the model, the SentenceTransformers backend is
lazy and loads on first `run()`. Callers that want a warm pipeline should
issue one throwaway `retrieve(query="warmup")` at startup.

Public API:
    build_retrieval_pipeline: () -> haystack.Pipeline
    retrieve: (query, part=None, top_k=5) -> list[Document]

Filter shape: when `part` is provided, the run-time filter is
`{"field": "meta.part", "operator": "==", "value": part}`, the standard
Haystack 2.x metadata-filter form. Chroma's metadata is namespaced under
`meta.` at filter time even though Haystack Documents expose it under
`.meta` directly.
"""

from __future__ import annotations

from haystack import Document, Pipeline
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack_integrations.components.retrievers.chroma import ChromaEmbeddingRetriever

from src.rag.ingest import (
    DEFAULT_COLLECTION,
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_PERSIST_PATH,
    get_document_store,
)

DEFAULT_TOP_K = 5

_PIPELINE: Pipeline | None = None


def build_retrieval_pipeline(
    persist_path: str = DEFAULT_PERSIST_PATH,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    collection_name: str = DEFAULT_COLLECTION,
    top_k: int = DEFAULT_TOP_K,
) -> Pipeline:
    """Build a Haystack Pipeline that embeds a query and retrieves from Chroma.

    Args:
        persist_path: filesystem path of the persistent Chroma store.
        embedding_model: SentenceTransformers model id, must match the model
            used at ingest time (default: bge-m3).
        collection_name: Chroma collection name.
        top_k: default number of documents the retriever returns; can be
            overridden per call via the run-time payload.

    Returns:
        A Haystack Pipeline with two connected components:
            "text_embedder": SentenceTransformersTextEmbedder
            "retriever":     ChromaEmbeddingRetriever (top_k, filters set at run time)

        Pipeline input shape:
            {"text_embedder": {"text": "<query>"},
             "retriever":     {"filters": {...} | None, "top_k": int | None}}
    """
    document_store = get_document_store(persist_path, collection_name)
    text_embedder = SentenceTransformersTextEmbedder(model=embedding_model)
    retriever = ChromaEmbeddingRetriever(
        document_store=document_store,
        top_k=top_k,
    )

    pipeline = Pipeline()
    pipeline.add_component("text_embedder", text_embedder)
    pipeline.add_component("retriever", retriever)
    pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
    return pipeline


def _get_cached_pipeline() -> Pipeline:
    """Return the module-level pipeline, building it on first access."""
    global _PIPELINE
    if _PIPELINE is None:
        _PIPELINE = build_retrieval_pipeline()
    return _PIPELINE


def retrieve(
    query: str,
    part: str | None = None,
    top_k: int = DEFAULT_TOP_K,
    exclude_intro: bool = True,
) -> list[Document]:
    """Retrieve up to `top_k` documents for `query`, optionally filtered by part.

    Args:
        query: natural-language question, EN or DE.
        part: when provided, restricts retrieval to documents whose
            `meta["part"]` equals this value exactly. One of the seven
            heating-guide parts (see scripts/ingest.py output for the list)
            or None for global search.
        top_k: max number of documents to return.
        exclude_intro: when True (default), excludes chunks whose
            `section_header == "intro"`. Intro chunks are navigational
            and tend to dominate top-K via short-doc bias on broad
            queries (verified empirically by EXP-001 q10 miss with
            intro_dominance pattern). Set False to inspect them, e.g.
            for debugging or for queries explicitly about a chapter
            preamble.

    Returns:
        List of Haystack Documents in descending score order. Each Document
        carries the original `meta` dict (source_doc, section_header, part,
        chunk_index, chapter) and a `.score` populated by the retriever.
    """
    pipeline = _get_cached_pipeline()

    conditions: list[dict] = []
    if part is not None:
        conditions.append(
            {"field": "meta.part", "operator": "==", "value": part}
        )
    if exclude_intro:
        conditions.append(
            {"field": "meta.section_header", "operator": "!=", "value": "intro"}
        )

    retriever_payload: dict = {"top_k": top_k}
    if len(conditions) == 1:
        retriever_payload["filters"] = conditions[0]
    elif len(conditions) > 1:
        retriever_payload["filters"] = {"operator": "AND", "conditions": conditions}

    result = pipeline.run(
        {
            "text_embedder": {"text": query},
            "retriever": retriever_payload,
        }
    )
    return result["retriever"]["documents"]
