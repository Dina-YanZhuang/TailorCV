"""AI agent that tailors a CV for a specific job description using OpenAI."""

from __future__ import annotations

import os

from openai import OpenAI

_SYSTEM_PROMPT = """\
You are an expert career coach and professional CV writer.

Your task is to tailor the candidate's master CV for a specific job description.

Follow these guidelines:
1. Carefully read the job description and identify the key required skills,
   qualifications, technologies, and responsibilities.
2. Rewrite and reorganise the CV so that the most relevant experience and skills
   appear prominently.
3. Use strong action verbs and quantify achievements where possible.
4. Mirror keywords and phrases from the job description (for ATS optimisation)
   without fabricating experience or qualifications.
5. Remove or de-emphasise sections/bullet points that are not relevant to this role.
6. Keep the output well-structured with clear Markdown headings (##), bullet lists,
   and bold text for section titles.
7. Return ONLY the tailored CV content in Markdown — no preamble, no commentary.
"""

_USER_TEMPLATE = """\
## Master CV

{cv_text}

---

## Job Description

{jd_text}

---

Please tailor the CV above for the job description above.
"""


def tailor_cv(cv_text: str, jd_text: str, model: str = "gpt-4o") -> str:
    """Return a tailored CV in Markdown format.

    Requires the OPENAI_API_KEY environment variable to be set.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY environment variable is not set. "
            "Please add it to your .env file."
        )

    client = OpenAI(api_key=api_key)

    user_message = _USER_TEMPLATE.format(cv_text=cv_text, jd_text=jd_text)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.4,
    )

    return response.choices[0].message.content or ""
