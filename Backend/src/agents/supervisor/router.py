"""
Intent Classification & Query Router.
Determines whether a user query requires RAG (knowledge base retrieval)
or can be answered from general LLM knowledge.
"""

from enum import Enum
from typing import Optional
from src.agents.llm.provider import MultiLLMRouter
from src.utils.logger import logger


class QueryIntent(str, Enum):
    """Possible intents for incoming user queries."""
    RAG_QUERY = "rag_query"          # Needs knowledge base retrieval
    GENERAL_KNOWLEDGE = "general"     # General question, no RAG needed


INTENT_CLASSIFICATION_PROMPT = """You are an intent classifier for a Research Assistant with a persistent knowledge base.

Your job is to classify the user's query into one of two categories:
- "rag_query": The user is asking a question that likely requires information from indexed/ingested sources (research documents, articles, web pages). This includes questions about specific topics, facts, data, or information that would be in a knowledge base.
- "general": The user is asking a general conversational question, greeting, meta-question about the system, or something that clearly doesn't need document retrieval (e.g., "hello", "what can you do?", "how are you?", basic math, general knowledge everyone knows).

IMPORTANT: When in doubt, classify as "rag_query" — it's better to search and find nothing than to skip searching when relevant documents exist.

Respond with ONLY the classification label: either "rag_query" or "general". Nothing else."""


class IntentClassifier:
    """
    Classifies user intent to route to the appropriate agent.
    Uses a fast LLM call to determine if the query needs RAG retrieval.
    """

    def __init__(self, llm_router: Optional[MultiLLMRouter] = None):
        self.llm_router = llm_router or MultiLLMRouter()

    async def classify(self, query: str) -> QueryIntent:
        """
        Classify user query intent.
        
        Uses LLM-based classification for accuracy, with heuristic fallbacks
        if the LLM call fails.
        """
        # Quick heuristic pre-check for obvious cases
        quick_intent = self._heuristic_classify(query)
        if quick_intent is not None:
            logger.info(f"[IntentClassifier] Heuristic classification: {quick_intent.value} for '{query[:60]}'")
            return quick_intent

        # LLM-based classification for ambiguous queries
        try:
            messages = [
                {"role": "system", "content": INTENT_CLASSIFICATION_PROMPT},
                {"role": "user", "content": query},
            ]

            response = await self.llm_router.generate_from_messages(
                messages=messages,
                temperature=0.0,
            )

            if response.success:
                raw_label = response.content.strip().lower().replace('"', '').replace("'", "")
                if "rag" in raw_label:
                    intent = QueryIntent.RAG_QUERY
                elif "general" in raw_label:
                    intent = QueryIntent.GENERAL_KNOWLEDGE
                else:
                    # Default to RAG when uncertain
                    intent = QueryIntent.RAG_QUERY

                logger.info(
                    f"[IntentClassifier] LLM classification: {intent.value} "
                    f"(raw: '{raw_label}') for '{query[:60]}'"
                )
                return intent

        except Exception as e:
            logger.warning(f"[IntentClassifier] LLM classification failed: {e}. Defaulting to RAG.")

        # Fallback: default to RAG (better to search than miss)
        return QueryIntent.RAG_QUERY

    @staticmethod
    def _heuristic_classify(query: str) -> Optional[QueryIntent]:
        """
        Fast heuristic pre-check for obviously general or obviously RAG queries.
        Returns None if the query is ambiguous and needs LLM classification.
        """
        query_lower = query.strip().lower()

        # Obvious greetings / meta-questions
        greeting_patterns = [
            "hello", "hi", "hey", "good morning", "good evening",
            "what can you do", "who are you", "help me",
            "how are you", "what's up", "thanks", "thank you",
        ]
        for pattern in greeting_patterns:
            if query_lower == pattern or query_lower.startswith(pattern + " ") or query_lower.startswith(pattern + "?"):
                return QueryIntent.GENERAL_KNOWLEDGE

        # Very short queries (1-2 words) are usually greetings or commands
        word_count = len(query_lower.split())
        if word_count <= 2 and not any(kw in query_lower for kw in ["what", "how", "why", "when", "where", "explain", "describe"]):
            return QueryIntent.GENERAL_KNOWLEDGE

        # Return None for ambiguous queries — let LLM decide
        return None
