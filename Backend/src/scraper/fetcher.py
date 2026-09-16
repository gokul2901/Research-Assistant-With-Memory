"""
Async Webpage Fetcher with SSRF Verification, Size Protection, and Exponential Backoff.
"""

import random
from typing import Optional, Tuple
import asyncio
import httpx
from src.config.settings import settings
from src.utils.logger import logger
from src.scraper.security import validate_url_security, validate_content_type

BROWSER_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
]


def get_browser_headers(user_agent: Optional[str] = None) -> dict:
    ua = user_agent or random.choice(BROWSER_USER_AGENTS)
    return {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    }


class WebpageFetcher:
    def __init__(
        self,
        timeout: int = settings.SCRAPE_TIMEOUT_SECONDS,
        max_retries: int = settings.MAX_RETRIES,
        max_redirects: int = settings.MAX_REDIRECTS,
        max_size_mb: int = settings.MAX_RESPONSE_SIZE_MB,
        user_agent: str = settings.SCRAPER_USER_AGENT
    ):
        self.timeout = timeout
        self.max_retries = max_retries
        self.max_redirects = max_redirects
        self.max_bytes = max_size_mb * 1024 * 1024
        self.default_user_agent = user_agent

    async def fetch(self, url: str) -> Tuple[str, Optional[str]]:
        """
        Fetch webpage HTML content with:
        1. SSRF validation on initial URL and each redirect
        2. Exponential backoff retries on transient network errors and 403 blocks
        3. Response size limit enforcement
        4. Content-Type verification
        5. Rotating browser-like headers and User-Agent rotation on 403
        
        Returns:
            (html_content, error_message)
        """
        # Initial SSRF Security check
        is_safe, sec_err = validate_url_security(url)
        if not is_safe:
            return "", f"Security validation failed: {sec_err}"

        current_url = url
        redirect_count = 0

        async with httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=False,
            verify=False
        ) as client:
            for attempt in range(1, self.max_retries + 1):
                # Rotate browser headers for this attempt
                headers = get_browser_headers(self.default_user_agent if attempt == 1 else None)
                logger.debug(f"Attempt {attempt}/{self.max_retries} for {current_url} using User-Agent: {headers['User-Agent']}")

                try:
                    logger.info(f"Initiating HTTP GET request to {current_url} [Attempt {attempt}]")

                    response = await client.get(current_url, headers=headers)

                    logger.debug(f"Received response from {current_url}: status={response.status_code}, content_type={response.headers.get('Content-Type')}, content_length={response.headers.get('Content-Length')}")

                    # Handle manual redirects with SSRF check on target
                    while response.is_redirect:
                        redirect_count += 1
                        if redirect_count > self.max_redirects:
                            return "", f"Exceeded maximum redirect limit of {self.max_redirects}"

                        location = response.headers.get("Location")
                        if not location:
                            break

                        next_url = str(response.url.join(location))
                        logger.debug(f"Following redirect {redirect_count} to {next_url}")

                        # Validate next redirect target for SSRF
                        is_target_safe, target_sec_err = validate_url_security(next_url)
                        if not is_target_safe:
                            return "", f"Redirect to unsafe address '{next_url}' blocked: {target_sec_err}"

                        current_url = next_url
                        response = await client.get(current_url, headers=headers)
                        logger.debug(f"Redirect response: status={response.status_code}")

                    # Check Content-Type
                    content_type = response.headers.get("Content-Type", "")
                    is_valid_type, type_err = validate_content_type(content_type)
                    if not is_valid_type:
                        logger.warning(f"Invalid content type '{content_type}' for {current_url}: {type_err}")
                        return "", type_err

                    # Check Content-Length if present
                    content_length = response.headers.get("Content-Length")
                    if content_length and int(content_length) > self.max_bytes:
                        logger.warning(f"Response size {content_length} exceeds limit {self.max_bytes}")
                        return "", f"Response size ({content_length} bytes) exceeds limit of {self.max_bytes} bytes"

                    # Handle 403 Forbidden specifically by treating it as retryable with UA rotation
                    if response.status_code == 403:
                        logger.warning(f"Received HTTP 403 Forbidden for {current_url} on attempt {attempt}. Rotating User-Agent and retrying...")
                        if attempt < self.max_retries:
                            await asyncio.sleep(1.5 ** attempt)
                            continue
                        else:
                            return "", f"HTTP 403 Forbidden - Access denied after {self.max_retries} attempts"

                    response.raise_for_status()

                    raw_text = response.text
                    raw_bytes_len = len(raw_text.encode("utf-8"))
                    if raw_bytes_len > self.max_bytes:
                        logger.warning(f"Downloaded HTML size {raw_bytes_len} exceeds limit {self.max_bytes}")
                        return "", f"Downloaded HTML size exceeds maximum limit of {self.max_bytes} bytes"

                    logger.info(f"Successfully fetched {current_url} ({raw_bytes_len} bytes)")
                    return raw_text, None

                except httpx.HTTPStatusError as e:
                    status = e.response.status_code
                    if status in (401, 404, 410, 422):
                        # Non-retryable client errors (excluding 403)
                        logger.warning(f"Non-retryable HTTP error {status} for {current_url}: {e.response.reason_phrase}")
                        return "", f"HTTP {status} - {e.response.reason_phrase}"
                    logger.warning(f"Transient HTTP error {status} for {current_url} on attempt {attempt}: {e}")

                except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.NetworkError, httpx.ConnectError) as e:
                    logger.warning(f"Network error on attempt {attempt} for {current_url}: {e}")

                except Exception as e:
                    logger.error(f"Unexpected fetch error for {current_url}: {e}")
                    return "", str(e)

                # Exponential backoff before retry
                if attempt < self.max_retries:
                    backoff_delay = 1.5 ** attempt
                    logger.debug(f"Waiting {backoff_delay:.2f}s before retry attempt {attempt + 1}")
                    await asyncio.sleep(backoff_delay)

            return "", f"Failed to fetch {url} after {self.max_retries} attempts"
