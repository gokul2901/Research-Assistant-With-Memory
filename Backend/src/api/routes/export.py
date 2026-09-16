"""
PDF Export Endpoints for Research Intelligence Reports.
"""

import os
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from src.schemas.common import APIResponse
from src.schemas.pdf import ExportPDFRequest, ExportPDFResponse
from src.services.chat_service import ChatService
from src.services.source_service import SourceService
from src.pdf.generator import PDFReportGenerator
from src.api.dependencies import get_chat_service, get_source_service, get_pdf_generator
from src.config.settings import settings

router = APIRouter(prefix="/export", tags=["PDF Export"])


@router.post("/pdf", response_model=APIResponse[ExportPDFResponse])
async def export_session_pdf(
    payload: ExportPDFRequest,
    chat_svc: ChatService = Depends(get_chat_service),
    source_svc: SourceService = Depends(get_source_service),
    pdf_gen: PDFReportGenerator = Depends(get_pdf_generator)
):
    """
    Generate and export a comprehensive research report PDF containing session Q&As,
    grounded citations, and referenced source metadata tables.
    """
    session = None
    if payload.session_id:
        session = chat_svc.get_session(payload.session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session with ID '{payload.session_id}' not found."
            )
    else:
        # If no session ID provided, pick the latest active session or create empty
        if chat_svc._sessions:
            latest_session_id = list(chat_svc._sessions.keys())[-1]
            session = chat_svc._sessions[latest_session_id]
        else:
            session = chat_svc.get_or_create_session("default_session")

    # Fetch referenced sources
    all_sources = source_svc.list_sources(limit=50)
    sources_data = [s.model_dump() for s in all_sources.sources]

    # Generate PDF
    filepath = pdf_gen.generate_research_report(
        session=session,
        sources=sources_data if payload.include_sources_summary else [],
        report_title=payload.report_title or "Research Assistant - Intelligence Report"
    )

    filename = os.path.basename(filepath)
    file_size = os.path.getsize(filepath)

    return APIResponse(
        success=True,
        message="PDF Report successfully generated",
        data=ExportPDFResponse(
            download_url=f"/api/v1/export/pdf/{filename}",
            file_name=filename,
            file_size_bytes=file_size,
            generated_at=datetime.utcnow().isoformat()
        )
    )


@router.get("/pdf/{file_name}")
async def download_pdf_file(file_name: str):
    """Directly stream and download the generated PDF report."""
    filepath = os.path.join(settings.PDF_EXPORT_DIR, file_name)
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"PDF file '{file_name}' not found."
        )

    return FileResponse(
        path=filepath,
        filename=file_name,
        media_type="application/pdf"
    )
