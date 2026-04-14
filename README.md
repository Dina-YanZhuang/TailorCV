# TailorCV

TailorCV is an AI-powered CV refining agent. Upload your master CV and a job description, and the app rewrites your CV to match the role — highlighting the most relevant skills and experience.

---

## Features

- **Document upload** – accepts master CV in PDF or DOCX format
- **Job description input** – upload a file or paste the text directly
- **AI tailoring** – uses OpenAI to rewrite and optimise your CV for the target role
- **Download** – get the tailored CV as a ready-to-use document
- **Simple web UI** – clean HTML/CSS/JS frontend with loading state and result display

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python · FastAPI |
| AI | OpenAI API |
| Document parsing | PDF / DOCX → plain text |
| Frontend | HTML · CSS · JavaScript |

---

## Getting Started

### Prerequisites

- Python 3.10+
- An [OpenAI API key](https://platform.openai.com/api-keys)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Dina-YanZhuang/TailorCV.git
cd TailorCV

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Open .env and add your OpenAI API key
```

### Running the App

```bash
uvicorn main:app --reload
```

Open `http://localhost:8000` in your browser.

---

## Usage

1. **Upload your master CV** (PDF or DOCX).
2. **Provide the job description** – upload a file or paste the text into the input box.
3. Click **Tailor my CV** and wait for the AI to process your documents.
4. **Download** the tailored CV.

---

## Project Structure

```
TailorCV/
├── main.py            # FastAPI application and API endpoints
├── requirements.txt   # Python dependencies
├── .env.example       # Environment variable template
├── static/            # Frontend assets (HTML, CSS, JS)
└── README.md
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | Your OpenAI API key |

Copy `.env.example` to `.env` and fill in the values before running the app.

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a pull request

---

## License

This project is open source. See [LICENSE](LICENSE) for details.
