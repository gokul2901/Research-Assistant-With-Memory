"""
Source Management Service Layer.
Handles Source CRUD, re-indexing/refresh, and knowledge statistics.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from src.models.domain import Source, IngestionStatus
from src.rag.components.vector_store.repository import VectorRepository
from src.schemas.sources import (
    SourceResponse,
    SourceListResponse,
    SourceStatisticsResponse,
    SourceRefreshResponse,
    DomainStat
)
from src.utils.logger import logger


class SourceService:
    def __init__(self, repository: Optional[VectorRepository] = None):
        self.repository = repository or VectorRepository()

    def get_source_by_id(self, source_id: str) -> Optional[SourceResponse]:
        """Fetch source by ID and convert to schema."""
        source = self.repository.get_source(source_id)
        if not source:
            return None
        return SourceResponse(
            source_id=source.source_id,
            url=source.url,
            title=source.title,
            domain=source.domain,
            date_added=source.date_added,
            last_updated=source.last_updated,
            content_hash=source.content_hash,
            status=source.status.value,
            chunk_count=source.chunk_count,
            character_count=source.character_count,
            error_message=source.error_message,
        )

    def list_sources(self, limit: int = 100, offset: int = 0) -> SourceListResponse:
        """List all indexed sources."""
        sources = self.repository.list_sources(limit=limit, offset=offset)
        source_responses = [
            SourceResponse(
                source_id=s.source_id,
                url=s.url,
                title=s.title,
                domain=s.domain,
                date_added=s.date_added,
                last_updated=s.last_updated,
                content_hash=s.content_hash,
                status=s.status.value,
                chunk_count=s.chunk_count,
                character_count=s.character_count,
                error_message=s.error_message,
            )
            for s in sources
        ]
        return SourceListResponse(
            total_sources=len(source_responses),
            sources=source_responses
        )

    def delete_source(self, source_id: str) -> bool:
        """Delete source metadata and associated chunks."""
        return self.repository.delete_source(source_id)

    def get_statistics(self) -> SourceStatisticsResponse:
        """Compute aggregated knowledge base statistics."""
        raw_stats = self.repository.get_statistics()
        domain_breakdown = [
            DomainStat(
                domain=d["domain"],
                source_count=d["source_count"],
                chunk_count=d["chunk_count"]
            )
            for d in raw_stats["domain_breakdown"]
        ]
        return SourceStatisticsResponse(
            total_sources=raw_stats["total_sources"],
            total_chunks=raw_stats["total_chunks"],
            total_characters=raw_stats["total_characters"],
            indexed_sources=raw_stats["indexed_sources"],
            failed_sources=raw_stats["failed_sources"],
            domain_breakdown=domain_breakdown
        )

    def clear_all_sources(self) -> Dict[str, int]:
        """Erase all sources and vector chunks from ChromaDB."""
        return self.repository.clear_all()
