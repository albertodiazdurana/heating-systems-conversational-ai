"""Markdown chunking for the heating-guide knowledge base.

Sprint 2 Phase 3 thread 1. Header-aware splitting on H2/H3 via LangChain's
MarkdownHeaderTextSplitter, then conversion to Haystack Documents with
metadata for downstream retrieval (source_doc, part, chapter, section_header,
chunk_index).

The splitter strips the H2/H3 header line from page_content and lifts it
into metadata. The H1 (part-level title) is captured separately, since
splitting on H1 would produce one chunk per file. Pre-H2 chunks (intro
text under the H1) are kept with section_header="intro" so they remain
addressable in retrieval results.

Public API:
    split_markdown_file: Path -> list[haystack.Document]
"""

from pathlib import Path

from haystack import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter

HEADER_LEVELS = [("##", "chapter"), ("###", "section_header")]


def _extract_part_title(text: str) -> str:
    """Return the first H1 line's text, or '' if no H1."""
    for line in text.splitlines():
        if line.startswith("# ") and not line.startswith("## "):
            return line[2:].strip()
    return ""


def split_markdown_file(path: Path) -> list[Document]:
    """Split a markdown file into Haystack Documents on H2/H3 boundaries.

    Each returned Document has:
        content: chunk text (header line stripped by the splitter)
        meta:
            source_doc: filename (e.g. "01_Domain_Fundamentals.md")
            part: H1 title for the file (e.g. "Part I: Domain Fundamentals")
            chapter: H2 title if the chunk is under one, else ""
            section_header: H3 title if under one, else "intro"
            chunk_index: 0-based position within the file

    Args:
        path: absolute path to a markdown file.

    Returns:
        List of Haystack Documents, one per chunk. Empty list if the file
        is empty or contains no chunkable content.
    """
    text = path.read_text(encoding="utf-8")
    part = _extract_part_title(text)
    splitter = MarkdownHeaderTextSplitter(headers_to_split_on=HEADER_LEVELS)
    lc_chunks = splitter.split_text(text)

    documents: list[Document] = []
    for index, chunk in enumerate(lc_chunks):
        meta = chunk.metadata
        documents.append(
            Document(
                content=chunk.page_content,
                meta={
                    "source_doc": path.name,
                    "part": part,
                    "chapter": meta.get("chapter", ""),
                    "section_header": meta.get("section_header", "intro"),
                    "chunk_index": index,
                },
            )
        )
    return documents