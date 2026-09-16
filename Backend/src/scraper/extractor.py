"""
Multi-strategy Content Extraction Engine.
Combines Trafilatura (Strategy 1) and BeautifulSoup4 (Strategy 2)
with boilerplate removal, structural normalization, and metadata extraction.
"""

from typing import Dict, Any, Optional, Tuple
from bs4 import BeautifulSoup
import trafilatura
from src.config.settings import settings
from src.utils.logger import logger
from src.scraper.cleaner import remove_boilerplate, normalize_text
from src.scraper.metadata import extract_metadata, calculate_content_hash
from src.scraper.url_utils import extract_domain


class ExtractedDocument:
    def __init__(
        self,
        url: str,
        canonical_url: str,
        title: str,
        clean_text: str,
        domain: str,
        language: str,
        content_hash: str,
        word_count: int,
        character_count: int,
        metadata: Dict[str, Any],
        status: str = "EXTRACTED",
        error: Optional[str] = None
    ):
        self.url = url
        self.canonical_url = canonical_url
        self.title = title
        self.clean_text = clean_text
        self.domain = domain
        self.language = language
        self.content_hash = content_hash
        self.word_count = word_count
        self.character_count = character_count
        self.metadata = metadata
        self.status = status
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "canonical_url": self.canonical_url,
            "title": self.title,
            "clean_text": self.clean_text,
            "domain": self.domain,
            "language": self.language,
            "content_hash": self.content_hash,
            "word_count": self.word_count,
            "character_count": self.character_count,
            "metadata": self.metadata,
            "status": self.status,
            "error": self.error,
        }


class ContentExtractor:
    def __init__(self, min_content_length: int = settings.MIN_CONTENT_LENGTH):
        self.min_content_length = min_content_length

    def _extract_trafilatura(self, html: str, url: str) -> Optional[Tuple[str, str]]:
        """Strategy 1: Trafilatura article content extraction."""
        try:
            downloaded = trafilatura.extract(
                html,
                url=url,
                include_comments=False,
                include_tables=True,
                include_links=False,
                output_format="markdown",
                with_metadata=False
            )
            if downloaded and len(downloaded.strip()) >= self.min_content_length:
                metadata = trafilatura.extract_metadata(html, default_url=url)
                title = metadata.title if metadata and metadata.title else ""
                return title, downloaded
        except Exception as e:
            logger.debug(f"Trafilatura extraction failed for {url}: {e}")
        return None

    def _extract_beautifulsoup(self, html: str, url: str) -> Tuple[str, str]:
        """Strategy 2: Fallback BeautifulSoup semantic tag extraction with boilerplate removal."""
        soup = BeautifulSoup(html, "html.parser")
        soup = remove_boilerplate(soup)

        # 1. Title
        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        elif soup.find("h1"):
            title = soup.find("h1").get_text().strip()
        else:
            title = extract_domain(url)

        # 2. Main content container
        main_content = (
            soup.find("main") or
            soup.find("article") or
            soup.find("section") or
            soup.find("div", {"id": lambda x: x and "content" in str(x).lower()}) or
            soup.find("div", {"class": lambda x: x and "content" in str(x).lower()}) or
            soup.body or
            soup
        )

        # 3. Preserving document structure (Headings, Paragraphs, Lists, Blockquotes, Tables)
        lines = []
        for element in main_content.find_all(
            ["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "blockquote", "table", "code", "pre"]
        ):
            text = element.get_text().strip()
            if not text:
                continue

            tag = element.name.lower()
            if tag == "h1":
                lines.append(f"\n# {text}\n")
            elif tag == "h2":
                lines.append(f"\n## {text}\n")
            elif tag == "h3":
                lines.append(f"\n### {text}\n")
            elif tag in ("h4", "h5", "h6"):
                lines.append(f"\n#### {text}\n")
            elif tag == "li":
                lines.append(f"- {text}")
            elif tag == "blockquote":
                lines.append(f"> {text}")
            elif tag == "table":
                lines.append(f"\n{text}\n")
            else:
                lines.append(text)

        extracted_text = "\n\n".join(lines).strip()
        if not extracted_text:
            extracted_text = soup.get_text(separator="\n", strip=True)

        return title, extracted_text

    def extract(self, html: str, url: str) -> ExtractedDocument:
        """
        Execute layered content extraction, text normalization, and metadata compilation.
        """
        domain = extract_domain(url)
        if "maps.google" in domain or "google.com/maps" in url.lower() or "maps.app.goo.gl" in url.lower() or "goo.gl/maps" in url.lower():
            from urllib.parse import unquote, urlparse, parse_qs
            parsed = urlparse(url)
            path = parsed.path
            query_params = parse_qs(parsed.query)
            place_name = ""
            coords = ""
            if "/place/" in path:
                parts = path.split("/place/")[1].split("/")
                if parts:
                    place_name = unquote(parts[0]).replace("+", " ")
                for p in parts:
                    if p.startswith("@") and "," in p:
                        coords = ", ".join(p.lstrip("@").split(",")[:2])
            elif "/search/" in path:
                parts = path.split("/search/")[1].split("/")
                if parts:
                    place_name = unquote(parts[0]).replace("+", " ")
            if not place_name and "q" in query_params:
                place_name = unquote(query_params["q"][0]).replace("+", " ")
            if not place_name or place_name.lower() in ("google maps", "maps", "search"):
                place_name = "Google Maps Location"

            final_title = f"Google Maps: {place_name}"
            clean_text = f"# {final_title}\n- Place Name / Address: {place_name}"
            if coords:
                clean_text += f"\n- Coordinates: {coords}"
            clean_text += f"\n- Source Link: {url}\n\nThis knowledge source represents an interactive Google Maps location for '{place_name}'."

            return ExtractedDocument(
                url=url,
                canonical_url=url,
                title=final_title,
                clean_text=clean_text,
                domain=domain,
                language="en",
                content_hash=calculate_content_hash(clean_text),
                word_count=len(clean_text.split()),
                character_count=len(clean_text),
                metadata={"extractor_strategy": "google_maps_parser", "place_name": place_name, "coordinates": coords},
                status="EXTRACTED"
            )

        if not html or not html.strip():
            return ExtractedDocument(
                url=url,
                canonical_url=url,
                title="",
                clean_text="",
                domain=extract_domain(url),
                language="en",
                content_hash="",
                word_count=0,
                character_count=0,
                metadata={},
                status="FAILED_EXTRACTION",
                error="Empty HTML response received from webpage"
            )

        # 1. Try Strategy 1 (Trafilatura)
        strategy = "trafilatura"
        result = self._extract_trafilatura(html, url)

        if result:
            title, raw_text = result
        else:
            # 2. Try Strategy 2 (BeautifulSoup)
            strategy = "beautifulsoup4"
            title, raw_text = self._extract_beautifulsoup(html, url)

        # 3. Clean and normalize text
        clean_text = normalize_text(raw_text)

        # 4. Strategy 3 check: Minimum content length
        if len(clean_text) < self.min_content_length:
            return ExtractedDocument(
                url=url,
                canonical_url=url,
                title=title or extract_domain(url),
                clean_text="",
                domain=extract_domain(url),
                language="en",
                content_hash="",
                word_count=0,
                character_count=0,
                metadata={"strategy": strategy},
                status="FAILED_EXTRACTION",
                error=f"Extracted content length ({len(clean_text)} chars) is below minimum threshold ({self.min_content_length} chars)"
            )

        # 5. Extract rich metadata
        meta = extract_metadata(html, url, clean_text)
        meta["extractor_strategy"] = strategy

        final_title = title or meta.get("title") or extract_domain(url)

        return ExtractedDocument(
            url=url,
            canonical_url=meta.get("canonical_url", url),
            title=final_title,
            clean_text=clean_text,
            domain=meta.get("domain", extract_domain(url)),
            language=meta.get("language", "en"),
            content_hash=meta.get("content_hash", calculate_content_hash(clean_text)),
            word_count=meta.get("word_count", len(clean_text.split())),
            character_count=meta.get("character_count", len(clean_text)),
            metadata=meta,
            status="EXTRACTED"
        )
