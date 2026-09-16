"""
Production Ingestion Service Layer.
Orchestrates URL security validation, multi-level duplicate detection,
n8n webhook dispatching, fallback web scraping, recursive chunking,
batch embedding, and persistent ChromaDB vector indexing.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
import asyncio
from src.models.domain import Source, Chunk, IngestionStatus
from src.models.ingestion_job import IngestionJob
from src.rag.components.data_processor.ingestion import job_manager, IngestionJobManager
from src.integrations.n8n import n8n_client, N8NIntegrationClient
from src.scraper.url_utils import normalize_url, validate_url, extract_domain
from src.scraper.fetcher import WebpageFetcher
from src.scraper.extractor import ContentExtractor, ExtractedDocument
from src.rag.components.data_processor.chunking import RecursiveChunkingEngine
from src.rag.components.data_processor.embeddings import EmbeddingService
from src.rag.components.vector_store.repository import VectorRepository
from src.utils.hashing import generate_url_hash, generate_content_hash
from src.schemas.ingestion import (
    IngestionItemResult,
    IngestionSummaryResponse,
    IngestionJobResponse,
    BulkIngestionResponse,
    IngestionCallbackPayload,
)
from src.config.settings import settings
from src.utils.logger import logger


class IngestionService:
    def __init__(
        self,
        fetcher: Optional[WebpageFetcher] = None,
        extractor: Optional[ContentExtractor] = None,
        chunker: Optional[RecursiveChunkingEngine] = None,
        embedding_service: Optional[EmbeddingService] = None,
        repository: Optional[VectorRepository] = None,
        jobs: Optional[IngestionJobManager] = None,
        n8n: Optional[N8NIntegrationClient] = None,
        max_concurrent: int = settings.MAX_CONCURRENT_SCRAPES
    ):
        self.fetcher = fetcher or WebpageFetcher()
        self.extractor = extractor or ContentExtractor()
        self.chunker = chunker or RecursiveChunkingEngine()
        self.embedding_service = embedding_service or EmbeddingService()
        self.repository = repository or VectorRepository()
        self.job_manager = jobs or job_manager
        self.n8n = n8n or n8n_client
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def ingest_single_url(
        self,
        raw_url: str,
        force_refresh: bool = False,
        job_id: Optional[str] = None
    ) -> IngestionItemResult:
        """
        Execute full RAG URL ingestion pipeline:
        1. URL Normalization & SSRF Validation
        2. Ingestion Job Registration (QUEUED -> FETCHING -> EXTRACTING -> CHUNKING -> EMBEDDING -> INDEXING)
        3. Level 1 & Level 2 Duplicate Check
        4. Web Scraping & Content Extraction (or n8n dispatch)
        5. Level 3 Content Hash Duplicate Check
        6. Recursive Chunking preserving document hierarchy
        7. Batch Embedding Generation
        8. Additive ChromaDB Persistent Vector Indexing
        """
        async with self.semaphore:
            # 1. Validation & Normalization
            is_valid, val_err = validate_url(raw_url)
            if not is_valid:
                logger.warning(f"Invalid URL rejected: {raw_url} - Reason: {val_err}")
                dummy_source_id = f"src_{generate_url_hash(raw_url)[:16]}"
                if job_id:
                    self.job_manager.update_job(job_id, status="FAILED", error=val_err)

                return IngestionItemResult(
                    source_id=dummy_source_id,
                    url=raw_url,
                    title="Invalid URL",
                    domain=extract_domain(raw_url),
                    status=IngestionStatus.FAILED.value,
                    chunk_count=0,
                    character_count=0,
                    content_hash="",
                    date_added=datetime.utcnow(),
                    error_message=val_err
                )

            url = normalize_url(raw_url)
            domain = extract_domain(url)
            source_id = f"src_{generate_url_hash(url)[:16]}"

            # Create or update job
            if not job_id:
                job = self.job_manager.create_job(url=url, source_id=source_id)
                job_id = job.job_id

            self.job_manager.update_job(job_id, status="FETCHING")
            logger.info(f"Ingestion started for '{url}' (Source ID: {source_id}, Job ID: {job_id})")

            # 2. Check Level 1 Duplicate in database
            existing_source = self.repository.get_source(source_id)

            # 3. Fetch Webpage HTML
            html_content, fetch_err = await self.fetcher.fetch(url)
            if fetch_err or not html_content:
                error_msg = fetch_err or "Failed to download HTML content"
                logger.error(f"Fetch failed for {url}: {error_msg}")
                self.job_manager.update_job(job_id, status="FAILED", error=error_msg)

                # Persist failed source metadata
                failed_source = Source(
                    source_id=source_id,
                    url=url,
                    title=f"Failed Source ({domain})",
                    domain=domain,
                    status=IngestionStatus.FAILED,
                    error_message=error_msg,
                    last_updated=datetime.utcnow()
                )
                self.repository.upsert_source(failed_source)

                return IngestionItemResult(
                    source_id=source_id,
                    url=url,
                    title=failed_source.title,
                    domain=domain,
                    status=IngestionStatus.FAILED.value,
                    chunk_count=0,
                    character_count=0,
                    content_hash="",
                    date_added=failed_source.date_added,
                    error_message=error_msg
                )

            # 4. Extract and Clean Content
            self.job_manager.update_job(job_id, status="EXTRACTING")
            doc: ExtractedDocument = self.extractor.extract(html_content, url)

            if doc.status == "FAILED_EXTRACTION" or not doc.clean_text:
                error_msg = doc.error or "Failed to extract readable content"
                logger.error(f"Extraction failed for {url}: {error_msg}")
                self.job_manager.update_job(job_id, status="FAILED", error=error_msg)

                return IngestionItemResult(
                    source_id=source_id,
                    url=url,
                    title=doc.title or domain,
                    domain=domain,
                    status=IngestionStatus.FAILED.value,
                    chunk_count=0,
                    character_count=0,
                    content_hash="",
                    date_added=datetime.utcnow(),
                    error_message=error_msg
                )

            # 5. Level 3 Content Hash Duplicate Detection
            content_hash = doc.content_hash or generate_content_hash(doc.clean_text)

            if existing_source and existing_source.content_hash == content_hash and not force_refresh:
                logger.info(f"Source '{url}' unchanged (SHA-256 match). Marking as duplicate/cached.")
                self.job_manager.update_job(
                    job_id,
                    status="DUPLICATE",
                    canonical_url=doc.canonical_url,
                    word_count=doc.word_count,
                    chunk_count=existing_source.chunk_count
                )
                return IngestionItemResult(
                    source_id=source_id,
                    url=url,
                    title=existing_source.title,
                    domain=domain,
                    status=IngestionStatus.DUPLICATE.value,
                    chunk_count=existing_source.chunk_count,
                    character_count=existing_source.character_count,
                    content_hash=content_hash,
                    date_added=existing_source.date_added,
                    error_message=None
                )

            # 6. Create or Update Source Record
            is_update = existing_source is not None
            source = Source(
                source_id=source_id,
                url=url,
                title=doc.title,
                domain=domain,
                date_added=existing_source.date_added if existing_source else datetime.utcnow(),
                last_updated=datetime.utcnow(),
                content_hash=content_hash,
                status=IngestionStatus.PROCESSING,
                character_count=doc.character_count,
                metadata=doc.metadata
            )

            # 7. Chunking
            self.job_manager.update_job(job_id, status="CHUNKING")
            chunks = self.chunker.chunk_source(source, doc.clean_text)
            source.chunk_count = len(chunks)

            # 8. Embedding Generation
            self.job_manager.update_job(job_id, status="EMBEDDING")
            chunk_texts = [c.content for c in chunks]
            chunk_embeddings = self.embedding_service.embed_texts(chunk_texts)

            # 9. Persistent Storage in ChromaDB (Additive)
            self.job_manager.update_job(job_id, status="INDEXING")
            if is_update:
                self.repository.delete_chunks_by_source_id(source_id)

            self.repository.upsert_chunks(chunks, chunk_embeddings)

            # 10. Update Source status
            source.status = IngestionStatus.UPDATED if is_update else IngestionStatus.INDEXED
            self.repository.upsert_source(source)

            self.job_manager.update_job(
                job_id,
                status="COMPLETED",
                canonical_url=doc.canonical_url,
                word_count=doc.word_count,
                chunk_count=len(chunks)
            )

            logger.info(
                f"Successfully indexed source '{source.title}' ({url}) with {len(chunks)} chunks, {doc.character_count} chars."
            )

            return IngestionItemResult(
                source_id=source.source_id,
                url=source.url,
                title=source.title,
                domain=source.domain,
                status=source.status.value,
                chunk_count=source.chunk_count,
                character_count=source.character_count,
                content_hash=source.content_hash,
                date_added=source.date_added,
                error_message=None
            )

    async def ingest_batch_urls(
        self,
        urls: List[str],
        force_refresh: bool = False
    ) -> IngestionSummaryResponse:
        """Ingest multiple URLs concurrently with error isolation."""
        tasks = [self.ingest_single_url(u, force_refresh=force_refresh) for u in urls]
        results: List[IngestionItemResult] = await asyncio.gather(*tasks, return_exceptions=False)

        successful_count = sum(1 for r in results if r.status in (IngestionStatus.INDEXED.value, IngestionStatus.UPDATED.value))
        failed_count = sum(1 for r in results if r.status == IngestionStatus.FAILED.value)
        duplicate_count = sum(1 for r in results if r.status == IngestionStatus.DUPLICATE.value)

        return IngestionSummaryResponse(
            total_requested=len(urls),
            successful_count=successful_count,
            failed_count=failed_count,
            duplicate_count=duplicate_count,
            results=results
        )

    def submit_bulk_jobs(self, urls: List[str]) -> BulkIngestionResponse:
        """Submit independent asynchronous ingestion jobs for a batch of URLs."""
        job_responses: List[IngestionJobResponse] = []

        for raw_url in urls:
            url = normalize_url(raw_url)
            source_id = f"src_{generate_url_hash(url)[:16]}"
            job = self.job_manager.create_job(url=url, source_id=source_id)

            # Fire and forget async ingestion task
            asyncio.create_task(self.ingest_single_url(url, job_id=job.job_id))

            job_responses.append(IngestionJobResponse(
                job_id=job.job_id,
                source_id=job.source_id,
                url=job.url,
                canonical_url=job.canonical_url,
                status=job.status,
                created_at=job.created_at,
                started_at=job.started_at,
                completed_at=job.completed_at,
                error=job.error,
                word_count=job.word_count,
                chunk_count=job.chunk_count
            ))

        return BulkIngestionResponse(
            total_submitted=len(job_responses),
            jobs=job_responses
        )

    async def process_callback(self, payload: IngestionCallbackPayload) -> IngestionItemResult:
        """
        Process scraped content returned from n8n webhook callback.
        FastAPI validates, chunks, generates embeddings, and indexes in ChromaDB.
        """
        job = self.job_manager.get_job(payload.job_id)
        if not job:
            job = self.job_manager.create_job(url=payload.url, source_id=payload.source_id)

        if payload.status == "failed" or not payload.content:
            error_msg = payload.error or "n8n reported scraping failure"
            self.job_manager.update_job(payload.job_id, status="FAILED", error=error_msg)
            return IngestionItemResult(
                source_id=payload.source_id,
                url=payload.url,
                title=payload.title or "Scraping Failed",
                domain=extract_domain(payload.url),
                status=IngestionStatus.FAILED.value,
                chunk_count=0,
                character_count=0,
                content_hash="",
                date_added=datetime.utcnow(),
                error_message=error_msg
            )

        clean_text = payload.content.strip()
        content_hash = payload.content_hash or generate_content_hash(clean_text)
        domain = extract_domain(payload.url)

        # Check existing source for update
        existing_source = self.repository.get_source(payload.source_id)
        is_update = existing_source is not None

        source = Source(
            source_id=payload.source_id,
            url=payload.url,
            title=payload.title or f"Document from {domain}",
            domain=domain,
            date_added=existing_source.date_added if existing_source else datetime.utcnow(),
            last_updated=datetime.utcnow(),
            content_hash=content_hash,
            status=IngestionStatus.PROCESSING,
            character_count=len(clean_text),
            metadata=payload.metadata or {}
        )

        # Chunking
        self.job_manager.update_job(payload.job_id, status="CHUNKING")
        chunks = self.chunker.chunk_source(source, clean_text)
        source.chunk_count = len(chunks)

        # Embeddings
        self.job_manager.update_job(payload.job_id, status="EMBEDDING")
        chunk_texts = [c.content for c in chunks]
        chunk_embeddings = self.embedding_service.embed_texts(chunk_texts)

        # Indexing into ChromaDB
        self.job_manager.update_job(payload.job_id, status="INDEXING")
        if is_update:
            self.repository.delete_chunks_by_source_id(payload.source_id)

        self.repository.upsert_chunks(chunks, chunk_embeddings)
        source.status = IngestionStatus.UPDATED if is_update else IngestionStatus.INDEXED
        self.repository.upsert_source(source)

        self.job_manager.update_job(
            payload.job_id,
            status="COMPLETED",
            canonical_url=payload.canonical_url,
            word_count=len(clean_text.split()),
            chunk_count=len(chunks)
        )

        return IngestionItemResult(
            source_id=source.source_id,
            url=source.url,
            title=source.title,
            domain=source.domain,
            status=source.status.value,
            chunk_count=source.chunk_count,
            character_count=source.character_count,
            content_hash=source.content_hash,
            date_added=source.date_added,
            error_message=None
        )
