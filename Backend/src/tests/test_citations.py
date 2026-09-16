"""
Unit tests for Citation Engine and Hallucination Prevention.
"""

from src.rag.components.citations.engine import CitationEngine
from src.rag.components.retrieval.search import ContextPackage, ContextChunk


def test_citation_index_extraction():
    engine = CitationEngine()
    text = "FastAPI is a modern web framework [Source 1]. It supports async Python [Source 2] and typing [1, 3]."
    indices = engine.extract_citation_indices(text)
    assert 1 in indices
    assert 2 in indices
    assert 3 in indices


def test_citation_processing_and_mapping():
    engine = CitationEngine()
    
    # Mock context package
    chunk = ContextChunk(
        chunk_id="chk_1",
        source_id="src_fastapi",
        url="https://fastapi.tiangolo.com",
        title="FastAPI Documentation",
        content="FastAPI is a modern, fast web framework for building APIs with Python 3.8+.",
        similarity_score=0.92,
        rerank_score=0.95,
        chunk_index=0
    )
    
    pkg = ContextPackage(
        query="What is FastAPI?",
        chunks=[chunk],
        formatted_prompt_context="[Source 1] FastAPI is a modern framework.",
        sources_map={
            1: {
                "marker": 1,
                "source_id": "src_fastapi",
                "url": "https://fastapi.tiangolo.com",
                "title": "FastAPI Documentation",
                "domain": "fastapi.tiangolo.com"
            }
        }
    )

    answer = "FastAPI is a fast Python framework for building modern APIs [Source 1]."
    processed_ans, citations, sources, is_grounded = engine.process_citations(answer, pkg)

    assert is_grounded is True
    assert len(citations) == 1
    assert citations[0].citation_index == 1
    assert citations[0].url == "https://fastapi.tiangolo.com"
    assert len(sources) == 1


def test_anti_hallucination_fallback():
    engine = CitationEngine()
    pkg = ContextPackage(query="Unknown topic", chunks=[], formatted_prompt_context="", sources_map={})
    answer = "The requested information was not found in the provided source."
    
    processed_ans, citations, sources, is_grounded = engine.process_citations(answer, pkg)
    assert processed_ans == "The requested information was not found in the provided source."
    assert citations == []
    assert sources == []
    assert is_grounded is False
