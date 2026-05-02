"""Architectural boundary assertions.

Sprint 2 plan §72: no LangGraph imports in `src/rag/`; no Haystack imports
outside `src/rag/` and `src/tools/rag_search.py`. Codified as text-scan
assertions so the constraint fails CI on a misplaced import rather than
relying on code review.

Text scan rather than AST: this repo doesn't use conditional imports
(verified 2026-05-01); a literal substring scan is sufficient and
catches regressions in <10 ms per file.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / "src"

HAYSTACK_ALLOWED_DIRS = (SRC / "rag",)
HAYSTACK_ALLOWED_FILES = (SRC / "tools" / "rag_search.py",)


def _is_allowed_for_haystack(py_file: Path) -> bool:
    if py_file in HAYSTACK_ALLOWED_FILES:
        return True
    return any(allowed in py_file.parents for allowed in HAYSTACK_ALLOWED_DIRS)


def test_no_langgraph_imports_in_src_rag() -> None:
    rag_dir = SRC / "rag"
    offenders: list[Path] = []
    for py_file in rag_dir.rglob("*.py"):
        text = py_file.read_text(encoding="utf-8")
        if "from langgraph" in text or "import langgraph" in text:
            offenders.append(py_file)
    assert not offenders, f"langgraph imports leaked into src/rag/: {offenders}"


def test_no_haystack_imports_outside_rag_modules() -> None:
    offenders: list[Path] = []
    for py_file in SRC.rglob("*.py"):
        if _is_allowed_for_haystack(py_file):
            continue
        text = py_file.read_text(encoding="utf-8")
        if "from haystack" in text or "import haystack" in text:
            offenders.append(py_file)
    assert not offenders, (
        f"haystack imports leaked outside src/rag/ and rag_search.py: {offenders}"
    )
