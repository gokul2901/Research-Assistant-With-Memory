"""
Unit tests for Multi-Level Duplicate Detection (URL, Canonical URL, and Content Hash).
"""

import pytest
from src.scraper.url_utils import normalize_url
from src.scraper.metadata import calculate_content_hash


def test_level_1_url_duplicate_normalization():
    url1 = "https://example.com/blog/article?utm_source=google"
    url2 = "https://example.com/blog/article/"
    url3 = "https://example.com/blog/article?utm_campaign=winter"

    norm1 = normalize_url(url1)
    norm2 = normalize_url(url2)
    norm3 = normalize_url(url3)

    assert norm1 == norm2 == norm3 == "https://example.com/blog/article"


def test_level_3_content_hash_duplicate():
    text_version_a = "Retrieval-Augmented Generation enhances LLMs by retrieving relevant context."
    text_version_b = "Retrieval-Augmented Generation enhances LLMs by retrieving relevant context."
    text_version_c = "A different text regarding database systems."

    hash_a = calculate_content_hash(text_version_a)
    hash_b = calculate_content_hash(text_version_b)
    hash_c = calculate_content_hash(text_version_c)

    assert hash_a == hash_b
    assert hash_a != hash_c
