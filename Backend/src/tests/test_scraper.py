"""
Unit tests for Web Scraper and Content Extraction Pipeline.
"""

import pytest
from src.scraper.extractor import ContentExtractor, ExtractedDocument
from src.scraper.metadata import extract_metadata, calculate_content_hash, detect_language


def test_content_extractor_with_html():
    html_sample = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>FastAPI Tutorial - High Performance Web Framework</title>
        <link rel="canonical" href="https://fastapi.tiangolo.com/tutorial/first-steps/" />
        <meta name="description" content="A comprehensive tutorial on building async APIs in Python." />
        <meta property="og:title" content="FastAPI Tutorial" />
    </head>
    <body>
        <main>
            <h1>First Steps with FastAPI</h1>
            <p>FastAPI is a modern, high-performance web framework for building APIs with Python 3.8+.</p>
            <h2>Creating an App Instance</h2>
            <p>You can create an app instance by importing FastAPI and instantiating it with app = FastAPI().</p>
            <ul>
                <li>Automatic OpenAPI documentation at /docs</li>
                <li>Pydantic data validation and serialization</li>
            </ul>
        </main>
    </body>
    </html>
    """
    extractor = ContentExtractor(min_content_length=30)
    doc: ExtractedDocument = extractor.extract(html_sample, "https://fastapi.tiangolo.com/tutorial/first-steps/")

    assert doc.status == "EXTRACTED"
    assert "FastAPI" in doc.title
    assert "First Steps with FastAPI" in doc.clean_text
    assert doc.canonical_url == "https://fastapi.tiangolo.com/tutorial/first-steps"
    assert doc.language == "en"
    assert doc.word_count > 10
    assert len(doc.content_hash) == 64 # SHA-256


def test_content_extractor_empty_or_short_html():
    extractor = ContentExtractor(min_content_length=50)
    doc = extractor.extract("<html><body><p>Too short</p></body></html>", "https://example.com/short")
    assert doc.status == "FAILED_EXTRACTION"
    assert "below minimum threshold" in doc.error


def test_language_detection():
    english_text = "This is a comprehensive research assistant indexing document content."
    assert detect_language(english_text, "en") == "en"

    tamil_text = "இது ஒரு தமிழ் ஆவணம் ஆகும். ஆராய்ச்சி உதவியாளர் தரவுகளைச் சேமிக்கிறது."
    assert detect_language(tamil_text) == "ta"

    hindi_text = "यह एक हिंदी दस्तावेज है जो ज्ञानकोष में सुरक्षित किया गया है।"
    assert detect_language(hindi_text) == "hi"
