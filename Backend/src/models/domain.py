"""
Core domain models for the Research Assistant with Persistent Memory.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from src.utils.hashing import generate_uuid


class IngestionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"
    DUPLICATE = "duplicate"
    UPDATED = "updated"


@dataclass
class Source:
    source_id: str
    url: str
    title: str
    domain: str
    date_added: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    content_hash: str = ""
    status: IngestionStatus = IngestionStatus.PENDING
    chunk_count: int = 0
    character_count: int = 0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "url": self.url,
            "title": self.title,
            "domain": self.domain,
            "date_added": self.date_added.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "content_hash": self.content_hash,
            "status": self.status.value,
            "chunk_count": self.chunk_count,
            "character_count": self.character_count,
            "error_message": self.error_message or "",
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Source":
        date_added = datetime.fromisoformat(data["date_added"]) if isinstance(data.get("date_added"), str) else datetime.utcnow()
        last_updated = datetime.fromisoformat(data["last_updated"]) if isinstance(data.get("last_updated"), str) else datetime.utcnow()
        return cls(
            source_id=data["source_id"],
            url=data["url"],
            title=data.get("title", "Untitled Document"),
            domain=data.get("domain", ""),
            date_added=date_added,
            last_updated=last_updated,
            content_hash=data.get("content_hash", ""),
            status=IngestionStatus(data.get("status", IngestionStatus.INDEXED.value)),
            chunk_count=int(data.get("chunk_count", 0)),
            character_count=int(data.get("character_count", 0)),
            error_message=data.get("error_message") or None,
            metadata=data.get("metadata", {}),
        )


@dataclass
class Chunk:
    chunk_id: str
    source_id: str
    url: str
    chunk_index: int
    content: str
    token_count: int
    title: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "source_id": self.source_id,
            "url": self.url,
            "chunk_index": self.chunk_index,
            "token_count": self.token_count,
            "title": self.title,
        }


@dataclass
class CitationReference:
    citation_index: int
    source_id: str
    url: str
    title: str
    chunk_id: Optional[str] = None
    snippet: Optional[str] = None


@dataclass
class ChatMessage:
    message_id: str
    session_id: str
    role: str  # "user" or "assistant"
    content: str
    citations: List[CitationReference] = field(default_factory=list)
    sources: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    model_used: Optional[str] = None
    retrieved_chunk_count: int = 0


@dataclass
class ChatSession:
    session_id: str
    title: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    messages: List[ChatMessage] = field(default_factory=list)
