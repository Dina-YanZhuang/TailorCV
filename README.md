# TailorCV

TailorCV is an AI-powered tool that automatically generates a tailored CV and cover letter for a specific job posting. It reads your master CV data and a job description, uses GPT to select the most relevant experiences and rewrite bullet points, and then compiles a polished PDF via LaTeX.

---

## How It Works

The pipeline in `generate_v2.py` runs five steps in sequence:

1. **Parse JD** – Sends the job description to GPT and extracts structured fields: required skills, responsibilities, keywords, and tone.
2. **Match experience** – Asks GPT to pick the top 4 most relevant entries from your `master_cv.json` experiences based on the job requirements.
3. **Generate summary** – Produces a concise professional summary (max 55 words) aligned to the target role.
4. **Rewrite bullets** – For each matched experience, GPT writes 2 achievement-oriented bullet points tailored to the job.
5. **Compile & output** – Fills placeholders in `agent_template.tex`, compiles the result with `pdflatex`, and writes a cover letter to a text file.

**Outputs:**
- `tailored_cv.tex` – The filled LaTeX source file.
- `tailored_cv.pdf` – The compiled, ready-to-send CV.
- `tailored_cover_letter.txt` – A tailored cover letter (max 320 words).

---

## Prerequisites

| Requirement | Notes |
|---|---|
| Python 3.9+ | |
| `pdflatex` | Part of [TeX Live](https://www.tug.org/texlive/) or [MiKTeX](https://miktex.org/). Must be on your `PATH`. |
| OpenAI API key | Used to call the GPT model. |

The LaTeX template uses the following packages: `fontawesome`, `FiraSans`, `microtype`, `enumitem`, `hyperref`, `graphicx`, `xcolor`. Install any missing packages via your TeX distribution's package manager.

---

## Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Dina-YanZhuang/TailorCV.git
   cd TailorCV
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` file** in the project root with your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-...
   ```

---

## Usage

1. **Edit `master_cv.json`** with your full work history, education, and profile. The file contains:
   - `profile` – name and languages.
   - `experiences` – list of roles, each with company, title, dates, tags, skills, and raw bullet data.
   - `education` – list of degrees with institution, dates, and optional thesis details.

2. **Create `jd.txt`** in the project root and paste the full text of the job description you are targeting.

3. **(Optional) Add a profile photo** named `Yan.jpg` (or update the `{{PHOTO_PATH}}` replacement in `generate_v2.py`) in the project root.

4. **Run the generator:**
   ```bash
   python generate_v2.py
   ```
   The script prints its progress and produces `tailored_cv.pdf` and `tailored_cover_letter.txt`.

---

## Project Structure

```
TailorCV/
├── generate_v2.py          # Main script – orchestrates the full pipeline
├── master_cv.json          # Your complete CV data (edit this with your own info)
├── agent_template.tex      # LaTeX CV template with {{PLACEHOLDER}} variables
├── requirements.txt        # Python dependencies
├── jd.txt                  # Job description to target (you create this each run)
├── tailored_cv.tex         # Generated LaTeX source (output)
├── tailored_cv.pdf         # Compiled PDF CV (output)
└── tailored_cover_letter.txt  # Generated cover letter (output)
```

### Template Placeholders

`agent_template.tex` uses the following placeholders that `generate_v2.py` replaces at runtime:

| Placeholder | Content |
|---|---|
| `{{FULL_NAME}}` | Candidate name from `master_cv.json` |
| `{{PHOTO_PATH}}` | Path to profile photo |
| `{{PROFILE_SUMMARY}}` | GPT-generated professional summary |
| `{{CONTACT_BLOCK}}` | Email, phone, and LinkedIn |
| `{{CORE_CAPABILITIES}}` | Key skills list |
| `{{LANGUAGE_BLOCK}}` | Languages and proficiency levels |
| `{{EDUCATION_BLOCK}}` | Formatted education entries |
| `{{EXPERIENCE_BLOCK}}` | GPT-tailored experience entries |

---

## Customisation

- **Contact details and core capabilities** are currently hardcoded in the `replacements` dictionary inside `main()` in `generate_v2.py`. Edit those strings directly to reflect your own information.
- **Photo**: Place your photo in the project root and update the `{{PHOTO_PATH}}` value in `generate_v2.py`.
- **Number of matched experiences**: Change the instruction `"Return top 4 most relevant experiences"` in `match_experience()` to any number you prefer.
- **Summary length**: The default cap is 55 words. Adjust the prompt in `generate_summary()`.
