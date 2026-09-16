"""
Pydantic schemas for PDF Report Generation.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ExportPDFRequest(BaseModel):
    session_id: Optional[str] = Field(None, description="Export conversation history from a specific session")
    question_ids: Optional[List[str]] = Field(None, description="Optional list of specific message IDs to include")
    report_title: Optional[str] = Field("Research Assistant - Intelligence Report", description="Title printed on the PDF header")
    include_sources_summary: bool = Field(True, description="Include summary table of all referenced sources")
    include_full_citations: bool = Field(True, description="Include detailed citation reference snippets")


class ExportPDFResponse(BaseModel):
    download_url: str
    file_name: str
    file_size_bytes: int
    generated_at: str
