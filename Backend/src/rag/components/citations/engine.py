"""
Citation Attribution and Source Grounding Engine.
Resolves citation markers ([Source X]) to verified source URLs, chunk metadata, and titles.
"""

import re
from typing import List, Dict, Any, Tuple, Optional, Set
from src.schemas.chat import CitationItem, SourceMetadataRef
from src.rag.components.retrieval.search import ContextPackage
from src.utils.logger import logger


class CitationEngine:
    # Regex matching [Source 1], [Source 2], [1], [Source 1][Source 2], [Source 1, 2]
    SOURCE_MARKER_REGEX = re.compile(
        r"\[(?:Source\s*)?(\d+)(?:\s*,\s*(?:Source\s*)?(\d+))*\]",
        re.IGNORECASE
    )

    def extract_citation_indices(self, text: str) -> Set[int]:
        """Extract all cited numbers from text."""
        indices = set()
        # Find explicit bracketed markers
        matches = re.finditer(r"\[(?:Source\s*)?(\d+)\]", text, re.IGNORECASE)
        for m in matches:
            try:
                indices.add(int(m.group(1)))
            except ValueError:
                pass

        # Also find multi-citations like [Source 1, 2] or [1, 2]
        multi_matches = re.finditer(r"\[(?:Source\s*)?(\d+(?:\s*,\s*(?:Source\s*)?\d+)+)\]", text, re.IGNORECASE)
        for m in multi_matches:
            raw_nums = re.findall(r"\d+", m.group(1))
            for n in raw_nums:
                indices.add(int(n))

        return indices

    def process_citations(
        self,
        raw_answer: str,
        context_package: ContextPackage
    ) -> Tuple[str, List[CitationItem], List[SourceMetadataRef], bool]:
        """
        Process LLM output to extract citations, map to sources, and determine groundedness.
        """
        is_empty_or_fallback = (
            "not found in sources" in raw_answer.lower() or
            "not found in the provided source" in raw_answer.lower() or
            "not found in the provided sources" in raw_answer.lower() or
            "the requested information was not found" in raw_answer.lower() or
            not raw_answer.strip()
        )

        if is_empty_or_fallback:
            return "The requested information was not found in the provided source.", [], [], False

        cited_indices = self.extract_citation_indices(raw_answer)
        citations: List[CitationItem] = []
        referenced_sources_dict: Dict[str, SourceMetadataRef] = {}

        # If LLM didn't include explicit bracket markers, but generated an answer,
        # attribute all retrieved sources that provided high scoring context
        if not cited_indices and context_package.sources_map:
            logger.debug("No explicit [Source X] markers found; attributing top retrieved sources.")
            cited_indices = set(context_package.sources_map.keys())

        for idx in sorted(cited_indices):
            if idx in context_package.sources_map:
                src_info = context_package.sources_map[idx]
                source_id = src_info["source_id"]
                url = src_info["url"]
                title = src_info["title"]
                domain = src_info.get("domain", "")

                # Find representative chunk snippet
                matching_chunks = [c for c in context_package.chunks if c.source_id == source_id]
                snippet = matching_chunks[0].content[:200] + "..." if matching_chunks else ""
                chunk_id = matching_chunks[0].chunk_id if matching_chunks else None

                citation = CitationItem(
                    citation_index=idx,
                    source_id=source_id,
                    url=url,
                    title=title,
                    chunk_id=chunk_id,
                    snippet=snippet
                )
                citations.append(citation)

                if source_id not in referenced_sources_dict:
                    referenced_sources_dict[source_id] = SourceMetadataRef(
                        source_id=source_id,
                        url=url,
                        title=title,
                        domain=domain,
                        chunk_count=len(matching_chunks)
                    )

        referenced_sources = list(referenced_sources_dict.values())
        is_grounded = len(citations) > 0

        return raw_answer, citations, referenced_sources, is_grounded
