"""
URL Ingestion, Job Tracking, and n8n Callback Endpoints.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header, status
from src.schemas.common import APIResponse
from src.schemas.ingestion import (
    IngestUrlRequest,
    IngestionSummaryResponse,
    IngestionJobResponse,
    BulkIngestionResponse,
    IngestionCallbackPayload,
    IngestionItemResult,
)
from src.services.ingestion_service import IngestionService
from src.rag.components.data_processor.ingestion import job_manager
from src.integrations.n8n import n8n_client
from src.api.dependencies import get_ingestion_service
from src.utils.logger import logger

router = APIRouter(prefix="", tags=["Ingestion & Automation"])


@router.post("/ingest", response_model=APIResponse[IngestionSummaryResponse], status_code=status.HTTP_200_OK)
async def ingest_urls(
    payload: IngestUrlRequest,
    service: IngestionService = Depends(get_ingestion_service)
):
    """
    Ingest single or batch URLs synchronously into the persistent knowledge base.
    """
    urls_to_process = payload.get_urls()
    if not urls_to_process:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid URLs provided in request body."
        )

    summary = await service.ingest_batch_urls(
        urls=urls_to_process,
        force_refresh=payload.force_refresh
    )

    return APIResponse(
        success=summary.successful_count > 0 or summary.duplicate_count > 0,
        message=f"Ingestion complete: {summary.successful_count} indexed, {summary.duplicate_count} cached/duplicate, {summary.failed_count} failed.",
        data=summary
    )


@router.get("/ingestion/jobs/{job_id}", response_model=APIResponse[IngestionJobResponse])
async def get_ingestion_job(job_id: str):
    """Get the current execution status and metrics for an ingestion job."""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ingestion job '{job_id}' not found."
        )

    return APIResponse(
        success=True,
        message="Job details retrieved",
        data=IngestionJobResponse(
            job_id=job.job_id,
            source_id=job.source_id,
            url=job.url,
            canonical_url=job.canonical_url,
            status=job.status,
            created_at=job.created_at,
            started_at=job.started_at,
            completed_at=job.completed_at,
            error=job.error,
            word_count=job.word_count,
            chunk_count=job.chunk_count
        )
    )


@router.post("/ingestion/callback", response_model=APIResponse[IngestionItemResult])
async def n8n_ingestion_callback(
    payload: IngestionCallbackPayload,
    x_n8n_callback_secret: Optional[str] = Header(None),
    service: IngestionService = Depends(get_ingestion_service)
):
    """
    Callback endpoint called by n8n after completing webpage scraping.
    Validates X-N8N-Callback-Secret header before chunking and embedding.
    """
    # Security: Validate Callback Secret
    if not n8n_client.verify_callback_secret(x_n8n_callback_secret):
        logger.warning(f"Unauthorized n8n callback attempt for job '{payload.job_id}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-N8N-Callback-Secret header."
        )

    logger.info(f"Processing n8n callback for job '{payload.job_id}' (URL: {payload.url})")
    result = await service.process_callback(payload)

    return APIResponse(
        success=result.status in ("indexed", "updated"),
        message=f"Callback processed: source {result.status}",
        data=result
    )
