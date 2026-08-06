"""
Enterprise Embedding Engine for the Memory & Knowledge Subsystem.
Supports OpenAI Embeddings API and Sentence Transformers (offline) with:
- LRU-based in-memory embedding cache
- Batch processing
- Async execution with thread pool for sync SDKs
- Dimension validation
- Retry logic
- Graceful offline fallback
"""

import asyncio
import hashlib
import math
import re
import time
from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import List, Optional, Tuple

from app.config import settings
from app.core.logging import logger


# ─────────────────────────────────────────────────
# Base Protocol
# ─────────────────────────────────────────────────

class BaseEmbeddingProvider(ABC):
    """Abstract interface all embedding providers must implement."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        pass

    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """Generates a single embedding vector for the given text."""
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generates embeddings for a list of texts in one batch call."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        pass


# ─────────────────────────────────────────────────
# OpenAI Embedding Provider
# ─────────────────────────────────────────────────

class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """
    OpenAI Embeddings API using the official openai SDK.
    Supports text-embedding-3-small (1536d) and text-embedding-3-large (3072d).
    """

    def __init__(self, model: Optional[str] = None) -> None:
        self._model = model or settings.OPENAI_EMBEDDING_MODEL
        self._client = None
        self._dim: Optional[int] = None

    @property
    def provider_name(self) -> str:
        return "OpenAIEmbeddings"

    @property
    def dimension(self) -> int:
        if self._dim is not None:
            return self._dim
        # Known dimensions
        if "3-small" in self._model:
            return 1536
        if "3-large" in self._model:
            return 3072
        if "ada" in self._model:
            return 1536
        return 1536

    def _get_client(self):
        if self._client is None:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(
                    api_key=settings.OPENAI_API_KEY,
                    timeout=30.0,
                    max_retries=2
                )
            except Exception as e:
                logger.warning("OpenAI embedding client init failed", error=str(e))
                self._client = False
        return self._client if self._client is not False else None

    async def health_check(self) -> bool:
        if not settings.OPENAI_API_KEY:
            return False
        client = self._get_client()
        if client is None:
            return False
        try:
            await self.embed("health check")
            return True
        except Exception:
            return False

    async def embed(self, text: str) -> List[float]:
        client = self._get_client()
        if client is None or not settings.OPENAI_API_KEY:
            raise RuntimeError("OpenAI embedding client unavailable")
        resp = await client.embeddings.create(input=text, model=self._model)
        vec = resp.data[0].embedding
        self._dim = len(vec)
        return vec

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        client = self._get_client()
        if client is None or not settings.OPENAI_API_KEY:
            raise RuntimeError("OpenAI embedding client unavailable")
        resp = await client.embeddings.create(input=texts, model=self._model)
        # Sort by index to preserve order
        sorted_data = sorted(resp.data, key=lambda d: d.index)
        return [d.embedding for d in sorted_data]


# ─────────────────────────────────────────────────
# Sentence Transformer Provider (Offline)
# ─────────────────────────────────────────────────

# Module-level cached model (loaded once per process)
_st_model = None
_st_model_name: Optional[str] = None


def _get_st_model(model_name: str):
    """Returns cached SentenceTransformer model (thread-safe via GIL)."""
    global _st_model, _st_model_name
    if _st_model is None or _st_model_name != model_name:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading SentenceTransformer model...", model=model_name)
            _st_model = SentenceTransformer(model_name)
            _st_model_name = model_name
            logger.info("SentenceTransformer model loaded", model=model_name)
        except Exception as e:
            logger.warning("SentenceTransformer load failed", model=model_name, error=str(e))
            _st_model = False
    return _st_model if _st_model is not False else None


class SentenceTransformerProvider(BaseEmbeddingProvider):
    """
    Offline embedding provider using sentence-transformers.
    Default model: all-MiniLM-L6-v2 (384 dimensions, ~80MB).
    """

    def __init__(self, model_name: Optional[str] = None) -> None:
        self._model_name = model_name or settings.SENTENCE_TRANSFORMER_MODEL

    @property
    def provider_name(self) -> str:
        return "SentenceTransformer"

    @property
    def dimension(self) -> int:
        # all-MiniLM-L6-v2 → 384; all-mpnet-base-v2 → 768
        if "MiniLM" in self._model_name:
            return 384
        if "mpnet" in self._model_name:
            return 768
        return settings.EMBEDDING_DIMENSION

    async def health_check(self) -> bool:
        model = _get_st_model(self._model_name)
        return model is not None

    async def embed(self, text: str) -> List[float]:
        return (await self.embed_batch([text]))[0]

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        model = _get_st_model(self._model_name)
        if model is None:
            raise RuntimeError("SentenceTransformer model unavailable")
        # SentenceTransformer is synchronous — run in executor to avoid blocking event loop
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None,
            lambda: model.encode(texts, convert_to_numpy=False, show_progress_bar=False)
        )
        return [list(map(float, emb)) for emb in embeddings]


# ─────────────────────────────────────────────────
# Fallback Hash Provider (last resort)
# ─────────────────────────────────────────────────

class HashEmbeddingProvider(BaseEmbeddingProvider):
    """
    Deterministic hash-based embedding — used only when all real providers fail.
    NOT suitable for semantic search. Produces stable vectors for testing only.
    """

    @property
    def provider_name(self) -> str:
        return "HashEmbedding"

    @property
    def dimension(self) -> int:
        return settings.EMBEDDING_DIMENSION

    async def health_check(self) -> bool:
        return True

    async def embed(self, text: str) -> List[float]:
        dim = self.dimension
        vec = [0.0] * dim
        words = re.findall(r"\w+", text.lower())
        for idx, word in enumerate(words):
            wh = abs(int(hashlib.md5(word.encode()).hexdigest(), 16))
            dim_idx = wh % dim
            vec[dim_idx] += 1.0 + (idx * 0.05)
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [round(v / norm, 6) for v in vec]

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [await self.embed(t) for t in texts]


# ─────────────────────────────────────────────────
# LRU Embedding Cache
# ─────────────────────────────────────────────────

class EmbeddingCache:
    """Thread-safe LRU cache for embedding vectors keyed by content hash."""

    def __init__(self, max_size: int = 1000) -> None:
        self._cache: OrderedDict[str, List[float]] = OrderedDict()
        self._max_size = max_size
        self._hits = 0
        self._misses = 0

    def _key(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def get(self, text: str) -> Optional[List[float]]:
        key = self._key(text)
        if key in self._cache:
            self._cache.move_to_end(key)
            self._hits += 1
            return self._cache[key]
        self._misses += 1
        return None

    def put(self, text: str, vector: List[float]) -> None:
        key = self._key(text)
        self._cache[key] = vector
        self._cache.move_to_end(key)
        if len(self._cache) > self._max_size:
            self._cache.popitem(last=False)

    @property
    def hit_rate(self) -> float:
        total = self._hits + self._misses
        return round(self._hits / total, 4) if total > 0 else 0.0

    @property
    def stats(self) -> dict:
        return {"hits": self._hits, "misses": self._misses, "hit_rate": self.hit_rate, "size": len(self._cache)}


# ─────────────────────────────────────────────────
# Embedding Engine (Orchestrator)
# ─────────────────────────────────────────────────

class EmbeddingEngine:
    """
    Orchestrates embedding generation with:
    - LRU cache (no duplicate embeddings)
    - Primary provider selection (OpenAI or SentenceTransformer)
    - Automatic fallback to SentenceTransformer → Hash
    - Batch processing
    - Dimension validation
    - Retry with exponential backoff
    """

    def __init__(self) -> None:
        self._cache = EmbeddingCache(max_size=settings.EMBEDDING_CACHE_SIZE)
        self._primary: Optional[BaseEmbeddingProvider] = None
        self._fallback: Optional[BaseEmbeddingProvider] = None
        self._hash_provider = HashEmbeddingProvider()
        self._total_embeddings = 0
        self._total_latency_ms = 0.0
        self._initialized = False

    def _build_providers(self) -> Tuple[BaseEmbeddingProvider, BaseEmbeddingProvider]:
        """Selects primary and fallback providers based on configuration."""
        if settings.EMBEDDING_PROVIDER == "openai" and settings.OPENAI_API_KEY:
            return OpenAIEmbeddingProvider(), SentenceTransformerProvider()
        return SentenceTransformerProvider(), self._hash_provider

    async def initialize(self) -> bool:
        """Initializes providers and warms up the primary embedding model."""
        if self._initialized:
            return True
        self._primary, self._fallback = self._build_providers()

        primary_ok = await self._primary.health_check()
        if primary_ok:
            logger.info(
                "EmbeddingEngine initialized",
                provider=self._primary.provider_name,
                dimension=self._primary.dimension
            )
        else:
            logger.warning(
                "Primary embedding provider unhealthy, using fallback",
                primary=self._primary.provider_name,
                fallback=self._fallback.provider_name
            )

        self._initialized = True
        return primary_ok

    async def embed(self, text: str) -> List[float]:
        """Generates embedding with cache, retry, and provider fallback."""
        if not text or not text.strip():
            return [0.0] * settings.EMBEDDING_DIMENSION

        # Check cache first
        cached = self._cache.get(text)
        if cached is not None:
            return cached

        if not self._initialized:
            await self.initialize()

        start = time.time()
        vector = await self._embed_with_fallback(text)
        elapsed_ms = (time.time() - start) * 1000.0

        # Validate dimension
        expected_dim = self._active_provider.dimension
        if len(vector) != expected_dim:
            logger.warning(
                "Embedding dimension mismatch",
                expected=expected_dim,
                got=len(vector)
            )

        self._cache.put(text, vector)
        self._total_embeddings += 1
        self._total_latency_ms += elapsed_ms
        return vector

    async def _embed_with_fallback(self, text: str, max_retries: int = 2) -> List[float]:
        """Attempts embedding with primary provider, falls back on failure."""
        providers = [self._primary, self._fallback, self._hash_provider]
        for provider in providers:
            if provider is None:
                continue
            for attempt in range(1, max_retries + 1):
                try:
                    vec = await provider.embed(text)
                    self._active_provider = provider
                    return vec
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    if attempt < max_retries:
                        await asyncio.sleep(0.5 * attempt)
                    else:
                        logger.warning(
                            "Embedding provider failed, trying next",
                            provider=provider.provider_name,
                            error=str(e)
                        )
        # Absolute fallback — hash embedding
        self._active_provider = self._hash_provider
        return await self._hash_provider.embed(text)

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Batch embedding with cache for repeated texts."""
        if not self._initialized:
            await self.initialize()

        # Separate cached vs uncached
        results: List[Optional[List[float]]] = [None] * len(texts)
        uncached_indices: List[int] = []
        uncached_texts: List[str] = []

        for i, text in enumerate(texts):
            cached = self._cache.get(text)
            if cached is not None:
                results[i] = cached
            else:
                uncached_indices.append(i)
                uncached_texts.append(text)

        # Batch-embed uncached texts
        if uncached_texts:
            try:
                vectors = await self._primary.embed_batch(uncached_texts)
            except Exception:
                try:
                    vectors = await self._fallback.embed_batch(uncached_texts)
                except Exception:
                    vectors = await self._hash_provider.embed_batch(uncached_texts)

            for idx, vec in zip(uncached_indices, vectors):
                self._cache.put(texts[idx], vec)
                results[idx] = vec
                self._total_embeddings += 1

        return [r or [0.0] * settings.EMBEDDING_DIMENSION for r in results]

    @property
    def active_provider_name(self) -> str:
        if hasattr(self, "_active_provider") and self._active_provider:
            return self._active_provider.provider_name
        if self._primary:
            return self._primary.provider_name
        return "Unknown"

    @property
    def cache_stats(self) -> dict:
        return self._cache.stats

    @property
    def total_embeddings(self) -> int:
        return self._total_embeddings

    @property
    def avg_latency_ms(self) -> float:
        return round(self._total_latency_ms / max(1, self._total_embeddings), 2)


# Module-level singleton
embedding_engine = EmbeddingEngine()
