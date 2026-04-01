"""
Resume parser for StealthApply.
Extracts plain text from PDF and DOCX resume files.
"""

import os
from pathlib import Path
from typing import Optional


def parse_resume(file_path: str) -> str:
    """
    Extract plain text from a resume file.

    Supports PDF (.pdf) and Word (.docx) formats.

    Args:
        file_path: Absolute path to the resume file.

    Returns:
        Extracted text as a string.

    Raises:
        ValueError: If the file format is not supported.
        FileNotFoundError: If the file does not exist.
        RuntimeError: If parsing fails.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Resume file not found: {file_path}")

    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return _parse_pdf(str(path))
    elif suffix == ".docx":
        return _parse_docx(str(path))
    else:
        raise ValueError(
            f"Unsupported file format: '{suffix}'. Please use PDF (.pdf) or Word (.docx)."
        )


def _parse_pdf(file_path: str) -> str:
    """Extract text from a PDF file using PyPDF2."""
    try:
        import PyPDF2
    except ImportError:
        raise RuntimeError(
            "PyPDF2 is not installed. Run: pip install PyPDF2"
        )

    text_parts: list[str] = []

    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page_num, page in enumerate(reader.pages):
                try:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
                except Exception as e:
                    # Skip pages that fail to parse
                    text_parts.append(f"[Page {page_num + 1} could not be read]")
    except Exception as e:
        raise RuntimeError(f"Failed to parse PDF: {e}")

    full_text = "\n".join(text_parts).strip()
    if not full_text:
        raise RuntimeError("No text could be extracted from the PDF. It may be image-based.")

    return full_text


def _parse_docx(file_path: str) -> str:
    """Extract text from a DOCX file using python-docx."""
    try:
        from docx import Document
    except ImportError:
        raise RuntimeError(
            "python-docx is not installed. Run: pip install python-docx"
        )

    try:
        doc = Document(file_path)
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        full_text = "\n".join(paragraphs).strip()
    except Exception as e:
        raise RuntimeError(f"Failed to parse DOCX: {e}")

    if not full_text:
        raise RuntimeError("No text could be extracted from the DOCX file.")

    return full_text


def get_resume_preview(text: str, max_chars: int = 500) -> str:
    """Return a short preview of the resume text for display."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."
