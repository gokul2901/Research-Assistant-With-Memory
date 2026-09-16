"""
Source Management REST API Endpoints.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from src.schemas.common import APIResponse
from src.schemas.sources import (
    SourceResponse,
    SourceListResponse,
    SourceStatisticsResponse,
    SourceRefreshResponse
)
from src.schemas.ingestion import (
    IngestUrlRequest,
    IngestionItemResult,
    BulkIngestionResponse,
)
from src.services.source_service import SourceService
from src.services.ingestion_service import IngestionService
from src.api.dependencies import get_source_service, get_ingestion_service

router = APIRouter(prefix="/sources", tags=["Sources"])


@router.get("/statistics", response_model=APIResponse[SourceStatisticsResponse])
async def get_source_statistics(service: SourceService = Depends(get_source_service)):
    """Retrieve aggregate knowledge base statistics (sources, chunks, domains)."""
    stats = service.get_statistics()
    return APIResponse(
        success=True,
        message="Knowledge base statistics retrieved",
        data=stats
    )


@router.get("", response_model=APIResponse[SourceListResponse])
async def list_sources(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    service: SourceService = Depends(get_source_service)
):
    """List all indexed sources in the persistent knowledge base."""
    source_list = service.list_sources(limit=limit, offset=offset)
    return APIResponse(
        success=True,
        message=f"Retrieved {len(source_list.sources)} sources",
        data=source_list
    )


@router.post("", response_model=APIResponse[IngestionItemResult], status_code=status.HTTP_201_CREATED)
async def create_source(
    payload: IngestUrlRequest,
    ingest_svc: IngestionService = Depends(get_ingestion_service)
):
    """Directly register and ingest a new source URL into the knowledge base."""
    urls = payload.get_urls()
    if not urls:
        raise HTTPException(status_code=400, detail="Must provide a valid 'url'")

    target_url = urls[0]
    result = await ingest_svc.ingest_single_url(target_url, force_refresh=payload.force_refresh)

    if result.status == "failed":
        raise HTTPException(status_code=400, detail=f"Failed to ingest source: {result.error_message}")

    return APIResponse(
        success=True,
        message="Source ingested and indexed successfully",
        data=result
    )


@router.post("/bulk", response_model=APIResponse[BulkIngestionResponse], status_code=status.HTTP_202_ACCEPTED)
async def create_sources_bulk(
    payload: IngestUrlRequest,
    ingest_svc: IngestionService = Depends(get_ingestion_service)
):
    """Submit multiple URLs asynchronously. Creates independent jobs for each URL."""
    urls = payload.get_urls()
    if not urls:
        raise HTTPException(status_code=400, detail="Must provide a list of valid URLs.")

    bulk_response = ingest_svc.submit_bulk_jobs(urls)

    return APIResponse(
        success=True,
        message=f"Submitted {bulk_response.total_submitted} ingestion job(s)",
        data=bulk_response
    )


@router.get("/{source_id}", response_model=APIResponse[SourceResponse])
async def get_source(
    source_id: str,
    service: SourceService = Depends(get_source_service)
):
    """Get metadata details of a specific indexed source."""
    source = service.get_source_by_id(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source with ID '{source_id}' not found."
        )
    return APIResponse(
        success=True,
        message="Source details retrieved",
        data=source
    )


@router.delete("/{source_id}", response_model=APIResponse[dict])
async def delete_source(
    source_id: str,
    service: SourceService = Depends(get_source_service)
):
    """Delete a source and purge its embeddings/chunks from the vector database."""
    source = service.get_source_by_id(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source with ID '{source_id}' not found."
        )

    deleted = service.delete_source(source_id)
    if not deleted:
        raise HTTPException(status_code=500, detail="Failed to delete source from database.")

    return APIResponse(
        success=True,
        message=f"Source '{source_id}' and all associated chunks permanently deleted",
        data={"source_id": source_id, "deleted": True}
    )


@router.post("/{source_id}/refresh", response_model=APIResponse[SourceRefreshResponse])
@router.put("/{source_id}/refresh", response_model=APIResponse[SourceRefreshResponse])
async def refresh_source(
    source_id: str,
    source_svc: SourceService = Depends(get_source_service),
    ingest_svc: IngestionService = Depends(get_ingestion_service)
):
    """Re-scrape an existing source URL, detect updates, and re-embed chunks."""
    source = source_svc.get_source_by_id(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source with ID '{source_id}' not found."
        )

    old_hash = source.content_hash
    result = await ingest_svc.ingest_single_url(source.url, force_refresh=True)

    status_msg = "Content was updated and re-indexed" if result.content_hash != old_hash else "Content unchanged; vectors refreshed"

    return APIResponse(
        success=result.status in ("indexed", "updated"),
        message=status_msg,
        data=SourceRefreshResponse(
            source_id=source_id,
            url=source.url,
            status=result.status,
            message=status_msg,
            old_hash=old_hash,
            new_hash=result.content_hash,
            chunk_count=result.chunk_count
        )
    )


@router.delete("", response_model=APIResponse[dict])
async def clear_all_sources(service: SourceService = Depends(get_source_service)):
    """Erases all sources and vector chunks from ChromaDB."""
    metrics = service.clear_all_sources()
    return APIResponse(
        success=True,
        message=f"Knowledge base reset completed: erased {metrics.get('deleted_sources', 0)} sources and {metrics.get('deleted_chunks', 0)} chunks.",
        data=metrics
    )

