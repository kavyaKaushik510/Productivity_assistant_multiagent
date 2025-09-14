# tools/llm.py
from __future__ import annotations
import os
from typing import Dict
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv

from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI

# Load env vars from .env file
load_dotenv()

# Simple in-memory cache
_llm_cache: Dict[str, str] = {}


def get_llm() -> BaseChatModel:
    """
    Return a chat model instance.
    Prefers Gemini (GOOGLE_API_KEY), otherwise OpenAI (OPENAI_API_KEY).
    """
    google_key = os.getenv("GOOGLE_API_KEY")

    if google_key:
        return ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2)
    else:
        raise ValueError("No LLM provider available. Set GOOGLE_API_KEY in .env")


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_llm(prompt: str) -> str:
    """
    Call LLM with retries + caching.
    """
    if prompt in _llm_cache:
        return _llm_cache[prompt]

    llm = get_llm()
    response = llm.invoke(prompt)
    output = response.content if hasattr(response, "content") else str(response)

    _llm_cache[prompt] = output
    return output


# ---- Prompt Helpers ----

def email_to_tasks_prompt(email_text: str) -> str:
    return f"""
You are an assistant that extracts actionable tasks from an email.

EMAIL:
{email_text}

Return:
1. A short summary of the thread
2. A list of actionable tasks (bullet points).
"""


def transcript_to_tasks_prompt(transcript_text: str) -> str:
    return f"""
You are an assistant that extracts actionable tasks from a meeting transcript.

TRANSCRIPT:
{transcript_text}

Return:
1. A short meeting summary
2. A list of action items (bullet points).
"""

def email_to_tasks_json_prompt(email_text: str) -> str:
    return f"""
You are an assistant that extracts actionable tasks from an email.

EMAIL:
{email_text}

Return your answer strictly in JSON with this structure:

{{
  "summary": "short one-line summary of the email",
  "tasks": [
    {{"title": "clear, concise action item", "confidence": 0.85}},
    {{"title": "another action item", "confidence": 0.75}}
  ]
}}

Rules:
- Only include true action items (things the user must do).
- Skip boilerplate like "Summary:" or "Actionable Tasks:" headings.
- Confidence must be a number between 0 and 1.
- Maximum 5 tasks per email.
"""

