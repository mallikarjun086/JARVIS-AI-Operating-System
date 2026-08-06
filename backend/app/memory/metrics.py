"""
Memory Engine Observability Metrics.
Tracks: memory count, embedding stats, vector search latency, recall latency,
compression count, archive count, storage size, and cache hit rate.
"""

import time
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class MemoryEngineMetrics:
    """Thread-safe (GIL-protected) metric counters for the Memory Engine."""

    # Counts
    total_memories_created: int = 0
    total_memories_deleted: int = 0
    total_memories_archived: int = 0
    total_embeddings_generated: int = 0
    total_compressions: int = 0
    total_searches: int = 0
    total_recalls: int = 0

    # Latency accumulators (ms)
    total_vector_search_ms: float = 0.0
    total_recall_latency_ms: float = 0.0
    total_embedding_latency_ms: float = 0.0

    # Cache stats
    embedding_cache_hits: int = 0
    embedding_cache_misses: int = 0

    # Breakdown
    memories_by_type: Dict[str, int] = field(default_factory=dict)
    memories_by_category: Dict[str, int] = field(default_factory=dict)

    def record_memory_created(self, memory_type: str, category: str) -> None:
        self.total_memories_created += 1
        self.memories_by_type[memory_type] = self.memories_by_type.get(memory_type, 0) + 1
        self.memories_by_category[category] = self.memories_by_category.get(category, 0) + 1

    def record_search(self, latency_ms: float) -> None:
        self.total_searches += 1
        self.total_vector_search_ms += latency_ms

    def record_recall(self, latency_ms: float) -> None:
        self.total_recalls += 1
        self.total_recall_latency_ms += latency_ms

    def record_embedding(self, latency_ms: float) -> None:
        self.total_embeddings_generated += 1
        self.total_embedding_latency_ms += latency_ms

    def record_compression(self) -> None:
        self.total_compressions += 1

    def record_archive(self) -> None:
        self.total_memories_archived += 1

    @property
    def avg_vector_search_ms(self) -> float:
        return round(self.total_vector_search_ms / max(1, self.total_searches), 2)

    @property
    def avg_recall_latency_ms(self) -> float:
        return round(self.total_recall_latency_ms / max(1, self.total_recalls), 2)

    @property
    def avg_embedding_latency_ms(self) -> float:
        return round(self.total_embedding_latency_ms / max(1, self.total_embeddings_generated), 2)

    @property
    def cache_hit_rate(self) -> float:
        total = self.embedding_cache_hits + self.embedding_cache_misses
        return round(self.embedding_cache_hits / total, 4) if total > 0 else 0.0

    def to_dict(self) -> dict:
        return {
            "total_memories_created": self.total_memories_created,
            "total_memories_deleted": self.total_memories_deleted,
            "total_memories_archived": self.total_memories_archived,
            "total_embeddings_generated": self.total_embeddings_generated,
            "total_compressions": self.total_compressions,
            "total_searches": self.total_searches,
            "total_recalls": self.total_recalls,
            "avg_vector_search_ms": self.avg_vector_search_ms,
            "avg_recall_latency_ms": self.avg_recall_latency_ms,
            "avg_embedding_latency_ms": self.avg_embedding_latency_ms,
            "cache_hit_rate": self.cache_hit_rate,
            "memories_by_type": self.memories_by_type,
            "memories_by_category": self.memories_by_category,
        }


# Module-level singleton
memory_metrics = MemoryEngineMetrics()
