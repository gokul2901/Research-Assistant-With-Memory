"""
===============================================================================
RESEARCH ASSISTANT WITH PERSISTENT MEMORY
Enterprise RAG Platform & Knowledge Management System
===============================================================================
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from src.config.settings import settings
from src.utils.logger import logger, setup_logging
from src.api.middleware.logging import RequestLoggingMiddleware
from src.api.middleware.error_handler import (
    validation_exception_handler,
    global_exception_handler,
)
from src.api.routes import (
    health_router,
    ingestion_router,
    webhook_router,
    sources_router,
    chat_router,
    export_router,
)
from src.rag.components.vector_store.chroma_client import ChromaManager
from src.rag.components.data_processor.embeddings import EmbeddingService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown hooks."""
    # Startup
    setup_logging()
    logger.info("================================================================")
    logger.info(f"Starting {settings.APP_NAME} (v{settings.APP_VERSION})")
    logger.info(f"Environment: {settings.APP_ENV} | Debug: {settings.DEBUG}")
    logger.info("Initializing ChromaDB Persistent Client...")
    
    # Ensure export directory exists
    os.makedirs(settings.PDF_EXPORT_DIR, exist_ok=True)
    
    # Pre-warm Chroma and Embedding engine
    chroma = ChromaManager.get_instance()
    emb_service = EmbeddingService()
    logger.info(f"Primary LLM: {settings.PRIMARY_MODEL} | Fallbacks: {settings.FALLBACK_MODEL_1}, {settings.FALLBACK_MODEL_2}")
    logger.info("================================================================")
    
    yield

    # Shutdown
    logger.info("Shutting down Research Assistant backend services.")


# =============================================================================
# FastAPI Application Factory
# =============================================================================

app = FastAPI(
    title="Research Assistant with Persistent Memory",
    description="""
# Research Assistant with Persistent Memory - Production Backend

An enterprise-grade **Retrieval-Augmented Generation (RAG)** and **Knowledge Management System** engineered with **Persistent Memory**, **Async Python**, **FastAPI**, **ChromaDB**, **LiteLLM**, **Pydantic**, and **n8n Automation Webhooks**.

### Key Architectural Capabilities:
- **Scalable URL Ingestion & Web Scraping**: Ingest single or batch URLs with automated boilerplate removal, heading preservation, and content hashing deduplication.
- **n8n Webhook Integration**: Trigger real-time knowledge base ingestion directly from n8n automation pipelines.
- **Hierarchical Chunking Pipeline**: Recursive character and token chunking preserving structural document hierarchy and source metadata.
- **ChromaDB Vector Database & Persistent Memory**: Persistent semantic storage with cosine similarity indexing, metadata filtering, and multi-session retention.
- **Vector Search & Semantic Retrieval**: Multi-stage dense retrieval with relevance thresholding and lexical keyword re-ranking.
- **LiteLLM Multi-Model Router**: Automated failover across **Gemini**, **GLM**, and **Mistral/Groq**.
- **Citation Engine & Source Attribution**: Grounded responses with inline citations (`[Source 1]`) and strict hallucination prevention (*"Not found in sources."*).
- **Multi-Session Memory & PDF Export**: Track multi-turn sessions across time and generate downloadable intelligence reports.
- **Enterprise Design**: Clean Repository Pattern, Service Layer Architecture, Structured Logging, and OpenAPI Specification.
    """,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# =============================================================================
# Middleware Configuration
# =============================================================================

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Logging & Process Timing
app.add_middleware(RequestLoggingMiddleware)

# Exception Handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# =============================================================================
# Route Registration
# =============================================================================

# Health Check (Root & V1)
app.include_router(health_router)
app.include_router(health_router, prefix=settings.API_V1_PREFIX)

# API V1 Endpoints
app.include_router(ingestion_router, prefix=settings.API_V1_PREFIX)
app.include_router(webhook_router, prefix=settings.API_V1_PREFIX)
app.include_router(sources_router, prefix=settings.API_V1_PREFIX)
app.include_router(chat_router, prefix=settings.API_V1_PREFIX)
app.include_router(export_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["Root"])
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "documentation": "/docs",
        "api_v1": settings.API_V1_PREFIX
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
