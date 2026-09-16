"""
Webhook Ingestion Endpoint for n8n Automation Pipelines.
"""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, Request, HTTPException, status
from src.schemas.common import APIResponse
from src.schemas.ingestion import IngestUrlRequest, IngestionSummaryResponse
from src.services.ingestion_service import IngestionService
from src.api.dependencies import get_ingestion_service
from src.utils.logger import logger

router = APIRouter(prefix="/webhook", tags=["n8n Automation Webhooks"])


@router.post("/n8n", response_model=APIResponse[IngestionSummaryResponse], status_code=status.HTTP_200_OK)
async def n8n_webhook_ingest(
    request: Request,
    service: IngestionService = Depends(get_ingestion_service)
):
    """
    Dedicated webhook endpoint designed to receive triggered payloads from n8n workflows.
    Accepts arbitrary JSON payloads containing 'url', 'urls', or an array of items from n8n.
    """
    try:
        body = await request.json()
    except Exception as e:
        raw_body = (await request.body()).decode("utf-8", errors="ignore").strip()
        if not raw_body:
            raise HTTPException(
                status_code=400,
                detail="Request body is empty. Please configure n8n to send JSON body: {'url': 'https://example.com'}"
            )
        try:
            import json
            body = json.loads(raw_body)
        except Exception:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid JSON payload syntax. Please ensure Header 'Content-Type: application/json' and valid JSON body. Error: {str(e)}"
            )

    logger.info(f"Received n8n webhook payload: {str(body)[:200]}...")

    urls: List[str] = []
    # Handle direct dict format
    if isinstance(body, dict):
        if "url" in body and isinstance(body["url"], str):
            urls.append(body["url"])
        if "urls" in body and isinstance(body["urls"], list):
            urls.extend([u for u in body["urls"] if isinstance(u, str)])
        # If n8n sent custom node properties like `json.link` or `json.url`
        if "link" in body and isinstance(body["link"], str):
            urls.append(body["link"])
    # Handle list of items format from n8n
    elif isinstance(body, list):
        for item in body:
            if isinstance(item, dict):
                if "url" in item and isinstance(item["url"], str):
                    urls.append(item["url"])
                elif "link" in item and isinstance(item["link"], str):
                    urls.append(item["link"])
            elif isinstance(item, str):
                urls.append(item)

    if not urls:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract any valid URLs from n8n payload."
        )

    summary = await service.ingest_batch_urls(urls=urls, force_refresh=False)

    return APIResponse(
        success=True,
        message=f"n8n webhook processed: {summary.successful_count} indexed, {summary.duplicate_count} unchanged, {summary.failed_count} failed.",
        data=summary
    )
