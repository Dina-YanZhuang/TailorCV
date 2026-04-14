"""FastAPI application for TailorCV."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.ai_agent import tailor_cv
from app.parser import extract_text

load_dotenv()

app = FastAPI(title="TailorCV", version="1.0.0")

_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

_STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")


@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    return FileResponse(str(_STATIC_DIR / "index.html"))


@app.post("/api/tailor")
async def tailor(
    cv_file: UploadFile = File(..., description="Master CV (PDF, DOCX, or TXT)"),
    jd_file: UploadFile | None = File(
        None, description="Job description file (PDF, DOCX, or TXT) — optional"
    ),
    jd_text: str | None = Form(
        None, description="Job description text — used when no file is uploaded"
    ),
) -> JSONResponse:
    """Tailor the uploaded CV for the given job description.

    Accepts either a job-description *file* or raw *text* (not both required).
    """
    # --- read and validate CV file ---
    cv_bytes = await cv_file.read()
    if len(cv_bytes) > _MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="CV file exceeds the 10 MB limit.")
    if not cv_file.filename:
        raise HTTPException(status_code=400, detail="CV file has no filename.")

    try:
        cv_content = extract_text(cv_file.filename, cv_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not cv_content.strip():
        raise HTTPException(
            status_code=400,
            detail="Could not extract any text from the CV file. "
            "Please make sure the file is not scanned/image-only.",
        )

    # --- read job description ---
    jd_content: str = ""
    if jd_file and jd_file.filename:
        jd_bytes = await jd_file.read()
        if len(jd_bytes) > _MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413, detail="Job description file exceeds the 10 MB limit."
            )
        try:
            jd_content = extract_text(jd_file.filename, jd_bytes)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    elif jd_text:
        jd_content = jd_text

    if not jd_content.strip():
        raise HTTPException(
            status_code=400,
            detail="Please provide the job description — either upload a file or paste the text.",
        )

    # --- call the AI agent ---
    try:
        tailored = tailor_cv(cv_content, jd_content)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=502, detail=f"OpenAI API error: {exc}"
        ) from exc

    return JSONResponse({"tailored_cv": tailored})
