"""Unit tests for src.rag.chunking."""

from pathlib import Path

import pytest

from src.rag.chunking import split_markdown_file


@pytest.fixture
def sample_md(tmp_path: Path) -> Path:
    content = (
        "# Part I: Domain\n"
        "Intro paragraph under the part.\n"
        "\n"
        "## Chapter 1: Heat\n"
        "Chapter intro.\n"
        "\n"
        "### 1.1 Conduction\n"
        "Fourier's law applies.\n"
        "\n"
        "### 1.2 Convection\n"
        "Newton's law of cooling.\n"
        "\n"
        "## Chapter 2: Energy\n"
        "Energy chapter content.\n"
    )
    path = tmp_path / "sample.md"
    path.write_text(content, encoding="utf-8")
    return path


def test_split_returns_haystack_documents(sample_md: Path) -> None:
    docs = split_markdown_file(sample_md)
    assert len(docs) == 5  # intro, ch1-intro, 1.1, 1.2, ch2-intro


def test_part_metadata_propagates_to_every_chunk(sample_md: Path) -> None:
    docs = split_markdown_file(sample_md)
    for doc in docs:
        assert doc.meta["part"] == "Part I: Domain"
        assert doc.meta["source_doc"] == "sample.md"


def test_section_header_defaults_to_intro(sample_md: Path) -> None:
    docs = split_markdown_file(sample_md)
    intro_docs = [d for d in docs if d.meta["section_header"] == "intro"]
    assert len(intro_docs) == 3  # part-intro + 2 chapter-intros


def test_h3_metadata_captured(sample_md: Path) -> None:
    docs = split_markdown_file(sample_md)
    h3_docs = [d for d in docs if d.meta["section_header"] != "intro"]
    headers = {d.meta["section_header"] for d in h3_docs}
    assert headers == {"1.1 Conduction", "1.2 Convection"}


def test_chunk_index_is_zero_based_and_sequential(sample_md: Path) -> None:
    docs = split_markdown_file(sample_md)
    indices = [d.meta["chunk_index"] for d in docs]
    assert indices == list(range(len(docs)))


def test_empty_file_returns_empty_list(tmp_path: Path) -> None:
    path = tmp_path / "empty.md"
    path.write_text("", encoding="utf-8")
    assert split_markdown_file(path) == []