"""
Unit tests for URL Normalization, Validation, and SSRF Security Protection.
"""

import pytest
from src.scraper.url_utils import normalize_url, validate_url, extract_domain, is_valid_http_url
from src.scraper.security import validate_url_security, is_ip_blocked
import ipaddress


def test_normalize_url_basic():
    url = "  https://docs.example.com/guide/  "
    normalized = normalize_url(url)
    assert normalized == "https://docs.example.com/guide"


def test_normalize_url_removes_tracking_params():
    url = "https://example.com/article?utm_source=twitter&utm_medium=social&page=2&fbclid=12345"
    normalized = normalize_url(url)
    assert "page=2" in normalized
    assert "utm_source" not in normalized
    assert "fbclid" not in normalized


def test_normalize_url_scheme_default():
    url = "example.com/path"
    normalized = normalize_url(url)
    assert normalized.startswith("https://example.com/path")


def test_extract_domain():
    assert extract_domain("https://www.tiangolo.fastapi.com/path") == "tiangolo.fastapi.com"
    assert extract_domain("http://docs.pydantic.dev:8080/latest/") == "docs.pydantic.dev"
    assert extract_domain("invalid-url") == "invalid-url"


def test_is_valid_http_url():
    assert is_valid_http_url("https://fastapi.tiangolo.com") is True
    assert is_valid_http_url("http://example.org/test") is True
    assert is_valid_http_url("ftp://example.com") is False
    assert is_valid_http_url("javascript:alert(1)") is False
    assert is_valid_http_url("") is False


def test_ssrf_blocked_ip_ranges():
    assert is_ip_blocked(ipaddress.ip_address("127.0.0.1")) is True
    assert is_ip_blocked(ipaddress.ip_address("10.0.0.5")) is True
    assert is_ip_blocked(ipaddress.ip_address("192.168.1.100")) is True
    assert is_ip_blocked(ipaddress.ip_address("172.16.5.10")) is True
    assert is_ip_blocked(ipaddress.ip_address("169.254.169.254")) is True # Cloud Metadata
    assert is_ip_blocked(ipaddress.ip_address("8.8.8.8")) is False # Public IP


def test_ssrf_validation_hostnames():
    is_safe, err = validate_url_security("http://localhost/admin")
    assert is_safe is False
    assert "blocked" in err.lower()

    is_safe, err = validate_url_security("http://127.0.0.1:8000/docs")
    assert is_safe is False

    is_safe, err = validate_url_security("http://169.254.169.254/latest/meta-data")
    assert is_safe is False
