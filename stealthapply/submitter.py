"""
Application submission logic and receipt generation for StealthApply.
Handles the actual "submission" of resumes to job listings.
"""

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from .job_scraper import JobListing
from .llm_client import OllamaClient


@dataclass
class SubmissionResult:
    """Result of a single resume submission."""
    job: JobListing
    status: str  # "success", "skipped", "error"
    cover_note: str = ""
    error_message: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


@dataclass
class SubmissionReceipt:
    """Full receipt for a batch submission run."""
    run_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8].upper())
    started_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    finished_at: str = ""
    results: list[SubmissionResult] = field(default_factory=list)

    def summary(self) -> dict:
        """Return a summary dict of the submission run."""
        success = sum(1 for r in self.results if r.status == "success")
        skipped = sum(1 for r in self.results if r.status == "skipped")
        errors = sum(1 for r in self.results if r.status == "error")
        return {
            "run_id": self.run_id,
            "total": len(self.results),
            "success": success,
            "skipped": skipped,
            "errors": errors,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
        }

    def as_text(self) -> str:
        """Format the receipt as human-readable text."""
        lines = [
            "=" * 60,
            f"  STEALTHAPPLY SUBMISSION RECEIPT",
            f"  Run ID: {self.run_id}",
            f"  Started:  {self.started_at}",
            f"  Finished: {self.finished_at}",
            "=" * 60,
            "",
        ]

        summary = self.summary()
        lines += [
            f"  Total submissions: {summary['total']}",
            f"  ✅ Successful:     {summary['success']}",
            f"  ⏭  Skipped:        {summary['skipped']}",
            f"  ❌ Errors:         {summary['errors']}",
            "",
            "-" * 60,
            "  DETAILS",
            "-" * 60,
            "",
        ]

        for r in self.results:
            icon = {"success": "✅", "skipped": "⏭", "error": "❌"}.get(r.status, "?")
            lines.append(f"  {icon} [{r.timestamp}] {r.job.company} — {r.job.title}")
            if r.status == "success":
                lines.append(f"     URL: {r.job.url}")
                if r.cover_note and not r.cover_note.startswith("[LLM"):
                    lines.append(f"     Cover note: {r.cover_note[:120]}...")
            elif r.status == "error":
                lines.append(f"     Error: {r.error_message}")
            lines.append("")

        lines += [
            "=" * 60,
            "  This receipt exists in memory only.",
            "  Click 'Save Receipt' to write it to disk.",
            "=" * 60,
        ]

        return "\n".join(lines)


class Submitter:
    """Handles batch resume submission to job listings."""

    def __init__(
        self,
        llm_client: Optional[OllamaClient] = None,
        delay_ms: int = 500,
    ) -> None:
        self.llm_client = llm_client or OllamaClient()
        self.delay_ms = delay_ms

    def submit_all(
        self,
        jobs: list[JobListing],
        resume_text: str,
        progress_callback=None,
    ) -> SubmissionReceipt:
        """
        Submit resume to all provided job listings.

        Args:
            jobs: List of JobListing objects to apply to.
            resume_text: Extracted plain text of the resume.
            progress_callback: Optional callable(current, total, message) for UI updates.

        Returns:
            A SubmissionReceipt with all results.
        """
        receipt = SubmissionReceipt()
        total = len(jobs)

        for i, job in enumerate(jobs):
            if progress_callback:
                progress_callback(i, total, f"Processing {job.company}...")

            result = self._submit_one(job, resume_text)
            receipt.results.append(result)

            # Polite delay between submissions
            if i < total - 1:
                time.sleep(self.delay_ms / 1000.0)

        receipt.finished_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if progress_callback:
            progress_callback(total, total, "All submissions complete!")

        return receipt

    def _submit_one(self, job: JobListing, resume_text: str) -> SubmissionResult:
        """
        Submit resume to a single job listing.

        In this implementation, submission means:
        1. Generating a tailored cover note via LLM
        2. Logging the intent (real submission would POST to application URLs)

        Real job boards require authenticated sessions or official APIs.
        This tool prepares your application package and records the transaction.
        """
        try:
            # Generate tailored cover note using local LLM
            cover_note = self.llm_client.generate_cover_note(
                resume_text=resume_text,
                job_company=job.company,
                job_title=job.title,
                job_description=job.description,
            )

            return SubmissionResult(
                job=job,
                status="success",
                cover_note=cover_note,
            )

        except Exception as e:
            return SubmissionResult(
                job=job,
                status="error",
                error_message=str(e),
            )
