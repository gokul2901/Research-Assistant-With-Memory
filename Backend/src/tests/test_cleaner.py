"""
Unit tests for Content Cleaning, Boilerplate Stripping, and Text Normalization.
"""

import pytest
from bs4 import BeautifulSoup
from src.scraper.cleaner import remove_boilerplate, normalize_text


def test_remove_boilerplate():
    html_raw = """
    <html>
    <head><title>Test Page</title></head>
    <body>
        <nav><a href="/">Home</a><a href="/login">Login</a></nav>
        <header>Header Banner</header>
        <div class="cookie-banner">Please accept all cookies</div>
        <div class="ad-container">Special Discount Advertisement</div>
        <main>
            <h1>Real Article Title</h1>
            <p>This is the substantive article content that should be preserved.</p>
        </main>
        <footer>Copyright 2026 Example Corp</footer>
        <script>console.log('tracking');</script>
        <style>body { color: red; }</style>
    </body>
    </html>
    """
    soup = BeautifulSoup(html_raw, "html.parser")
    cleaned_soup = remove_boilerplate(soup)

    text = cleaned_soup.get_text()
    assert "Real Article Title" in text
    assert "substantive article content" in text
    assert "Please accept all cookies" not in text
    assert "Special Discount Advertisement" not in text
    assert "Header Banner" not in text
    assert "console.log" not in text


def test_normalize_text_entities_and_whitespace():
    raw_text = """
    # Introduction &amp; Overview
    
    
    This is an article with &quot;quotes&quot; and &lt;special&gt; characters.   
    
    
    - First item
    - Second item
    
    
    
    End of document.
    """
    normalized = normalize_text(raw_text)

    assert "# Introduction & Overview" in normalized
    assert 'with "quotes" and <special> characters.' in normalized
    assert "- First item" in normalized
    assert "\n\n\n\n" not in normalized  # Collapsed excess blank lines
