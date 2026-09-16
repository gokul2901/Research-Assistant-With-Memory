"""
Embedding Providers and Service with Batching, In-Memory Caching, and Retry Handling.
Merges provider implementations and the embedding service into a single cohesive module.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
import litellm
from src.config.settings import settings
from src.utils.logger import logger
from src.utils.hashing import generate_content_hash


# =============================================================================
# Embedding Providers
# =============================================================================

class BaseEmbeddingProvider(ABC):
    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        pass

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        pass


class FastEmbedProvider(BaseEmbeddingProvider):
    """
    Local ONNX-based high speed embedding provider using FastEmbed.
    Runs locally with zero external API latency, no rate limits, and 384-dim embeddings.
    """
    def __init__(self, model_name: str = settings.EMBEDDING_MODEL):
        try:
            from fastembed import TextEmbedding
            self.model = TextEmbedding(model_name=model_name)
            logger.info(f"Initialized FastEmbed provider with model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load FastEmbed TextEmbedding: {e}")
            self.model = None

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        if self.model is None:
            # Fallback zero vector generator if model failed to load
            return [[0.0] * settings.EMBEDDING_DIMENSION for _ in texts]
        embeddings_generator = self.model.embed(texts)
        return [[float(x) for x in emb] for emb in embeddings_generator]

    def embed_query(self, text: str) -> List[float]:
        results = self.embed_texts([text])
        return results[0] if results else [0.0] * settings.EMBEDDING_DIMENSION


class LiteLLMEmbeddingProvider(BaseEmbeddingProvider):
    """
    Remote embedding provider via LiteLLM / OpenAI Embeddings API.
    """
    def __init__(self, model_name: str = "text-embedding-3-small", api_key: Optional[str] = None):
        self.model_name = model_name
        self.api_key = api_key or settings.OPENAI_API_KEY

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        try:
            response = litellm.embedding(
                model=self.model_name,
                input=texts,
                api_key=self.api_key
            )
            return [item["embedding"] for item in response["data"]]
        except Exception as e:
            logger.warning(f"LiteLLM embedding failed: {e}. Falling back to FastEmbed provider.")
            fallback = FastEmbedProvider()
            return fallback.embed_texts(texts)

    def embed_query(self, text: str) -> List[float]:
        results = self.embed_texts([text])
        return results[0] if results else [0.0] * 1536


# =============================================================================
# Embedding Service (Batching, Caching, Retry)
# =============================================================================

class EmbeddingService:
    def __init__(
        self,
        provider: str = settings.EMBEDDING_PROVIDER,
        batch_size: int = settings.EMBEDDING_BATCH_SIZE
    ):
        self.batch_size = batch_size
        self._cache: Dict[str, List[float]] = {}

        if provider == "openai" and settings.OPENAI_API_KEY:
            self.provider: BaseEmbeddingProvider = LiteLLMEmbeddingProvider(
                model_name="text-embedding-3-small",
                api_key=settings.OPENAI_API_KEY
            )
        else:
            self.provider = FastEmbedProvider()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def _embed_batch_with_retry(self, texts: List[str]) -> List[List[float]]:
        return self.provider.embed_texts(texts)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of texts using batching and hash-based caching."""
        if not texts:
            return []

        results: List[List[float]] = [[] for _ in texts]
        uncached_indices: List[int] = []
        uncached_texts: List[str] = []

        # 1. Check cache
        for idx, text in enumerate(texts):
            text_hash = generate_content_hash(text)
            if text_hash in self._cache:
                results[idx] = self._cache[text_hash]
            else:
                uncached_indices.append(idx)
                uncached_texts.append(text)

        # 2. Compute embeddings for uncached in batches
        if uncached_texts:
            logger.debug(f"Computing embeddings for {len(uncached_texts)} uncached texts (Batch size: {self.batch_size})")
            for i in range(0, len(uncached_texts), self.batch_size):
                batch = uncached_texts[i:i + self.batch_size]
                batch_embeddings = self._embed_batch_with_retry(batch)

                for sub_idx, emb in enumerate(batch_embeddings):
                    original_idx = uncached_indices[i + sub_idx]
                    results[original_idx] = emb
                    # Store in cache
                    text_hash = generate_content_hash(batch[sub_idx])
                    self._cache[text_hash] = emb

        return results

    def embed_query(self, query: str) -> List[float]:
        """Embed a search query."""
        query_hash = generate_content_hash(f"query:{query}")
        if query_hash in self._cache:
            return self._cache[query_hash]

        emb = self.provider.embed_query(query)
        self._cache[query_hash] = emb
        return emb

    def clear_cache(self) -> None:
        """Clear embedding cache."""
        self._cache.clear()
