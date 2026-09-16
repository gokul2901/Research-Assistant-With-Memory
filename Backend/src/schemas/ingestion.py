"""
Pydantic schemas for URL Ingestion, n8n Callbacks, and Job Management.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator


class IngestUrlRequest(BaseModel):
    """
    Accepts single URL format:
    {"url": "https://example.com"}
    OR multi-URL batch format:
    {"urls": ["https://site1.com", "https://site2.com"]}
    """
    url: Optional[str] = Field(None, description="Single URL to ingest")
    urls: Optional[List[str]] = Field(None, description="List of URLs to ingest")
    force_refresh: bool = Field(False, description="Force re-indexing even if content hash is unchanged")

    @field_validator("url", mode="before")
    def validate_single_url(cls, v):
        if v and not isinstance(v, str):
            return str(v)
        return v

    def get_urls(self) -> List[str]:
        target_urls = []
        if self.url:
            target_urls.append(self.url.strip())
        if self.urls:
            target_urls.extend([u.strip() for u in self.urls if u and u.strip()])
        # Deduplicate while preserving order
        seen = set()
        deduped = []
        for u in target_urls:
            if u not in seen:
                seen.add(u)
                deduped.append(u)
        return deduped


class IngestionItemResult(BaseModel):
    source_id: str
    url: str
    title: str
    domain: str
    status: str
    chunk_count: int
    character_count: int
    content_hash: str
    date_added: datetime
    error_message: Optional[str] = None


class IngestionSummaryResponse(BaseModel):
    total_requested: int
    successful_count: int
    failed_count: int
    duplicate_count: int
    results: List[IngestionItemResult]


class IngestionJobResponse(BaseModel):
    job_id: str
    source_id: str
    url: str
    canonical_url: Optional[str] = None
    status: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    word_count: int = 0
    chunk_count: int = 0


class BulkIngestionResponse(BaseModel):
    total_submitted: int
    jobs: List[IngestionJobResponse]


class IngestionCallbackPayload(BaseModel):
    """
    Payload received from n8n scraping workflow callback.
    """
    job_id: str = Field(..., description="Ingestion Job ID")
    source_id: str = Field(..., description="Target Source ID")
    status: str = Field(..., description="'completed' or 'failed'")
    url: str = Field(..., description="Target scraped URL")
    canonical_url: Optional[str] = None
    title: Optional[str] = "Untitled Source"
    content: Optional[str] = ""
    language: Optional[str] = "en"
    content_hash: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
