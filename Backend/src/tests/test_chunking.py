"""
Unit tests for Recursive Chunking Engine.
"""

from src.rag.components.data_processor.chunking import RecursiveChunkingEngine
from src.models.domain import Source, IngestionStatus


def test_recursive_chunking_hierarchy():
    chunker = RecursiveChunkingEngine(chunk_size=100, chunk_overlap=20)
    source = Source(
        source_id="src_test_123",
        url="https://example.com/rag",
        title="RAG Systems Overview",
        domain="example.com",
        status=IngestionStatus.PENDING
    )

    sample_text = (
        "# Introduction to RAG\n\n"
        "Retrieval-Augmented Generation bridges pre-trained LLMs with private knowledge bases.\n\n"
        "## Vector Search\n\n"
        "Dense embeddings map text into continuous vector spaces where cosine distance computes relevance.\n\n"
        "## Hallucination Guardrails\n\n"
        "By restricting generation strictly to retrieved sources, factual consistency is preserved."
    )

    chunks = chunker.chunk_source(source, sample_text)

    assert len(chunks) > 0
    for idx, c in enumerate(chunks):
        assert c.source_id == "src_test_123"
        assert c.url == "https://example.com/rag"
        assert c.chunk_index == idx
        assert c.token_count > 0
        assert len(c.content) > 0
