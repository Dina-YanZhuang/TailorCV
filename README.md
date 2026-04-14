# ✂️ TailorCV — AI-Powered CV Refining Agent

TailorCV takes your **master CV** and a **job description** and uses GPT-4o to produce a tailored CV optimised for that specific role — keyword-matched, ATS-friendly, and professionally written.

---

## Features

- 📄 Upload your CV as **PDF**, **DOCX**, or **TXT**
- 💼 Provide the job description as a **file** or **pasted text**
- 🤖 AI rewrites and reorganises your CV to match the role
- 📋 Copy the result or **download it as Markdown**

---

## Quick Start

### 1. Clone & install dependencies

```bash
git clone https://github.com/Dina-YanZhuang/TailorCV.git
cd TailorCV
pip install -r requirements.txt
```

### 2. Set your OpenAI API key

```bash
cp .env.example .env
# Edit .env and replace sk-... with your real key
```

### 3. Run the server

```bash
uvicorn app.main:app --reload
```

Open **http://localhost:8000** in your browser.

---

## Project Structure

```
TailorCV/
├── app/
│   ├── main.py          # FastAPI app & API routes
│   ├── parser.py        # PDF / DOCX / TXT text extraction
│   ├── ai_agent.py      # OpenAI GPT-4o CV tailoring logic
│   └── static/
│       ├── index.html   # Single-page UI
│       ├── style.css    # Styles
│       └── app.js       # Client-side logic
├── tests/
│   └── test_parser.py   # Unit tests for document parsing
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## API

### `POST /api/tailor`

**Form data** (multipart):

| Field     | Type        | Required | Description                              |
|-----------|-------------|----------|------------------------------------------|
| `cv_file` | File upload | ✅        | Master CV (PDF, DOCX, or TXT, ≤ 10 MB)  |
| `jd_file` | File upload | *or*     | Job description file (PDF, DOCX, or TXT) |
| `jd_text` | String      | *or*     | Raw job description text                 |

**Response** `200 OK`:

```json
{
  "tailored_cv": "## John Smith\n\n..."
}
```

---

## Requirements

- Python 3.10+
- An [OpenAI API key](https://platform.openai.com/api-keys) with access to `gpt-4o`

---

## License

MIT