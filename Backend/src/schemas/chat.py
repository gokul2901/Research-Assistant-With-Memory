"""
Pydantic schemas for Question Answering, Grounded Retrieval, and Chat API.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="The natural language question to ask across ingested sources")
    session_id: Optional[str] = Field(None, description="Optional session ID to persist multi-turn conversation memory")
    top_k: Optional[int] = Field(5, ge=1, le=30, description="Number of relevant chunks to retrieve")
    similarity_threshold: Optional[float] = Field(0.35, ge=0.0, le=1.0, description="Minimum cosine similarity score threshold")
    source_filters: Optional[List[str]] = Field(None, description="Optional list of source_ids to restrict search to")
    model_override: Optional[str] = Field(None, description="Optional specific model override (e.g., gemini/gemini-1.5-flash)")


class CitationItem(BaseModel):
    citation_index: int = Field(..., description="1-based index corresponding to [Source X] marker in the answer")
    source_id: str
    url: str
    title: str
    chunk_id: Optional[str] = None
    snippet: Optional[str] = None


class SourceMetadataRef(BaseModel):
    source_id: str
    url: str
    title: str
    domain: str
    chunk_count: int


class ChatResponse(BaseModel):
    question: str
    answer: str
    citations: List[CitationItem]
    sources: List[SourceMetadataRef]
    session_id: str
    model_used: str
    retrieved_chunks_count: int
    is_grounded: bool
    execution_time_ms: float


class ChatMessageHistoryItem(BaseModel):
    message_id: str
    role: str
    content: str
    timestamp: datetime
    citations: List[CitationItem] = []
    sources: List[SourceMetadataRef] = []


class ChatSessionHistoryResponse(BaseModel):
    session_id: str
    total_messages: int
    created_at: datetime
    messages: List[ChatMessageHistoryItem]
