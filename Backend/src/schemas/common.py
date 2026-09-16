"""
Common Pydantic schemas and generic response wrappers.
"""

from typing import Generic, Optional, TypeVar, Any, Dict
from pydantic import BaseModel, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[T] = None
    error: Optional[str] = None


class HealthStatus(BaseModel):
    status: str = "healthy"
    version: str
    environment: str
    vectorstore_status: str
    indexed_sources_count: int
    indexed_chunks_count: int
    active_primary_llm: str
    fallback_llms: list[str]
