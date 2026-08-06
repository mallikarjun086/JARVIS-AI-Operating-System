"""
Vector Storage Adapter interfacing with ChromaDB and high-performance embedding calculation.
Provides backward compatibility while delegating vector operations to EmbeddingEngine and ChromaVectorStore.
"""

import asyncio
import math
import re
from typing import List, Optional

from app.memory.embedding import embedding_engine
from app.memory.vector_store import chroma_store


class ChromaVectorAdapter:
    """
    Vector Store Adapter implementing embedding synthesis and cosine similarity calculation.
    Supports native ChromaDB integration and EmbeddingEngine delegation.
    """

    def __init__(self, dimension: int = 384) -> None:
        self.dimension = dimension

    def generate_embedding(self, text: str) -> List[float]:
        """
        Synchronous wrapper around EmbeddingEngine (fallback to hash if async loop not running).
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Loop is running, use fallback hash vector to avoid blocking
                return self._hash_embedding(text)
            return loop.run_until_complete(embedding_engine.embed(text))
        except Exception:
            return self._hash_embedding(text)

    async def generate_embedding_async(self, text: str) -> List[float]:
        """Generates real embedding using EmbeddingEngine."""
        return await embedding_engine.embed(text)

    def _hash_embedding(self, text: str) -> List[float]:
        """Fallback normalized float vector embedding."""
        vec = [0.0] * self.dimension
        words = re.findall(r"\w+", text.lower())
        for idx, word in enumerate(words):
            word_hash = abs(hash(word))
            dim_idx = word_hash % self.dimension
            vec[dim_idx] += 1.0 + (idx * 0.05)

        norm = math.sqrt(sum(val * val for val in vec)) or 1.0
        return [round(val / norm, 6) for val in vec]

    def compute_cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """Calculates cosine similarity between two float vectors."""
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))

        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0

        return round(max(0.0, min(1.0, dot_product / (norm_a * norm_b))), 4)


vector_adapter = ChromaVectorAdapter()
