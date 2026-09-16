"""
Repository Layer for ChromaDB Vector Storage and Source Metadata Persistence.
"""

from typing import List, Optional, Dict, Any, Tuple
from collections import defaultdict
from src.models.domain import Source, Chunk, IngestionStatus
from src.rag.components.vector_store.chroma_client import ChromaManager
from src.utils.logger import logger


class VectorRepository:
    def __init__(self, chroma_manager: Optional[ChromaManager] = None):
        self.chroma = chroma_manager or ChromaManager.get_instance()
        self.sources_col = self.chroma.sources_collection
        self.chunks_col = self.chroma.chunks_collection

    # =========================================================================
    # Source Metadata CRUD
    # =========================================================================

    def upsert_source(self, source: Source) -> None:
        """Persist or update source record in sources_collection."""
        meta = source.to_dict()
        # Chroma requires document or non-empty string
        doc_str = f"Source: {source.title}\nURL: {source.url}\nDomain: {source.domain}"
        
        self.sources_col.upsert(
            ids=[source.source_id],
            documents=[doc_str],
            metadatas=[meta]
        )
        logger.debug(f"Upserted source metadata: {source.source_id} ({source.url})")

    def get_source(self, source_id: str) -> Optional[Source]:
        """Fetch a source by its unique ID."""
        try:
            res = self.sources_col.get(ids=[source_id])
            if res and res["ids"] and len(res["ids"]) > 0:
                meta = res["metadatas"][0]
                return Source.from_dict(meta)
        except Exception as e:
            logger.error(f"Error fetching source {source_id}: {e}")
        return None

    def get_source_by_url(self, url: str) -> Optional[Source]:
        """Find an existing source matching the canonical URL."""
        try:
            res = self.sources_col.get(where={"url": url})
            if res and res["ids"] and len(res["ids"]) > 0:
                meta = res["metadatas"][0]
                return Source.from_dict(meta)
        except Exception as e:
            logger.debug(f"Error querying source by URL {url}: {e}")
        return None

    def list_sources(self, limit: int = 100, offset: int = 0) -> List[Source]:
        """List all indexed sources."""
        try:
            res = self.sources_col.get(limit=limit, offset=offset)
            if not res or not res["ids"]:
                return []
            sources = []
            for meta in res["metadatas"]:
                sources.append(Source.from_dict(meta))
            return sorted(sources, key=lambda s: s.date_added, reverse=True)
        except Exception as e:
            logger.error(f"Error listing sources: {e}")
            return []

    def delete_source(self, source_id: str) -> bool:
        """Delete source metadata and all its associated vector chunks."""
        try:
            # 1. Delete associated chunks
            self.delete_chunks_by_source_id(source_id)
            # 2. Delete source record
            self.sources_col.delete(ids=[source_id])
            logger.info(f"Deleted source {source_id} and its associated vector chunks")
            return True
        except Exception as e:
            logger.error(f"Error deleting source {source_id}: {e}")
            return False

    # =========================================================================
    # Chunk Vector Operations
    # =========================================================================

    def upsert_chunks(self, chunks: List[Chunk], embeddings: List[List[float]]) -> None:
        """Persist chunk vectors, document text, and rich metadata."""
        if not chunks:
            logger.warning("[Repository] upsert_chunks called with empty chunk list — nothing stored!")
            return

        ids = [c.chunk_id for c in chunks]
        docs = [c.content for c in chunks]
        metadatas = [
            {
                "source_id": c.source_id,
                "url": c.url,
                "title": c.title,
                # BUG FIX: domain was missing — retrieval always got empty string for domain
                "domain": getattr(c, "domain", ""),
                "chunk_index": c.chunk_index,
                "token_count": c.token_count,
            }
            for c in chunks
        ]

        self.chunks_col.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=docs,
            metadatas=metadatas
        )
        logger.info(
            f"[Repository] ✅ Persisted {len(chunks)} chunk vectors to ChromaDB. "
            f"Sample chunk IDs: {ids[:3]}"
        )

    def delete_chunks_by_source_id(self, source_id: str) -> None:
        """Delete all chunks associated with a given source_id."""
        try:
            self.chunks_col.delete(where={"source_id": source_id})
            logger.debug(f"Purged chunks for source {source_id}")
        except Exception as e:
            logger.warning(f"Error purging chunks for source {source_id}: {e}")

    def query_similarity(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        source_filters: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute semantic vector similarity search against ChromaDB chunks collection.
        Returns matched chunks with cosine similarity distances, text, and metadata.
        """
        where_clause = None
        if source_filters:
            if len(source_filters) == 1:
                where_clause = {"source_id": source_filters[0]}
            else:
                where_clause = {"source_id": {"$in": source_filters}}

        results = self.chunks_col.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_clause,
            include=["documents", "metadatas", "distances"]
        )

        matched_items: List[Dict[str, Any]] = []
        if not results or not results["ids"] or not results["ids"][0]:
            return matched_items

        ids = results["ids"][0]
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        for i in range(len(ids)):
            # Cosine distance in Chroma: similarity = 1.0 - distance
            dist = distances[i] if distances is not None else 1.0
            similarity = max(0.0, 1.0 - dist)

            matched_items.append({
                "chunk_id": ids[i],
                "content": documents[i],
                "metadata": metadatas[i],
                "distance": dist,
                "similarity_score": round(similarity, 4)
            })

        return matched_items

    # =========================================================================
    # Knowledge Base Statistics
    # =========================================================================

    def get_statistics(self) -> Dict[str, Any]:
        """Aggregate statistical summary of sources, domains, and chunks."""
        sources = self.list_sources(limit=1000)
        total_sources = len(sources)
        total_chunks = sum(s.chunk_count for s in sources)
        total_characters = sum(s.character_count for s in sources)
        indexed_count = sum(1 for s in sources if s.status == IngestionStatus.INDEXED)
        failed_count = sum(1 for s in sources if s.status == IngestionStatus.FAILED)

        domain_map = defaultdict(lambda: {"source_count": 0, "chunk_count": 0})
        for s in sources:
            domain_map[s.domain]["source_count"] += 1
            domain_map[s.domain]["chunk_count"] += s.chunk_count

        domain_breakdown = [
            {"domain": dom, "source_count": stat["source_count"], "chunk_count": stat["chunk_count"]}
            for dom, stat in sorted(domain_map.items(), key=lambda x: x[1]["chunk_count"], reverse=True)
        ]

        return {
            "total_sources": total_sources,
            "total_chunks": total_chunks,
            "total_characters": total_characters,
            "indexed_sources": indexed_count,
            "failed_sources": failed_count,
            "domain_breakdown": domain_breakdown,
        }

    # =========================================================================
    # Data Erasure & Reset
    # =========================================================================

    def clear_all(self) -> Dict[str, int]:
        """
        Completely reset and erase all ingested source metadata and vector chunks from ChromaDB.
        Returns metrics on deleted sources and chunks count.
        """
        try:
            sources_res = self.sources_col.get()
            source_ids = sources_res.get("ids", []) if sources_res else []
            sources_count = len(source_ids)
            if source_ids:
                self.sources_col.delete(ids=source_ids)

            chunks_res = self.chunks_col.get()
            chunk_ids = chunks_res.get("ids", []) if chunks_res else []
            chunks_count = len(chunk_ids)
            if chunk_ids:
                self.chunks_col.delete(ids=chunk_ids)

            logger.info(f"VectorRepository cleared: erased {sources_count} sources and {chunks_count} chunks.")
            return {"deleted_sources": sources_count, "deleted_chunks": chunks_count}
        except Exception as e:
            logger.error(f"Error while clearing VectorRepository: {e}")
            # Fallback: re-initialize collections via ChromaManager reset if delete fails
            try:
                self.chroma.client.reset()
                self.chroma.sources_collection = self.chroma.client.get_or_create_collection(
                    name=self.chroma.sources_collection.name
                )
                self.chroma.chunks_collection = self.chroma.client.get_or_create_collection(
                    name=self.chroma.chunks_collection.name
                )
                self.sources_col = self.chroma.sources_collection
                self.chunks_col = self.chroma.chunks_collection
                logger.info("ChromaDB reset performed as fallback.")
                return {"deleted_sources": -1, "deleted_chunks": -1}
            except Exception as reset_err:
                logger.error(f"ChromaDB reset fallback also failed: {reset_err}")
                raise e
