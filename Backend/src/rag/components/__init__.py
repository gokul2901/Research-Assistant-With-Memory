"""
RAG Components — modular building blocks for the retrieval-augmented generation pipeline.

Components:
- retrieval: Semantic search and re-ranking
- vector_store: ChromaDB persistent vector storage
- data_processor: Chunking, embedding generation, and ingestion job tracking
- citations: Citation attribution and source grounding
"""

from src.rag.components.retrieval.search import SemanticRetriever, ContextPackage, ContextChunk
from src.rag.components.retrieval.reranker import RelevanceReranker
from src.rag.components.vector_store.chroma_client import ChromaManager
from src.rag.components.vector_store.repository import VectorRepository
from src.rag.components.data_processor.chunking import RecursiveChunkingEngine
from src.rag.components.data_processor.embeddings import EmbeddingService
from src.rag.components.data_processor.ingestion import IngestionJobManager, job_manager
from src.rag.components.citations.engine import CitationEngine

__all__ = [
    "SemanticRetriever", "ContextPackage", "ContextChunk",
    "RelevanceReranker",
    "ChromaManager", "VectorRepository",
    "RecursiveChunkingEngine",
    "EmbeddingService",
    "IngestionJobManager", "job_manager",
    "CitationEngine",
]
