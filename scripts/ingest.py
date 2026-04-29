"""CLI runner for the Sprint 2 ingestion pipeline.

Walks the heating-guide knowledge base, splits each markdown file on H2/H3
boundaries, assigns stable document ids, and runs the Haystack pipeline to
embed (BAAI/bge-m3) and write to a persistent Chroma store.

Usage:
    uv run python scripts/ingest.py
    uv run python scripts/ingest.py --persist-path data/chroma --pattern "0?_*.md"
    KB_SOURCE_DIR=/some/other/path uv run python scripts/ingest.py

Exit 0 on success. Re-running on the same corpus is idempotent because
document ids are deterministic (sha256 of source_doc + chunk_index) and
the writer uses DuplicatePolicy.OVERWRITE.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.config import get_kb_source_dir, load_env  # noqa: E402
from src.rag.chunking import split_markdown_file  # noqa: E402
from src.rag.ingest import (  # noqa: E402
    DEFAULT_COLLECTION,
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_PERSIST_PATH,
    build_ingestion_pipeline,
    with_doc_ids,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=None,
        help="Override KB_SOURCE_DIR (default: src.config.get_kb_source_dir()).",
    )
    parser.add_argument(
        "--pattern",
        default="0?_*.md",
        help="Glob pattern matching KB files (default: '0?_*.md').",
    )
    parser.add_argument(
        "--persist-path",
        default=DEFAULT_PERSIST_PATH,
        help=f"Chroma persist path (default: {DEFAULT_PERSIST_PATH}).",
    )
    parser.add_argument(
        "--collection",
        default=DEFAULT_COLLECTION,
        help=f"Chroma collection name (default: {DEFAULT_COLLECTION}).",
    )
    parser.add_argument(
        "--embedding-model",
        default=DEFAULT_EMBEDDING_MODEL,
        help=f"SentenceTransformers model id (default: {DEFAULT_EMBEDDING_MODEL}).",
    )
    return parser.parse_args()


def main() -> int:
    load_env()
    args = parse_args()

    source_dir = args.source_dir or get_kb_source_dir()
    files = sorted(source_dir.glob(args.pattern))
    if not files:
        print(
            f"No files matching {args.pattern!r} in {source_dir}",
            file=sys.stderr,
        )
        return 1

    print(f"Source dir: {source_dir}")
    print(f"Pattern:    {args.pattern}  ({len(files)} files)")
    print(f"Persist:    {args.persist_path}  (collection: {args.collection})")
    print(f"Model:      {args.embedding_model}")
    print()

    documents = []
    for path in files:
        chunks = split_markdown_file(path)
        documents.extend(chunks)
        print(f"  {path.name}: {len(chunks)} chunks")
    print(f"\nTotal: {len(documents)} chunks")

    documents = with_doc_ids(documents)

    print(f"\nBuilding pipeline (first run downloads {args.embedding_model})...")
    pipeline = build_ingestion_pipeline(
        persist_path=args.persist_path,
        embedding_model=args.embedding_model,
        collection_name=args.collection,
    )

    print("Running pipeline (embedding + writing to Chroma)...")
    result = pipeline.run({"embedder": {"documents": documents}})
    written = result.get("writer", {}).get("documents_written", "unknown")
    print(f"\nDone. Documents written: {written}")
    return 0


if __name__ == "__main__":
    sys.exit(main())