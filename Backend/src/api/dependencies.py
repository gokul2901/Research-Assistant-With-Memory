"""
FastAPI Dependency Injection Providers.
"""

from functools import lru_cache
from src.rag.components.vector_store.chroma_client import ChromaManager
from src.rag.components.vector_store.repository import VectorRepository
from src.rag.components.data_processor.embeddings import EmbeddingService
from src.scraper.engine import WebScraperEngine
from src.rag.components.data_processor.chunking import RecursiveChunkingEngine
from src.services.source_service import SourceService
from src.services.ingestion_service import IngestionService
from src.services.chat_service import ChatService
from src.pdf.generator import PDFReportGenerator
from src.agents.llm.provider import MultiLLMRouter
from src.rag.components.citations.engine import CitationEngine
from src.rag.components.retrieval.search import SemanticRetriever
from src.rag.rag_pipeline import RAGPipeline
from src.agents.supervisor.graph import SupervisorAgent


@lru_cache()
def get_chroma_manager() -> ChromaManager:
    return ChromaManager.get_instance()


@lru_cache()
def get_vector_repository() -> VectorRepository:
    return VectorRepository(get_chroma_manager())


@lru_cache()
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()


@lru_cache()
def get_scraper_engine() -> WebScraperEngine:
    return WebScraperEngine()


@lru_cache()
def get_chunking_engine() -> RecursiveChunkingEngine:
    return RecursiveChunkingEngine()


@lru_cache()
def get_llm_router() -> MultiLLMRouter:
    return MultiLLMRouter()


@lru_cache()
def get_citation_engine() -> CitationEngine:
    return CitationEngine()


@lru_cache()
def get_semantic_retriever() -> SemanticRetriever:
    return SemanticRetriever(
        repository=get_vector_repository(),
        embedding_service=get_embedding_service()
    )


@lru_cache()
def get_rag_pipeline() -> RAGPipeline:
    return RAGPipeline(
        retriever=get_semantic_retriever(),
        citation_engine=get_citation_engine(),
    )


@lru_cache()
def get_supervisor_agent() -> SupervisorAgent:
    return SupervisorAgent(
        rag_pipeline=get_rag_pipeline(),
        llm_router=get_llm_router(),
    )


@lru_cache()
def get_source_service() -> SourceService:
    return SourceService(repository=get_vector_repository())


@lru_cache()
def get_ingestion_service() -> IngestionService:
    return IngestionService(
        chunker=get_chunking_engine(),
        embedding_service=get_embedding_service(),
        repository=get_vector_repository()
    )


@lru_cache()
def get_chat_service() -> ChatService:
    return ChatService(
        supervisor_agent=get_supervisor_agent(),
    )


@lru_cache()
def get_pdf_generator() -> PDFReportGenerator:
    return PDFReportGenerator()
