"""
Semantic Search & Context Retrieval Pipeline.
"""

from typing import List, Dict, Any, Optional
from src.rag.components.data_processor.embeddings import EmbeddingService
from src.rag.components.vector_store.repository import VectorRepository
from src.rag.components.retrieval.reranker import RelevanceReranker
from src.config.settings import settings
from src.utils.logger import logger


class ContextChunk:
    def __init__(
        self,
        chunk_id: str,
        source_id: str,
        url: str,
        title: str,
        content: str,
        similarity_score: float,
        rerank_score: float,
        chunk_index: int
    ):
        self.chunk_id = chunk_id
        self.source_id = source_id
        self.url = url
        self.title = title
        self.content = content
        self.similarity_score = similarity_score
        self.rerank_score = rerank_score
        self.chunk_index = chunk_index


class ContextPackage:
    def __init__(
        self,
        query: str,
        chunks: List[ContextChunk],
        formatted_prompt_context: str,
        sources_map: Dict[int, Dict[str, Any]]
    ):
        self.query = query
        self.chunks = chunks
        self.formatted_prompt_context = formatted_prompt_context
        self.sources_map = sources_map  # Maps index 1..N to source details


class SemanticRetriever:
    def __init__(
        self,
        repository: Optional[VectorRepository] = None,
        embedding_service: Optional[EmbeddingService] = None,
        reranker: Optional[RelevanceReranker] = None
    ):
        self.repository = repository or VectorRepository()
        self.embedding_service = embedding_service or EmbeddingService()
        self.reranker = reranker or RelevanceReranker()

    def retrieve(
        self,
        query: str,
        top_k: int = settings.DEFAULT_TOP_K,
        similarity_threshold: float = settings.DEFAULT_SIMILARITY_THRESHOLD,
        source_filters: Optional[List[str]] = None
    ) -> ContextPackage:
        """
        Execute full retrieval pipeline:
        1. Embed user question
        2. Vector search in ChromaDB (retrieve 2x top_k for candidate pool)
        3. Re-rank, filter, and select top_k items
        4. Assemble structured Context Package with labeled source markers
        """
        logger.info(
            f"[Retriever] 🔍 Query: '{query[:80]}' | threshold={similarity_threshold} | top_k={top_k}"
        )

        # 1. Embed query
        query_embedding = self.embedding_service.embed_query(query)
        logger.debug(f"[Retriever] Query embedding generated: dim={len(query_embedding)}")

        # 2. Vector search candidate pool (2 * top_k)
        candidate_count = min(top_k * 2, settings.MAX_TOP_K)
        raw_candidates = self.repository.query_similarity(
            query_embedding=query_embedding,
            top_k=candidate_count,
            source_filters=source_filters
        )

        logger.info(
            f"[Retriever] 📊 ChromaDB returned {len(raw_candidates)} raw candidates. "
            f"Scores: {[round(c.get('similarity_score', 0), 3) for c in raw_candidates]}"
        )

        if not raw_candidates:
            logger.warning("[Retriever] ⚠️ ChromaDB returned 0 results — knowledge base may be empty or query embedding failed!")

        # 3. Re-rank and filter
        ranked_candidates = self.reranker.rerank(
            query=query,
            retrieved_items=raw_candidates,
            similarity_threshold=similarity_threshold,
            max_results=top_k
        )

        logger.info(
            f"[Retriever] ✅ After re-ranking: {len(ranked_candidates)} chunks passed threshold={similarity_threshold}. "
            f"Rerank scores: {[round(c.get('rerank_score', 0), 3) for c in ranked_candidates]}"
        )

        if not ranked_candidates:
            logger.warning(
                f"[Retriever] ❌ All candidates filtered out by threshold={similarity_threshold}. "
                f"Raw candidate scores were: {[round(c.get('similarity_score', 0), 3) for c in raw_candidates]}. "
                f"Consider lowering DEFAULT_SIMILARITY_THRESHOLD in .env"
            )

        # 4. Format context chunks
        context_chunks: List[ContextChunk] = []
        sources_map: Dict[int, Dict[str, Any]] = {}
        source_id_to_marker: Dict[str, int] = {}
        formatted_context_parts: List[str] = []

        marker_counter = 1

        for item in ranked_candidates:
            meta = item.get("metadata", {})
            source_id = meta.get("source_id", "")
            url = meta.get("url", "")
            title = meta.get("title", "Untitled Source")
            content = item.get("content", "")

            # Group citations by unique URL / source_id
            if source_id not in source_id_to_marker:
                source_id_to_marker[source_id] = marker_counter
                sources_map[marker_counter] = {
                    "marker": marker_counter,
                    "source_id": source_id,
                    "url": url,
                    "title": title,
                    "domain": meta.get("domain", ""),
                    "chunks": []
                }
                marker_counter += 1

            assigned_marker = source_id_to_marker[source_id]
            sources_map[assigned_marker]["chunks"].append(item.get("chunk_id"))

            ctx_chunk = ContextChunk(
                chunk_id=item.get("chunk_id", ""),
                source_id=source_id,
                url=url,
                title=title,
                content=content,
                similarity_score=item.get("similarity_score", 0.0),
                rerank_score=item.get("rerank_score", 0.0),
                chunk_index=meta.get("chunk_index", 0)
            )
            context_chunks.append(ctx_chunk)

            # Format for LLM prompt: [Source X] (Title - URL): Content
            formatted_context_parts.append(
                f"[Source {assigned_marker}] (Title: {title} | URL: {url})\n{content}\n"
            )

        formatted_prompt_context = "\n---\n".join(formatted_context_parts)

        if formatted_prompt_context:
            logger.info(
                f"[Retriever] 📝 Context built: {len(context_chunks)} chunks across "
                f"{len(sources_map)} sources. Preview: '{formatted_prompt_context[:200]}...'"
            )

        return ContextPackage(
            query=query,
            chunks=context_chunks,
            formatted_prompt_context=formatted_prompt_context,
            sources_map=sources_map
        )
