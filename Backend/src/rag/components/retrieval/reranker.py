"""
Re-ranking and Context Scoring Engine.
Applies lexical overlap boosting, reciprocal rank fusion, and relevance filtering.
"""

from typing import List, Dict, Any
import re


class RelevanceReranker:
    """
    Reranks semantic vector search results by combining dense cosine similarity
    with exact lexical term overlap and structural heading importance.
    """

    @staticmethod
    def _extract_keywords(text: str) -> set[str]:
        words = re.findall(r"\b[a-zA-Z0-9_-]{3,}\b", text.lower())
        stopwords = {
            "the", "and", "for", "with", "this", "that", "from", "are",
            "have", "has", "was", "were", "what", "which", "where", "how"
        }
        return set(w for w in words if w not in stopwords)

    def rerank(
        self,
        query: str,
        retrieved_items: List[Dict[str, Any]],
        similarity_threshold: float = 0.35,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Filter by threshold and score candidates."""
        if not retrieved_items:
            return []

        query_keywords = self._extract_keywords(query)
        scored_candidates = []

        for item in retrieved_items:
            similarity = item.get("similarity_score", 0.0)
            if similarity < similarity_threshold:
                continue

            content = item.get("content", "").lower()
            metadata = item.get("metadata", {})
            title = metadata.get("title", "").lower()

            # Calculate lexical keyword overlap
            content_keywords = self._extract_keywords(content)
            title_keywords = self._extract_keywords(title)

            overlap_count = len(query_keywords.intersection(content_keywords))
            title_overlap_count = len(query_keywords.intersection(title_keywords))

            lexical_boost = 0.0
            if query_keywords:
                overlap_ratio = overlap_count / len(query_keywords)
                title_ratio = title_overlap_count / len(query_keywords)
                lexical_boost = (overlap_ratio * 0.15) + (title_ratio * 0.10)

            # Combined hybrid score (75% semantic vector similarity + 25% lexical boost)
            final_score = round(min(1.0, (similarity * 0.75) + lexical_boost), 4)

            scored_item = dict(item)
            scored_item["rerank_score"] = final_score
            scored_candidates.append(scored_item)

        # Fallback for broad/conversational queries if strict threshold filtered everything out
        if not scored_candidates and retrieved_items:
            for item in retrieved_items:
                similarity = item.get("similarity_score", 0.0)
                if similarity >= 0.05:
                    scored_item = dict(item)
                    scored_item["rerank_score"] = round(similarity, 4)
                    scored_candidates.append(scored_item)

        # Sort by rerank score descending
        scored_candidates.sort(key=lambda x: x["rerank_score"], reverse=True)
        return scored_candidates[:max_results]
