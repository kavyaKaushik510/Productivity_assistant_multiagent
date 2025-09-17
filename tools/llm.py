# tools/llm.py
from __future__ import annotations
import os
from typing import Dict
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv

from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

load_dotenv()

# Simple in-memory cache for prompt responses
_llm_cache: Dict[str, str] = {}


def get_llm() -> BaseChatModel:
    """Return a configured OpenAI chat model."""
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        raise ValueError("OPENAI_API_KEY not set. Please configure in .env")

    return ChatOpenAI(model="gpt-4o-mini", temperature=0.2)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_llm(prompt: str) -> str:
    """Call LLM with retries and simple caching."""
    if prompt in _llm_cache:
        return _llm_cache[prompt]

    llm = get_llm()
    response = llm.invoke(prompt)
    output = response.content if hasattr(response, "content") else str(response)

    _llm_cache[prompt] = output
    return output


# ---- Prompt Helpers ----

def email_to_tasks_prompt(email_text: str) -> str:
    """Prompt: extract a summary and action items from an email."""
    return f"""Summarize this email in one line, then list any clear action items as bullet points.

EMAIL:
{email_text}
"""


def transcript_to_tasks_prompt(transcript_text: str) -> str:
    """Prompt: extract a summary and action items from a meeting transcript."""
    return f"""Summarize this meeting in one line, list discussion points, and extract action items.

TRANSCRIPT:
{transcript_text}
"""


def email_to_tasks_json_prompt(email_text: str) -> str:
    """Prompt: extract summary and actionable tasks in strict JSON format."""
    return f"""Extract a concise summary and actionable tasks from this email.

EMAIL:
{email_text}

Respond strictly in JSON with:
{{
  "summary": "short summary",
  "tasks": [
    {{"title": "task description", "confidence": 0.9}}
  ]
}}

Guidelines:
- Only include real action items.
- Confidence is a float between 0 and 1.
- Max 10 tasks.
"""

