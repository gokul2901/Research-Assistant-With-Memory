"""
Content Cleaning, Boilerplate Removal, and Text Normalization Module.
"""

import re
import html
import unicodedata
from bs4 import BeautifulSoup
from src.utils.logger import logger

# CSS selectors for common boilerplate, ads, cookie banners, and navigation
UNWANTED_TAGS = [
    "script", "style", "nav", "footer", "header", "aside", "form",
    "iframe", "noscript", "svg", "button", "input", "select", "textarea"
]

UNWANTED_CLASSES_AND_IDS = [
    "cookie", "banner", "modal", "advertisement", "ad-container", "ads",
    "newsletter", "popup", "social-share", "share-buttons", "sidebar",
    "related-posts", "comments", "disclaimer", "sponsor", "nav-menu"
]


def remove_boilerplate(soup: BeautifulSoup) -> BeautifulSoup:
    """
    Remove boilerplate elements from BeautifulSoup tree:
    - Navigation bars, footers, headers, asides, scripts, forms
    - Advertisements, cookie consent banners, newsletter popups
    """
    # 1. Remove unwanted tags
    for tag in soup.find_all(UNWANTED_TAGS):
        tag.decompose()

    # 2. Remove unwanted classes and IDs
    for element in soup.find_all(attrs={"class": True}):
        classes = element.get("class", [])
        class_str = " ".join(classes).lower() if isinstance(classes, list) else str(classes).lower()
        if any(keyword in class_str for keyword in UNWANTED_CLASSES_AND_IDS):
            element.decompose()

    for element in soup.find_all(attrs={"id": True}):
        id_str = str(element.get("id", "")).lower()
        if any(keyword in id_str for keyword in UNWANTED_CLASSES_AND_IDS):
            element.decompose()

    return soup


def normalize_text(text: str) -> str:
    """
    Normalize extracted document text:
    - Decode HTML entities (&amp; -> &, &quot; -> ", etc.)
    - Unicode normalization (NFKC form)
    - Clean whitespace while strictly preserving Markdown headings (#, ##), lists (-, *), and blockquotes (>)
    - Compact excessive blank lines (maximum 2 consecutive newlines)
    """
    if not text:
        return ""

    # 1. Decode HTML entities
    decoded = html.unescape(text)

    # 2. Unicode normalization (NFKC)
    normalized = unicodedata.normalize("NFKC", decoded)

    # 3. Clean line by line
    cleaned_lines = []
    lines = normalized.splitlines()

    for line in lines:
        # Strip trailing and redundant internal tab/non-breaking spaces
        line_clean = line.rstrip()
        # Replace non-breaking spaces with standard space
        line_clean = line_clean.replace("\u00a0", " ").replace("\u200b", "")

        line_lower = line_clean.lower()
        if any(pat in line_lower for pat in [
            "enable javascript",
            "javascript must be enabled",
            "javascript is required",
            "eliminated the javascript",
            "javascript to use google maps"
        ]):
            continue

        # Preserve indentation for lists or code blocks if needed, else strip excess leading
        if line_clean.startswith(("#", "-", "*", ">", "1.", "2.", "3.", "4.", "5.")):
            cleaned_lines.append(line_clean)
        else:
            cleaned_lines.append(line_clean.strip())

    # 4. Collapse 3+ consecutive newlines into 2
    joined = "\n".join(cleaned_lines)
    compacted = re.sub(r"\n{3,}", "\n\n", joined)

    return compacted.strip()
