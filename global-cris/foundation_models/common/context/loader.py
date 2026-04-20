"""
Loads markdown context documents for use in advanced examples.

Usage:
    from common.context.loader import load_doc, load_all_docs, list_docs

    # Load a single document
    content = load_doc("microservices_architecture.md")

    # Load all documents
    docs = load_all_docs()

    # List available documents
    names = list_docs()
"""

import os
from pathlib import Path

DOCS_DIR = Path(__file__).parent / "docs"


def load_doc(filename: str) -> str:
    """
    Load a single markdown document by filename.

    Args:
        filename: Name of the .md file in the docs/ directory.

    Returns:
        The full text content of the document.

    Raises:
        FileNotFoundError: If the document doesn't exist.
    """
    filepath = DOCS_DIR / filename
    if not filepath.exists():
        available = list_docs()
        raise FileNotFoundError(
            f"Document '{filename}' not found. Available: {available}"
        )
    return filepath.read_text(encoding="utf-8")


def load_all_docs() -> dict[str, str]:
    """
    Load all markdown documents from the docs/ directory.

    Returns:
        Dictionary mapping filename to content.
    """
    docs = {}
    for filepath in sorted(DOCS_DIR.glob("*.md")):
        docs[filepath.name] = filepath.read_text(encoding="utf-8")
    return docs


def list_docs() -> list[str]:
    """List available document filenames."""
    return sorted(f.name for f in DOCS_DIR.glob("*.md"))
