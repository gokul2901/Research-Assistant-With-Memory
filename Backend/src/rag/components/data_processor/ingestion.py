"""
Ingestion Job Manager for State Machine and Job Execution Tracking.
"""

from datetime import datetime
from typing import Dict, List, Optional
import uuid
from src.models.ingestion_job import IngestionJob
from src.utils.logger import logger


class IngestionJobManager:
    def __init__(self):
        self._jobs: Dict[str, IngestionJob] = {}

    def create_job(self, url: str, source_id: Optional[str] = None) -> IngestionJob:
        """Create and register a new QUEUED ingestion job."""
        job_id = f"job_{uuid.uuid4().hex[:12]}"
        if not source_id:
            source_id = f"src_{uuid.uuid4().hex[:12]}"

        job = IngestionJob(
            job_id=job_id,
            source_id=source_id,
            url=url,
            status="QUEUED",
            created_at=datetime.utcnow()
        )
        self._jobs[job_id] = job
        logger.info(f"Created ingestion job '{job_id}' for URL: {url} -> Source: {source_id}")
        return job

    def get_job(self, job_id: str) -> Optional[IngestionJob]:
        """Fetch job by ID."""
        return self._jobs.get(job_id)

    def update_job(
        self,
        job_id: str,
        status: Optional[str] = None,
        canonical_url: Optional[str] = None,
        error: Optional[str] = None,
        word_count: Optional[int] = None,
        chunk_count: Optional[int] = None,
        increment_retry: bool = False
    ) -> Optional[IngestionJob]:
        """Update job lifecycle status and metrics."""
        job = self._jobs.get(job_id)
        if not job:
            return None

        if status:
            job.status = status
            if status == "FETCHING" and not job.started_at:
                job.started_at = datetime.utcnow()
            elif status in ("COMPLETED", "FAILED", "DUPLICATE"):
                job.completed_at = datetime.utcnow()

        if canonical_url:
            job.canonical_url = canonical_url

        if error is not None:
            job.error = error

        if word_count is not None:
            job.word_count = word_count

        if chunk_count is not None:
            job.chunk_count = chunk_count

        if increment_retry:
            job.retry_count += 1

        return job

    def list_jobs(self, limit: int = 50) -> List[IngestionJob]:
        """List recently registered ingestion jobs."""
        jobs_list = list(self._jobs.values())
        jobs_list.sort(key=lambda j: j.created_at, reverse=True)
        return jobs_list[:limit]


# Global singleton instance
job_manager = IngestionJobManager()
