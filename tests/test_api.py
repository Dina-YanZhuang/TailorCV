"""Integration tests for the /api/tailor endpoint (mocked AI)."""

from __future__ import annotations

import io
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

_MOCK_TAILORED = "## John Doe\n\n**Python Developer**\n\n- Tailored bullet point\n"

_CV_TXT = b"John Doe\nPython Developer\n5 years of experience in web development."
_JD_TXT = b"We are looking for a Python Developer with FastAPI experience."


def _mock_tailor(cv_text: str, jd_text: str, **_) -> str:
    return _MOCK_TAILORED


# ── happy-path tests ──────────────────────────────────────────────────────────

def test_tailor_with_txt_files():
    with patch("app.main.tailor_cv", side_effect=_mock_tailor):
        resp = client.post(
            "/api/tailor",
            files={
                "cv_file": ("cv.txt", io.BytesIO(_CV_TXT), "text/plain"),
                "jd_file": ("jd.txt", io.BytesIO(_JD_TXT), "text/plain"),
            },
        )
    assert resp.status_code == 200
    body = resp.json()
    assert "tailored_cv" in body
    assert "John Doe" in body["tailored_cv"]


def test_tailor_with_jd_text_form_field():
    with patch("app.main.tailor_cv", side_effect=_mock_tailor):
        resp = client.post(
            "/api/tailor",
            files={"cv_file": ("cv.txt", io.BytesIO(_CV_TXT), "text/plain")},
            data={"jd_text": "Looking for a Python developer."},
        )
    assert resp.status_code == 200
    assert "tailored_cv" in resp.json()


# ── validation error tests ────────────────────────────────────────────────────

def test_missing_cv_file_returns_422():
    resp = client.post(
        "/api/tailor",
        data={"jd_text": "Some job description"},
    )
    assert resp.status_code == 422


def test_missing_jd_returns_400():
    resp = client.post(
        "/api/tailor",
        files={"cv_file": ("cv.txt", io.BytesIO(_CV_TXT), "text/plain")},
    )
    assert resp.status_code == 400
    assert "job description" in resp.json()["detail"].lower()


def test_unsupported_cv_format_returns_400():
    with patch("app.main.tailor_cv", side_effect=_mock_tailor):
        resp = client.post(
            "/api/tailor",
            files={
                "cv_file": ("cv.odt", io.BytesIO(b"odt data"), "application/octet-stream"),
                "jd_file": ("jd.txt", io.BytesIO(_JD_TXT), "text/plain"),
            },
        )
    assert resp.status_code == 400
    assert "Unsupported file type" in resp.json()["detail"]


def test_empty_cv_text_returns_400():
    with patch("app.main.tailor_cv", side_effect=_mock_tailor):
        resp = client.post(
            "/api/tailor",
            files={
                "cv_file": ("cv.txt", io.BytesIO(b"   "), "text/plain"),
                "jd_file": ("jd.txt", io.BytesIO(_JD_TXT), "text/plain"),
            },
        )
    assert resp.status_code == 400


def test_missing_api_key_returns_500():
    """If OPENAI_API_KEY is absent the endpoint must return 500."""
    import os

    original_key = os.environ.pop("OPENAI_API_KEY", None)
    try:
        resp = client.post(
            "/api/tailor",
            files={
                "cv_file": ("cv.txt", io.BytesIO(_CV_TXT), "text/plain"),
                "jd_file": ("jd.txt", io.BytesIO(_JD_TXT), "text/plain"),
            },
        )
        assert resp.status_code == 500
        assert "OPENAI_API_KEY" in resp.json()["detail"]
    finally:
        if original_key:
            os.environ["OPENAI_API_KEY"] = original_key


# ── index page ────────────────────────────────────────────────────────────────

def test_index_returns_html():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "TailorCV" in resp.text
