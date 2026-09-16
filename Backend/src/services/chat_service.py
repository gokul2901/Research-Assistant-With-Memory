"""
Chat and Retrieval-Augmented Generation Service Layer.
Manages persistent conversation memory, delegates to the Supervisor Agent
for intelligent query routing and answer generation, and records session history.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
import time
from src.models.domain import ChatMessage, ChatSession, CitationReference
from src.agents.supervisor.graph import SupervisorAgent
from src.schemas.chat import (
    ChatRequest,
    ChatResponse,
    CitationItem,
    SourceMetadataRef,
    ChatMessageHistoryItem,
    ChatSessionHistoryResponse
)
from src.utils.hashing import generate_uuid
from src.config.settings import settings
from src.utils.logger import logger


class ChatService:
    def __init__(
        self,
        supervisor_agent: Optional[SupervisorAgent] = None,
    ):
        self.supervisor = supervisor_agent or SupervisorAgent()
        # In-memory persistent session store (can be wired to SQL/Redis if needed)
        self._sessions: Dict[str, ChatSession] = {}

    def get_or_create_session(self, session_id: Optional[str] = None) -> ChatSession:
        """Fetch existing session or create a new persistent session."""
        if not session_id:
            session_id = f"session_{generate_uuid()[:12]}"

        if session_id not in self._sessions:
            self._sessions[session_id] = ChatSession(
                session_id=session_id,
                title="Research Conversation",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                messages=[]
            )
        return self._sessions[session_id]

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Fetch session by ID."""
        return self._sessions.get(session_id)

    def get_session_history(self, session_id: str) -> Optional[ChatSessionHistoryResponse]:
        """Retrieve full formatted conversation history for a session."""
        session = self.get_session(session_id)
        if not session:
            return None

        history_items = []
        for msg in session.messages:
            cits = [
                CitationItem(
                    citation_index=c.citation_index,
                    source_id=c.source_id,
                    url=c.url,
                    title=c.title,
                    chunk_id=c.chunk_id,
                    snippet=c.snippet
                )
                for c in msg.citations
            ]
            srcs = [
                SourceMetadataRef(
                    source_id=s.get("source_id", ""),
                    url=s.get("url", ""),
                    title=s.get("title", ""),
                    domain=s.get("domain", ""),
                    chunk_count=s.get("chunk_count", 0)
                )
                for s in msg.sources
            ]
            history_items.append(ChatMessageHistoryItem(
                message_id=msg.message_id,
                role=msg.role,
                content=msg.content,
                timestamp=msg.timestamp,
                citations=cits,
                sources=srcs
            ))

        return ChatSessionHistoryResponse(
            session_id=session.session_id,
            total_messages=len(history_items),
            created_at=session.created_at,
            messages=history_items
        )

    async def answer_question(self, req: ChatRequest) -> ChatResponse:
        """
        End-to-end Query Pipeline via Supervisor Agent:
        1. Ensure Session persistence
        2. Invoke Supervisor Agent (intent classification → RAG or General)
        3. Record conversation messages to persistent session memory
        """
        start_time = time.perf_counter()
        session = self.get_or_create_session(req.session_id)

        # Use settings threshold — never hardcode
        threshold = req.similarity_threshold if req.similarity_threshold is not None else settings.DEFAULT_SIMILARITY_THRESHOLD
        top_k = req.top_k or settings.DEFAULT_TOP_K

        logger.info(
            f"[ChatService] 🔍 Query: '{req.question[:80]}' | "
            f"threshold={threshold} | top_k={top_k} | session={session.session_id}"
        )

        # Invoke the Supervisor Agent graph
        result = await self.supervisor.ainvoke({
            "question": req.question,
            "top_k": top_k,
            "similarity_threshold": threshold,
            "source_filters": req.source_filters,
            "model_override": req.model_override,
        })

        raw_answer = result.get("answer", "")
        citations = result.get("citations", [])
        referenced_sources = result.get("sources", [])
        model_used = result.get("model_used", "unknown")
        is_grounded = result.get("is_grounded", False)
        retrieved_chunks_count = result.get("retrieved_chunks_count", 0)
        exec_time_ms = result.get("execution_time_ms", round((time.perf_counter() - start_time) * 1000, 2))

        # Persist User Question to Session
        user_msg = ChatMessage(
            message_id=f"msg_{generate_uuid()[:12]}",
            session_id=session.session_id,
            role="user",
            content=req.question,
            timestamp=datetime.utcnow()
        )
        session.messages.append(user_msg)

        # Persist Assistant Answer to Session
        domain_citations = [
            CitationReference(
                citation_index=c.citation_index,
                source_id=c.source_id,
                url=c.url,
                title=c.title,
                chunk_id=c.chunk_id,
                snippet=c.snippet
            )
            for c in citations
        ]

        assistant_msg = ChatMessage(
            message_id=f"msg_{generate_uuid()[:12]}",
            session_id=session.session_id,
            role="assistant",
            content=raw_answer,
            citations=domain_citations,
            sources=[s.model_dump() for s in referenced_sources],
            timestamp=datetime.utcnow(),
            model_used=model_used,
            retrieved_chunk_count=retrieved_chunks_count
        )
        session.messages.append(assistant_msg)
        session.updated_at = datetime.utcnow()

        return ChatResponse(
            question=req.question,
            answer=raw_answer,
            citations=citations,
            sources=referenced_sources,
            session_id=session.session_id,
            model_used=model_used,
            retrieved_chunks_count=retrieved_chunks_count,
            is_grounded=is_grounded,
            execution_time_ms=exec_time_ms
        )
