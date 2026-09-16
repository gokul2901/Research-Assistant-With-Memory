"""
Pydantic schemas for Source Management endpoints.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SourceResponse(BaseModel):
    source_id: str
    url: str
    title: str
    domain: str
    date_added: datetime
    last_updated: datetime
    content_hash: str
    status: str
    chunk_count: int
    character_count: int
    error_message: Optional[str] = None


class SourceListResponse(BaseModel):
    total_sources: int
    sources: List[SourceResponse]


class DomainStat(BaseModel):
    domain: str
    source_count: int
    chunk_count: int


class SourceStatisticsResponse(BaseModel):
    total_sources: int
    total_chunks: int
    total_characters: int
    indexed_sources: int
    failed_sources: int
    domain_breakdown: List[DomainStat]


class SourceRefreshResponse(BaseModel):
    source_id: str
    url: str
    status: str
    message: str
    old_hash: str
    new_hash: str
    chunk_count: int
