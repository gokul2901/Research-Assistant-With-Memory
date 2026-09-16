"""
RAG Agent — LangGraph-compatible agent that answers from indexed knowledge.
Uses the RAG Pipeline for retrieval + context assembly, then invokes
the Multi-LLM Router for grounded answer generation with citation attribution.
"""

import time
from typing import Optional, List, Dict, Any

from src.rag.rag_pipeline import RAGPipeline
from src.agents.llm.provider import MultiLLMRouter, LLMResponse
from src.config.settings import settings
from src.utils.logger import logger


class RAGAgent:
    """
    LangGraph-compatible RAG Agent.
    
    Workflow:
    1. Retrieve context via RAG Pipeline (embed → vector search → rerank)
    2. Evaluate context relevance
    3. If relevant: generate grounded answer with citations
    4. If not relevant: fall back to general knowledge response
    """

    def __init__(
        self,
        rag_pipeline: Optional[RAGPipeline] = None,
        llm_router: Optional[MultiLLMRouter] = None,
    ):
        self.pipeline = rag_pipeline or RAGPipeline()
        self.llm_router = llm_router or MultiLLMRouter()

    async def invoke(self, state: dict) -> dict:
        """
        Execute the RAG agent workflow.
        
        Expected state keys:
        - question (str): The user's question
        - top_k (int, optional): Number of top results
        - similarity_threshold (float, optional): Minimum similarity score
        - source_filters (list, optional): Filter by specific source IDs
        - model_override (str, optional): Force a specific LLM model
        
        Returns updated state with:
        - answer, citations, sources, model_used, is_grounded,
          retrieved_chunks_count, execution_time_ms
        """
        start_time = time.perf_counter()

        question = state["question"]
        top_k = state.get("top_k", settings.DEFAULT_TOP_K)
        similarity_threshold = state.get(
            "similarity_threshold", settings.DEFAULT_SIMILARITY_THRESHOLD
        )
        source_filters = state.get("source_filters")
        model_override = state.get("model_override")

        logger.info(
            f"[RAGAgent] 🔍 Query: '{question[:80]}' | "
            f"threshold={similarity_threshold} | top_k={top_k}"
        )

        # Step 1 & 2: Retrieve and evaluate context
        rag_result = self.pipeline.run_retrieval(
            query=question,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
            source_filters=source_filters,
        )

        context_pkg = rag_result.context_package

        logger.info(
            f"[RAGAgent] 📦 Retrieval complete: {len(context_pkg.chunks)} chunks found "
            f"(sources: {list(context_pkg.sources_map.keys())})"
        )

        # Step 3: Generate answer based on context relevance
        if not rag_result.has_relevant_context:
            logger.info(
                f"[RAGAgent] No relevant context found (best_score={round(rag_result.best_rerank_score, 3)}). "
                "Falling back to general knowledge response."
            )
            llm_res: LLMResponse = await self.llm_router.generate_general_response(
                question=question,
                model_override=model_override,
            )
            exec_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

            return {
                "answer": llm_res.content,
                "citations": [],
                "sources": [],
                "model_used": llm_res.model_used,
                "is_grounded": False,
                "retrieved_chunks_count": len(context_pkg.chunks),
                "execution_time_ms": exec_time_ms,
            }

        # Step 3b: Generate grounded answer with context
        llm_res: LLMResponse = await self.llm_router.generate_response(
            question=question,
            context_str=context_pkg.formatted_prompt_context,
            model_override=model_override,
        )

        exec_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

        if not llm_res.success:
            return {
                "answer": llm_res.content,
                "citations": [],
                "sources": [
                    {
                        "source_id": info["source_id"],
                        "url": info["url"],
                        "title": info["title"],
                        "domain": info.get("domain", ""),
                        "chunk_count": len([c for c in context_pkg.chunks if c.source_id == info["source_id"]]),
                    }
                    for info in context_pkg.sources_map.values()
                ],
                "model_used": llm_res.model_used,
                "is_grounded": False,
                "retrieved_chunks_count": len(context_pkg.chunks),
                "execution_time_ms": exec_time_ms,
            }

        # Step 4: Process citations
        raw_answer, citations, referenced_sources, is_grounded = (
            self.pipeline.process_citations(
                raw_answer=llm_res.content,
                context_pkg=context_pkg,
            )
        )

        return {
            "answer": raw_answer,
            "citations": citations,
            "sources": referenced_sources,
            "model_used": llm_res.model_used,
            "is_grounded": is_grounded,
            "retrieved_chunks_count": len(context_pkg.chunks),
            "execution_time_ms": exec_time_ms,
        }
