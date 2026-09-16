"""
Domain Model for Ingestion Jobs and Task Tracking.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class IngestionJob(BaseModel):
    job_id: str = Field(..., description="Unique ingestion job identifier")
    source_id: str = Field(..., description="Target source ID in persistent memory")
    url: str = Field(..., description="Original submitted target URL")
    canonical_url: Optional[str] = Field(None, description="Resolved canonical URL")
    status: str = Field(
        "QUEUED",
        description="Current state: QUEUED, FETCHING, SCRAPING, EXTRACTING, CLEANING, CHUNKING, EMBEDDING, INDEXING, COMPLETED, FAILED, DUPLICATE"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    retry_count: int = 0
    word_count: int = 0
    chunk_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)
