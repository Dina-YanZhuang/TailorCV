import json
import os
import subprocess
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TEMPLATE = "agent_template.tex"
DATA = "master_cv.json"
JD_FILE = "jd.txt"


# ---------- Helpers ----------

def load_json():
    with open(DATA, "r", encoding="utf-8") as f:
        return json.load(f)


def load_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def save_text(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def escape_latex(text):
    rep = {
        "&": "\\&",
        "%": "\\%",
        "$": "\\$",
        "#": "\\#",
        "_": "\\_",
        "{": "\\{",
        "}": "\\}"
    }
    for k, v in rep.items():
        text = text.replace(k, v)
    return text


def ask_gpt(prompt):
    resp = client.chat.completions.create(
        model="gpt-5-3",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )
    return resp.choices[0].message.content


# ---------- Step 1: Parse JD ----------

def parse_jd(jd):
    prompt = f"""
Extract the following from this job description.
Return valid JSON only.

Fields:
skills
responsibilities
keywords
tone

JD:
{jd}
"""
    out = ask_gpt(prompt)
    return json.loads(out)


# ---------- Step 2: Match Experience ----------

def match_experience(jd_struct, data):
    prompt = f"""
You are matching job requirements with candidate experience.

Job requirements:
{json.dumps(jd_struct)}

Candidate experiences:
{json.dumps(data["experiences"])}

Return top 4 most relevant experiences as JSON array.
Only return JSON.
"""
    out = ask_gpt(prompt)
    return json.loads(out)


# ---------- Step 3: Summary ----------

def generate_summary(jd, matched):
    prompt = f"""
Write a concise professional summary for a CV.

Use candidate experience and align to the job.

Job:
{jd}

Experience:
{json.dumps(matched)}

Max 55 words.
Professional tone.
"""
    return ask_gpt(prompt).strip()


# ---------- Step 4: Rewrite Bullets ----------

def generate_experience_block(matched, jd):
    blocks = []

    for exp in matched:
        prompt = f"""
Rewrite 2 strong CV bullet points tailored to this job.

Job:
{jd}

Experience:
{json.dumps(exp)}

Rules:
- concise
- achievement-oriented
- no buzzwords
Return as JSON array of strings.
"""
        bullets = json.loads(ask_gpt(prompt))

        block = f"""
\\textbf{{{escape_latex(exp['title'])}}} \\\\
\\textit{{{escape_latex(exp['company'])}}} \\dates{{{exp['start_date']}--{exp['end_date']}}}\\\\
\\tightis
"""
        for b in bullets:
            block += f"\\smaller{{{escape_latex(b)}}}\n\\is\n"

        block += "\\jobsep\n"
        blocks.append(block)

    return "\n".join(blocks)


# ---------- Education ----------

def build_education(data):
    out = []
    for edu in data["education"]:
        out.append(f"""
\\textsc{{{escape_latex(edu['degree'])}}} \\\\
from \\textit{{{escape_latex(edu['institution'])}}}. \\dates{{{edu['start_date']}--{edu['end_date']}}}
\\is
""")
    return "\n".join(out)


# ---------- Cover Letter ----------

def generate_cover_letter(jd, matched):
    prompt = f"""
Write a tailored cover letter.

Structure:
1 opening
2 body paragraphs
1 closing

Use:
Job:
{jd}

Candidate:
{json.dumps(matched)}

Max 320 words.
"""
    return ask_gpt(prompt)


# ---------- Main ----------

def main():
    data = load_json()
    jd = load_text(JD_FILE)
    template = load_text(TEMPLATE)

    print("Parsing JD...")
    jd_struct = parse_jd(jd)

    print("Matching experience...")
    matched = match_experience(jd_struct, data)

    print("Generating summary...")
    summary = generate_summary(jd, matched)

    print("Generating experience block...")
    exp_block = generate_experience_block(matched, jd)

    replacements = {
        "{{FULL_NAME}}": data["profile"]["name"],
        "{{PHOTO_PATH}}": "Yan.jpg",
        "{{PROFILE_SUMMARY}}": escape_latex(summary),
        "{{CONTACT_BLOCK}}": f"""
\\faEnvelope\\ yanzhuang0128@gmail.com \\\\[0.4em]
\\faPhone\\ +46 767086693 \\\\[0.4em]
\\faLinkedin\\ linkedin.com/in/yan-zhuang
""",
        "{{CORE_CAPABILITIES}}": "\\begin{itemize}\\item Strategic Communication\\item Market Research\\item Cross-functional Collaboration\\item AI Product Knowledge\\item User Insights\\end{itemize}",
        "{{LANGUAGE_BLOCK}}": "\\textbf{Chinese}: Native\\\\ \\textbf{English}: Professional\\\\ \\textbf{Swedish}: Conversational\\\\",
        "{{EDUCATION_BLOCK}}": build_education(data),
        "{{EXPERIENCE_BLOCK}}": exp_block
    }

    for k, v in replacements.items():
        template = template.replace(k, v)

    save_text("tailored_cv.tex", template)

    subprocess.run(["pdflatex", "tailored_cv.tex"])

    print("Generating cover letter...")
    cl = generate_cover_letter(jd, matched)
    save_text("tailored_cover_letter.txt", cl)

    print("Done.")


if __name__ == "__main__":
    main()