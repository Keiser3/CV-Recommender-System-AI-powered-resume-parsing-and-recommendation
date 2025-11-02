# parser.py
import os
from dotenv import load_dotenv
import httpx
import json
import re

load_dotenv()  # loads variables from .env

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")  # now available

PROMPT_TEMPLATE = """
Extract the following information from the CV:

- degree
- field
- institution
- year

Return as JSON with keys: "degree", "field", "institution", "year".

CV Text:
{cv_text}
"""

async def parse_cv_with_llm(cv_text: str) -> dict:
    prompt = PROMPT_TEMPLATE.format(cv_text=cv_text[:3800])
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    json_body = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "max_tokens": 800
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post("https://api.openrouter.ai/v1/chat/completions", json=json_body, headers=headers)
        r.raise_for_status()
        out = r.json()

    llm_text = out["choices"][0]["message"]["content"]

    try:
        parsed = json.loads(llm_text)
    except Exception:
        m = re.search(r"\{.*\}", llm_text, re.S)
        parsed = json.loads(m.group(0)) if m else {}

    # Ensure keys exist to avoid KeyError
    for key in ["degree", "field", "institution", "year"]:
        parsed.setdefault(key, None)

    return parsed
