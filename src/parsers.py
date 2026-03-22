"""Document parsers for PDF and plain text files."""

from __future__ import annotations

from pathlib import Path


def parse_text_file(path: Path) -> str:
    """Read a plain text file and return its contents."""
    return path.read_text(encoding="utf-8", errors="replace")


def parse_pdf_file(path: Path) -> str:
    """Extract text from a PDF file using pdfplumber."""
    import pdfplumber

    pages: list[str] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
    return "\n\n".join(pages)


def parse_document(path: Path) -> str:
    """Auto-detect format and extract text from a document.

    Supports: .pdf, .txt, .md, .tex, .csv
    """
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return parse_pdf_file(path)
    if suffix in {".txt", ".md", ".tex", ".csv", ".tsv", ".text", ".rst"}:
        return parse_text_file(path)
    # Fallback: try reading as text
    try:
        return parse_text_file(path)
    except UnicodeDecodeError as exc:
        raise ValueError(
            f"Cannot parse file '{path.name}' with extension '{suffix}'. "
            "Supported formats: PDF, TXT, MD, TEX, CSV."
        ) from exc


def parse_text_content(text: str, source_name: str = "pasted_text") -> str:
    """Pass through text content (for direct text input in UI)."""
    _ = source_name
    return text
