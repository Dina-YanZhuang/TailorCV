"""Document parsing utilities for PDF, DOCX, and plain-text files."""

from __future__ import annotations

import io


def extract_text(filename: str, file_bytes: bytes) -> str:
    """Return the plain-text content of an uploaded document.

    Supported formats: .pdf, .docx, .txt
    """
    ext = filename.rsplit(".", 1)[-1].lower()

    if ext == "pdf":
        return _parse_pdf(file_bytes)
    if ext == "docx":
        return _parse_docx(file_bytes)
    if ext == "txt":
        return file_bytes.decode("utf-8", errors="replace")

    raise ValueError(
        f"Unsupported file type '.{ext}'. Please upload a PDF, DOCX, or TXT file."
    )


def _parse_pdf(data: bytes) -> str:
    import pdfplumber  # imported lazily to keep startup fast

    text_parts: list[str] = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n\n".join(text_parts)


def _parse_docx(data: bytes) -> str:
    from docx import Document  # python-docx

    doc = Document(io.BytesIO(data))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)
