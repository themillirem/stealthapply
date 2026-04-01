"""
Ollama LLM client for StealthApply.
Generates tailored cover letter snippets using a local LLM.
"""

import json
from typing import Optional
import requests

from .config import OLLAMA_BASE_URL, OLLAMA_DEFAULT_MODEL, OLLAMA_TIMEOUT


class OllamaClient:
    """Client for the Ollama local LLM API."""

    def __init__(
        self,
        base_url: str = OLLAMA_BASE_URL,
        model: str = OLLAMA_DEFAULT_MODEL,
        timeout: int = OLLAMA_TIMEOUT,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def is_available(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False

    def list_models(self) -> list[str]:
        """Return a list of available model names."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            resp.raise_for_status()
            data = resp.json()
            return [m["name"] for m in data.get("models", [])]
        except Exception:
            return []

    def generate_cover_note(
        self,
        resume_text: str,
        job_company: str,
        job_title: str,
        job_description: str,
    ) -> str:
        """
        Generate a brief, tailored cover letter note for a specific job.

        Args:
            resume_text: Full text of the applicant's resume.
            job_company: Company name.
            job_title: Job title.
            job_description: Job description text.

        Returns:
            A 2-3 sentence tailored cover note, or an error message if LLM is unavailable.
        """
        if not self.is_available():
            return (
                f"[LLM unavailable] Submitting resume for {job_title} at {job_company} "
                "without tailored cover note."
            )

        prompt = f"""You are helping a mechanical engineer apply for a SolidWorks engineering job.
Based on the resume and job description below, write a brief 2-3 sentence cover note 
that highlights the most relevant experience. Be specific, professional, and concise.

RESUME:
{resume_text[:2000]}

JOB:
Company: {job_company}
Title: {job_title}
Description: {job_description}

Write only the cover note text, nothing else."""

        try:
            resp = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 200,
                    },
                },
                timeout=self.timeout,
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", "").strip()
        except requests.Timeout:
            return f"[LLM timeout] Cover note generation timed out for {job_title} at {job_company}."
        except Exception as e:
            return f"[LLM error] {str(e)}"
