"""
Data Loader — Handles loading and extracting text from PDF documents.
Supports both file-path and byte-stream inputs.
"""

import fitz  # PyMuPDF
from pathlib import Path


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extract all text from PDF bytes (for resume uploads)."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text_parts = []
    for page_num in range(len(doc)):
        text_parts.append(doc[page_num].get_text("text"))
    doc.close()
    return "\n".join(text_parts)


def extract_pages_from_pdf(pdf_path: str) -> list[dict]:
    """
    Extract text page-by-page from a PDF file.
    Returns list of {"page_num": int, "text": str} dicts.
    """
    doc = fitz.open(pdf_path)
    pages = []
    for page_num in range(len(doc)):
        text = doc[page_num].get_text("text")
        if text.strip():
            pages.append({
                "page_num": page_num + 1,
                "text": text.strip(),
            })
    doc.close()
    return pages


def find_pdf_files(directory: str) -> list[Path]:
    """Find all PDF files in a directory recursively."""
    return list(Path(directory).rglob("*.pdf"))
