"""
URL normalization, validation, canonicalization, and parsing utilities.
"""

from typing import Tuple, Optional, Set
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
import re
from src.scraper.security import validate_url_security


TRACKING_PARAMS: Set[str] = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "gclid", "fbclid", "msclkid", "ref", "source", "mc_cid", "mc_eid",
    "yclid", "_ga", "_gl", "wbraid", "gbraid", "trk"
}


def normalize_url(raw_url: str) -> str:
    """
    Normalize target URL by:
    - Trimming whitespace
    - Lowercasing scheme and netloc
    - Removing hash fragments
    - Stripping common analytics tracking query parameters
    - Normalizing path trailing slash (preserve root '/')
    """
    if not raw_url:
        return ""

    url = raw_url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        parsed = urlparse(url)
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()

        # Filter out tracking query parameters
        query_params = parse_qsl(parsed.query, keep_blank_values=False)
        filtered_params = [(k, v) for k, v in query_params if k.lower() not in TRACKING_PARAMS]
        new_query = urlencode(filtered_params)

        # Normalize path
        path = parsed.path or "/"
        if len(path) > 1 and path.endswith("/"):
            path = path.rstrip("/")

        # Discard fragment (anchor #)
        return urlunparse((scheme, netloc, path, parsed.params, new_query, ""))
    except Exception:
        return url.strip()


def extract_domain(url: str) -> str:
    """Extract clean domain name without 'www.' prefix or port number."""
    if not url:
        return "unknown"
    try:
        url_to_parse = url.strip()
        if not url_to_parse.startswith(("http://", "https://")):
            url_to_parse = "https://" + url_to_parse
        parsed = urlparse(url_to_parse)
        netloc = parsed.netloc.lower()
        if ":" in netloc:
            netloc = netloc.split(":")[0]
        if netloc.startswith("www."):
            netloc = netloc[4:]
        return netloc or "unknown"
    except Exception:
        return "unknown"


def is_valid_http_url(url: str) -> bool:
    """Check if string is a valid HTTP/HTTPS URL with non-empty netloc."""
    if not url or not isinstance(url, str):
        return False
    try:
        parsed = urlparse(url.strip())
        return bool(parsed.scheme in ("http", "https") and parsed.netloc)
    except Exception:
        return False


def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Comprehensive URL validation combining syntax, scheme, and SSRF security checks.
    
    Returns:
        (is_valid, error_reason)
    """
    if not url or not isinstance(url, str):
        return False, "URL must be a non-empty string."

    clean_url = url.strip()
    if not is_valid_http_url(clean_url):
        return False, "Invalid URL format. Must start with http:// or https:// with a valid domain."

    # SSRF security check
    is_safe, error_msg = validate_url_security(clean_url)
    if not is_safe:
        return False, error_msg

    return True, None
