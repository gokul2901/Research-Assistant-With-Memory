"""
Health Check and System Diagnostics Endpoint.
"""

from fastapi import APIRouter, Depends
from src.config.settings import settings
from src.schemas.common import HealthStatus, APIResponse
from src.rag.components.vector_store.repository import VectorRepository
from src.api.dependencies import get_vector_repository

router = APIRouter(tags=["System Health"])


@router.get("/health", response_model=APIResponse[HealthStatus])
async def health_check(repo: VectorRepository = Depends(get_vector_repository)):
    """Check health of vector database, active LLM configurations, and statistics."""
    try:
        stats = repo.get_statistics()
        vectorstore_status = "connected"
        indexed_sources_count = stats["indexed_sources"]
        indexed_chunks_count = stats["total_chunks"]
    except Exception as e:
        vectorstore_status = f"unhealthy: {str(e)}"
        indexed_sources_count = 0
        indexed_chunks_count = 0

    status_data = HealthStatus(
        status="healthy" if vectorstore_status == "connected" else "degraded",
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
        vectorstore_status=vectorstore_status,
        indexed_sources_count=indexed_sources_count,
        indexed_chunks_count=indexed_chunks_count,
        active_primary_llm=settings.PRIMARY_MODEL,
        fallback_llms=[settings.FALLBACK_MODEL_1, settings.FALLBACK_MODEL_2]
    )

    return APIResponse(
        success=True,
        message="System is operational",
        data=status_data
    )
