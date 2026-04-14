"""Unit tests for the document parser."""

from __future__ import annotations

import io
import textwrap

import pytest


# ── helpers to generate minimal in-memory documents ──────────────────────────

def _make_pdf_bytes(text: str) -> bytes:
    """Create a minimal single-page PDF containing *text*."""
    import pdfplumber  # noqa: F401  (ensures import works before the real test)

    # We use reportlab only when available; otherwise fall back to a pre-baked PDF.
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=letter)
        c.drawString(72, 720, text)
        c.save()
        return buf.getvalue()
    except ImportError:
        # Minimal valid PDF (contains the given text literally in a stream)
        pdf = textwrap.dedent(f"""\
            %PDF-1.4
            1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
            2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
            3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>endobj
            4 0 obj<</Length {len(text) + 30}>>
            stream
            BT /F1 12 Tf 72 720 Td ({text}) Tj ET
            endstream
            endobj
            5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj
            xref
            0 6
            0000000000 65535 f\r
            trailer<</Size 6/Root 1 0 R>>
            startxref
            0
            %%EOF
        """).encode()
        return pdf


def _make_docx_bytes(text: str) -> bytes:
    """Create a minimal DOCX file containing *text*."""
    from docx import Document

    doc = Document()
    doc.add_paragraph(text)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


# ── parser tests ──────────────────────────────────────────────────────────────

from app.parser import extract_text  # noqa: E402 (after helpers)


def test_extract_txt_basic():
    data = b"Hello, world!\nSecond line."
    result = extract_text("resume.txt", data)
    assert "Hello, world!" in result
    assert "Second line." in result


def test_extract_txt_utf8():
    text = "Ünïcödé résumé"
    result = extract_text("cv.txt", text.encode("utf-8"))
    assert text in result


def test_extract_docx_basic():
    text = "Software Engineer with 5 years of experience."
    docx_bytes = _make_docx_bytes(text)
    result = extract_text("resume.docx", docx_bytes)
    assert text in result


def test_extract_unsupported_type():
    with pytest.raises(ValueError, match="Unsupported file type"):
        extract_text("resume.odt", b"data")


def test_extract_unsupported_type_rtf():
    with pytest.raises(ValueError, match="Unsupported file type"):
        extract_text("cv.rtf", b"{\\rtf1 hello}")


def test_filename_case_insensitive_extension():
    """Extension matching should be case-insensitive."""
    text = "Senior Developer"
    docx_bytes = _make_docx_bytes(text)
    # .DOCX in uppercase
    result = extract_text("RESUME.DOCX", docx_bytes)
    assert text in result


def test_extract_pdf_basic():
    """Smoke test: pdfplumber can read a PDF produced by our helper."""
    try:
        from reportlab.pdfgen import canvas as _  # noqa: F401
    except ImportError:
        pytest.skip("reportlab not installed — skipping PDF smoke test")

    text = "John Doe — Python Developer"
    pdf_bytes = _make_pdf_bytes(text)
    result = extract_text("cv.pdf", pdf_bytes)
    assert "John Doe" in result
