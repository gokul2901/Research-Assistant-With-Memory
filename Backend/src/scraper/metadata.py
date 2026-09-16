"""
Page Metadata and Language Extraction Module.
"""

import hashlib
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
from src.scraper.url_utils import extract_domain, normalize_url


def calculate_content_hash(text: str) -> str:
    """Compute deterministic SHA-256 hash of clean text for duplicate detection."""
    if not text:
        return ""
    clean_bytes = text.strip().encode("utf-8")
    return hashlib.sha256(clean_bytes).hexdigest()


def detect_language(text: str, html_lang: Optional[str] = None) -> str:
    """
    Detect document language:
    - Checks HTML lang attribute if available (e.g., 'en', 'ta', 'hi', 'fr', 'es')
    - Basic heuristic character-range analysis for non-Latin scripts
    """
    if html_lang:
        clean_lang = html_lang.strip().split("-")[0].split("_")[0].lower()
        if len(clean_lang) == 2:
            return clean_lang

    if not text:
        return "en"

    sample = text[:1000]

    # Heuristic Unicode block checks for Indian & Asian scripts
    tamil_chars = sum(1 for c in sample if "\u0b80" <= c <= "\u0bff")
    devanagari_chars = sum(1 for c in sample if "\u0900" <= c <= "\u097f") # Hindi/Sanskrit
    malayalam_chars = sum(1 for c in sample if "\u0d00" <= c <= "\u0d7f")
    telugu_chars = sum(1 for c in sample if "\u0c00" <= c <= "\u0c7f")

    if tamil_chars > 20:
        return "ta"
    if devanagari_chars > 20:
        return "hi"
    if malayalam_chars > 20:
        return "ml"
    if telugu_chars > 20:
        return "te"

    return "en"


def extract_metadata(html_content: str, url: str, clean_text: str) -> Dict[str, Any]:
    """
    Extract comprehensive page metadata:
    - Title (meta og:title -> <title> -> <h1> -> domain)
    - Canonical URL (<link rel="canonical"> -> og:url -> url)
    - Description (<meta name="description"> / og:description)
    - Author & published date
    - Domain & language
    - Word & character counts
    - Content SHA-256 hash
    """
    soup = BeautifulSoup(html_content, "html.parser")
    domain = extract_domain(url)

    # 1. Canonical URL
    canonical_url = None
    canonical_tag = soup.find("link", rel=lambda x: x and "canonical" in str(x).lower())
    if canonical_tag and canonical_tag.get("href"):
        canonical_url = normalize_url(canonical_tag["href"])

    if not canonical_url:
        og_url = soup.find("meta", property="og:url")
        if og_url and og_url.get("content"):
            canonical_url = normalize_url(og_url["content"])

    if not canonical_url:
        canonical_url = normalize_url(url)

    # 2. Title
    title = None
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        title = og_title["content"].strip()

    if not title and soup.title and soup.title.string:
        title = soup.title.string.strip()

    if not title:
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text().strip()

    if not title:
        title = f"Document from {domain}"

    # 3. Description
    description = None
    meta_desc = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", property="og:description")
    if meta_desc and meta_desc.get("content"):
        description = meta_desc["content"].strip()

    # 4. Author & Date
    author = None
    meta_author = soup.find("meta", attrs={"name": "author"}) or soup.find("meta", property="article:author")
    if meta_author and meta_author.get("content"):
        author = meta_author["content"].strip()

    published_date = None
    meta_date = (
        soup.find("meta", property="article:published_time") or
        soup.find("meta", attrs={"name": "date"}) or
        soup.find("meta", attrs={"name": "pubdate"})
    )
    if meta_date and meta_date.get("content"):
        published_date = meta_date["content"].strip()

    # 5. Language
    html_tag = soup.find("html")
    html_lang = html_tag.get("lang") if html_tag else None
    language = detect_language(clean_text, html_lang)

    # 6. Word & Character counts & SHA-256 Hash
    word_count = len(clean_text.split()) if clean_text else 0
    character_count = len(clean_text) if clean_text else 0
    content_hash = calculate_content_hash(clean_text)

    return {
        "url": url,
        "canonical_url": canonical_url,
        "title": title,
        "description": description,
        "author": author,
        "published_date": published_date,
        "domain": domain,
        "language": language,
        "word_count": word_count,
        "character_count": character_count,
        "content_hash": content_hash,
    }
