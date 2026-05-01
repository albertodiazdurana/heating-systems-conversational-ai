"""LangChain @tool wrapper around the Haystack retrieval pipeline.

Sprint 2 Phase 4 thread 2. Exposes `rag_search_tool` to the agent as a
single hybrid tool: open-ended retrieval by default, optional `part`
filter when the query is clearly scoped to one knowledge-base part.

Design choice (Open Design Question #1, decided at Phase 4 Gate 1):
hybrid (1 tool + optional `part` filter) over monolithic or fully
specialized. Rationale documented in
`dsm-docs/plans/2026-04-18_sprint2_rag_haystack_plan.md` §"Open Design
Questions" and the corresponding decision record (Phase 5).
"""

from __future__ import annotations

from langchain_core.tools import tool

from src.rag.retrieval import DEFAULT_TOP_K, retrieve

VALID_PARTS = (
    "Part I: Domain Fundamentals - Heating Systems & Energy Technology",
    "Part II: Data Science & Machine Learning for Energy Systems",
    "Part III: Production Engineering & MLOps",
    "Part IV: Technical Stack Deep Dive",
    "Part V: Applied Scenarios",
    "References",
    "Data Science for Residential Energy Systems",
)


@tool
def rag_search_tool(query: str, part: str = "") -> dict:
    """Search the heating-domain knowledge base for relevant passages.

    Use for open-ended domain questions (concepts, definitions, bilingual
    EN/DE lookups, technical context) that are NOT covered by the
    deterministic tools (standard_lookup_tool, heating_curve_tool, the unit
    converters). Bilingual retrieval works because bge-m3 embeddings are
    language-aligned, the user can ask in English or German.

    Args:
        query: Natural-language question, EN or DE.
        part: Optional filter to scope retrieval to one knowledge-base part.
            Pass an empty string for global search (default). Only set this
            when the query is clearly scoped to one part. Valid values:
              - "Part I: Domain Fundamentals - Heating Systems & Energy Technology"
              - "Part II: Data Science & Machine Learning for Energy Systems"
              - "Part III: Production Engineering & MLOps"
              - "Part IV: Technical Stack Deep Dive"
              - "Part V: Applied Scenarios"
              - "References"
              - "Data Science for Residential Energy Systems"

    Returns:
        dict with keys: query, part (echoed; empty string when unfiltered),
        hits (list of up to 5 dicts with keys: content, source_doc,
        section_header, part, score). Hits are ordered by descending score.
    """
    part_filter = part if part else None
    if part_filter is not None and part_filter not in VALID_PARTS:
        valid = "; ".join(VALID_PARTS)
        raise ValueError(
            f"Unknown part: {part!r}. Valid parts: {valid}. "
            f"Pass an empty string for global search."
        )

    documents = retrieve(query=query, part=part_filter, top_k=DEFAULT_TOP_K)
    return {
        "query": query,
        "part": part,
        "hits": [
            {
                "content": doc.content,
                "source_doc": doc.meta.get("source_doc"),
                "section_header": doc.meta.get("section_header"),
                "part": doc.meta.get("part"),
                "score": doc.score,
            }
            for doc in documents
        ],
    }
