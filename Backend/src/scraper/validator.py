"""
URL validation and canonicalization utilities.
"""

from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
import re


TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "gclid", "fbclid", "msclkid", "ref", "source", "mc_cid", "mc_eid"
}


def normalize_url(raw_url: str) -> str:
    """
    Normalize URL by:
    - Trimming whitespace
    - Validating scheme (default to https if missing)
    - Stripping common tracking query parameters
    - Lowercasing scheme and netloc
    - Removing trailing slash from path (unless root)
    """
    url = raw_url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()

    # Filter out tracking query parameters
    query_params = parse_qsl(parsed.query, keep_blank_values=False)
    filtered_params = [(k, v) for k, v in query_params if k.lower() not in TRACKING_PARAMS]
    new_query = urlencode(filtered_params)

    # Normalize path
    path = parsed.path or "/"

    return urlunparse((scheme, netloc, path, parsed.params, new_query, ""))


def extract_domain(url: str) -> str:
    """Extract domain name from URL."""
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        # Remove port if present
        if ":" in netloc:
            netloc = netloc.split(":")[0]
        # Remove www. prefix if present
        if netloc.startswith("www."):
            netloc = netloc[4:]
        return netloc or "unknown"
    except Exception:
        return "unknown"


def is_valid_http_url(url: str) -> bool:
    """Check if string is a syntactically valid HTTP/HTTPS URL."""
    try:
        parsed = urlparse(url)
        return bool(parsed.scheme in ("http", "https") and parsed.netloc)
    except Exception:
        return False
