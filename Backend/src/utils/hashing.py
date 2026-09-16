"""
Cryptographic hashing utilities for URL deduplication and content versioning.
"""

import hashlib
import uuid


def generate_content_hash(text: str) -> str:
    """Generate a deterministic SHA-256 hash from text content."""
    normalized = text.strip().encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()


def generate_url_hash(url: str) -> str:
    """Generate a deterministic SHA-256 hash from a canonical URL."""
    normalized = url.strip().lower().encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()


def generate_uuid() -> str:
    """Generate a random UUID v4 string."""
    return str(uuid.uuid4())
