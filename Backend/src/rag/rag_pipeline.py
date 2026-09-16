"""
RAG Pipeline Orchestrator.
Composes all RAG components (retrieval, citations, prompts) into a unified pipeline
that can be invoked by agents or services.
"""

from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass, field

from src.rag.components.retrieval.search import SemanticRetriever, ContextPackage
from src.rag.components.citations.engine import CitationEngine
from src.rag.prompts.templates import (
    RAG_SYSTEM_PROMPT,
    GENERAL_KNOWLEDGE_SYSTEM_PROMPT,
    build_rag_user_prompt,
    build_general_knowledge_prompt,
)
from src.schemas.chat import CitationItem, SourceMetadataRef
from src.config.settings import settings
from src.utils.logger import logger


@dataclass
class RAGResult:
    """Structured result from the RAG pipeline."""
    answer: str
    citations: List[CitationItem] = field(default_factory=list)
    sources: List[SourceMetadataRef] = field(default_factory=list)
    is_grounded: bool = False
    context_package: Optional[ContextPackage] = None
    has_relevant_context: bool = False
    best_rerank_score: float = 0.0


class RAGPipeline:
    """
    Orchestrates the full Retrieval-Augmented Generation pipeline.

    Responsibilities:
    - Retrieve relevant context from the vector store
    - Evaluate context relevance (confidence scoring)
    - Build LLM prompt messages with retrieved context
    - Process citations from LLM response
    
    The pipeline does NOT call the LLM directly — that is the agent's responsibility.
    This ensures clean separation between retrieval logic and generation logic.
    """

    MIN_CONFIDENCE = 0.20  # Minimum rerank score to consider context relevant

    def __init__(
        self,
        retriever: Optional[SemanticRetriever] = None,
        citation_engine: Optional[CitationEngine] = None,
    ):
        self.retriever = retriever or SemanticRetriever()
        self.citation_engine = citation_engine or CitationEngine()

    def retrieve_context(
        self,
        query: str,
        top_k: int = settings.DEFAULT_TOP_K,
        similarity_threshold: float = settings.DEFAULT_SIMILARITY_THRESHOLD,
        source_filters: Optional[List[str]] = None,
    ) -> ContextPackage:
        """
        Step 1: Embed query → Vector search → Rerank → Return context package.
        """
        return self.retriever.retrieve(
            query=query,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
            source_filters=source_filters,
        )

    def evaluate_context(self, context_pkg: ContextPackage) -> Tuple[bool, float]:
        """
        Step 2: Determine if retrieved context is relevant enough for a grounded answer.
        Returns (has_relevant_context, best_rerank_score).
        """
        best_score = max(
            (c.rerank_score for c in context_pkg.chunks), default=0.0
        )
        has_relevant = len(context_pkg.chunks) > 0 and best_score >= self.MIN_CONFIDENCE

        logger.info(
            f"[RAGPipeline] 🎯 Best rerank score: {round(best_score, 3)} | "
            f"MIN_CONFIDENCE={self.MIN_CONFIDENCE} | using_rag={has_relevant}"
        )

        return has_relevant, best_score

    def build_rag_messages(
        self, question: str, context_pkg: ContextPackage
    ) -> List[Dict[str, str]]:
        """
        Step 3a: Build LLM prompt messages WITH retrieved context for grounded answer.
        """
        user_prompt = build_rag_user_prompt(question, context_pkg.formatted_prompt_context)
        return [
            {"role": "system", "content": RAG_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

    def build_general_messages(self, question: str) -> List[Dict[str, str]]:
        """
        Step 3b: Build LLM prompt messages for general knowledge (no RAG context).
        """
        user_prompt = build_general_knowledge_prompt(question)
        return [
            {"role": "system", "content": GENERAL_KNOWLEDGE_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

    def process_citations(
        self,
        raw_answer: str,
        context_pkg: ContextPackage,
    ) -> Tuple[str, List[CitationItem], List[SourceMetadataRef], bool]:
        """
        Step 4: Extract and verify citations from LLM response.
        """
        return self.citation_engine.process_citations(
            raw_answer=raw_answer,
            context_package=context_pkg,
        )

    def run_retrieval(
        self,
        query: str,
        top_k: int = settings.DEFAULT_TOP_K,
        similarity_threshold: float = settings.DEFAULT_SIMILARITY_THRESHOLD,
        source_filters: Optional[List[str]] = None,
    ) -> RAGResult:
        """
        Execute retrieval + evaluation (Steps 1-2).
        Returns a RAGResult with context_package populated but no answer yet.
        The calling agent is responsible for LLM generation and then calling process_citations.
        """
        # Step 1: Retrieve
        context_pkg = self.retrieve_context(
            query=query,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
            source_filters=source_filters,
        )

        # Step 2: Evaluate
        has_relevant, best_score = self.evaluate_context(context_pkg)

        return RAGResult(
            answer="",  # To be filled by the agent after LLM call
            context_package=context_pkg,
            has_relevant_context=has_relevant,
            best_rerank_score=best_score,
        )
