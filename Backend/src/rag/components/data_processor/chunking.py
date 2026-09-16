"""
Recursive Text Chunking Engine.
Splits text intelligently along document hierarchy boundaries while preserving
context, token boundaries, and rich source metadata.
"""

from typing import List, Optional
import tiktoken
from src.models.domain import Chunk, Source
from src.utils.hashing import generate_uuid
from src.config.settings import settings
from src.utils.logger import logger


class RecursiveChunkingEngine:
    def __init__(
        self,
        chunk_size: int = settings.CHUNK_SIZE,
        chunk_overlap: int = settings.CHUNK_OVERLAP,
        encoding_name: str = "cl100k_base",
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        try:
            self.tokenizer = tiktoken.get_encoding(encoding_name)
        except Exception:
            self.tokenizer = None
            logger.warning(f"Could not load tiktoken encoding '{encoding_name}', falling back to char-based estimation")

        # Hierarchical separators for recursive splitting
        self.separators = [
            "\n\n# ",
            "\n\n## ",
            "\n\n### ",
            "\n\n",
            "\n",
            ". ",
            "? ",
            "! ",
            "; ",
            ", ",
            " ",
            "",
        ]

    def count_tokens(self, text: str) -> int:
        """Calculate token count of text."""
        if self.tokenizer:
            try:
                return len(self.tokenizer.encode(text))
            except Exception:
                pass
        # Heuristic fallback: ~4 characters per token
        return max(1, len(text) // 4)

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        """Recursively split text using hierarchy of separators."""
        final_chunks: List[str] = []
        separator = separators[-1]
        new_separators = []

        for i, sep in enumerate(separators):
            if sep == "":
                separator = ""
                break
            if sep in text:
                separator = sep
                new_separators = separators[i + 1:]
                break

        splits = text.split(separator) if separator else list(text)
        good_splits: List[str] = []

        for s in splits:
            if not s:
                continue
            if len(s) < self.chunk_size:
                good_splits.append(s)
            else:
                if new_separators:
                    sub_splits = self._split_text(s, new_separators)
                    good_splits.extend(sub_splits)
                else:
                    good_splits.append(s)

        # Merge pieces into chunks that fit chunk_size with chunk_overlap
        merged_chunks: List[str] = []
        current_chunk: List[str] = []
        current_len = 0

        for piece in good_splits:
            piece_len = len(piece) + len(separator)
            if current_len + piece_len > self.chunk_size and current_chunk:
                merged_text = separator.join(current_chunk).strip()
                if merged_text:
                    merged_chunks.append(merged_text)

                # Keep overlap items from the end of current_chunk
                overlap_items = []
                overlap_len = 0
                for item in reversed(current_chunk):
                    if overlap_len + len(item) <= self.chunk_overlap:
                        overlap_items.insert(0, item)
                        overlap_len += len(item)
                    else:
                        break
                current_chunk = overlap_items
                current_len = overlap_len

            current_chunk.append(piece)
            current_len += piece_len

        if current_chunk:
            final_text = separator.join(current_chunk).strip()
            if final_text:
                merged_chunks.append(final_text)

        return merged_chunks

    def chunk_source(self, source: Source, clean_text: str) -> List[Chunk]:
        """Split cleaned source text into structured, metadata-rich chunks."""
        if not clean_text or not clean_text.strip():
            return []

        raw_pieces = self._split_text(clean_text, self.separators)
        chunks: List[Chunk] = []

        for idx, piece in enumerate(raw_pieces):
            piece_clean = piece.strip()
            if not piece_clean:
                continue

            chunk_id = f"{source.source_id}_chunk_{idx}"
            token_count = self.count_tokens(piece_clean)

            chunk = Chunk(
                chunk_id=chunk_id,
                source_id=source.source_id,
                url=source.url,
                title=source.title,
                chunk_index=idx,
                content=piece_clean,
                token_count=token_count,
                metadata={
                    "domain": source.domain,
                    "date_added": source.date_added.isoformat(),
                    "source_title": source.title,
                }
            )
            chunks.append(chunk)

        logger.info(f"Generated {len(chunks)} chunks for source: {source.url} ({source.title})")
        return chunks
