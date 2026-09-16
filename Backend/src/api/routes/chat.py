"""
Grounded Question Answering and Chat REST Endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from src.schemas.common import APIResponse
from src.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatSessionHistoryResponse
)
from src.services.chat_service import ChatService
from src.api.dependencies import get_chat_service

router = APIRouter(prefix="/chat", tags=["Research Assistant Chat"])


@router.post("", response_model=APIResponse[ChatResponse], status_code=status.HTTP_200_OK)
async def ask_question(
    payload: ChatRequest,
    service: ChatService = Depends(get_chat_service)
):
    """
    Query the persistent knowledge base across all ingested sources.
    Performs semantic retrieval, multi-LLM routing, grounding checks, and citation attribution.
    """
    response = await service.answer_question(payload)
    return APIResponse(
        success=True,
        message="Answer generated with grounded citations",
        data=response
    )


@router.get("/history/{session_id}", response_model=APIResponse[ChatSessionHistoryResponse])
async def get_session_history(
    session_id: str,
    service: ChatService = Depends(get_chat_service)
):
    """Retrieve full conversation history and grounded citations for a research session."""
    history = service.get_session_history(session_id)
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID '{session_id}' not found."
        )
    return APIResponse(
        success=True,
        message="Session history retrieved",
        data=history
    )
