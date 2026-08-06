"""
Vector Memory Engine Implementation using NumPy.
Provides vector similarity search, cosine distance calculation, and file persistence.
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np
from jarvis.config import settings
from jarvis.domain.entities import MemoryRecord
from jarvis.domain.exceptions import VectorStoreError
from jarvis.domain.ports import LLMProviderPort, VectorStorePort
from jarvis.domain.value_objects import MemoryType
from jarvis.infrastructure.logging.logger import get_logger

logger = get_logger("jarvis.vector_store")


class VectorMemoryStore(VectorStorePort):
    """
    High-performance, async vector store using NumPy for vector matrix math.
    Calculates cosine similarity across memory records.
    """

    def __init__(
        self,
        llm_provider: LLMProviderPort,
        storage_path: Optional[Path] = None,
        dimension: Optional[int] = None
    ) -> None:
        self.llm_provider = llm_provider
        self.storage_path = storage_path or settings.VECTOR_STORE_PATH
        self.dimension = dimension or settings.VECTOR_DIMENSION
        self._memories: Dict[str, MemoryRecord] = {}
        self._lock = asyncio.Lock()

        # Load existing disk storage if available
        self._load_from_disk()

    async def add_memory(self, record: MemoryRecord) -> None:
        """Stores a memory record into in-memory storage and persists to disk."""
        if not record.vector:
            record.vector = await self.llm_provider.generate_embedding(record.content)

        async with self._lock:
            self._memories[record.id] = record
            self._save_to_disk()

        logger.info("Memory record indexed", memory_id=record.id, type=record.memory_type.value)

    async def search_memory(
        self,
        query: str,
        top_k: int = 5,
        min_similarity: float = 0.4
    ) -> List[MemoryRecord]:
        """Performs cosine vector similarity search for query string."""
        if not self._memories:
            return []

        query_vector = await self.llm_provider.generate_embedding(query)
        q_arr = np.array(query_vector, dtype=np.float32)
        q_norm = np.linalg.norm(q_arr)

        if q_norm == 0:
            return []

        async with self._lock:
            records = list(self._memories.values())

        scored_records = []
        for record in records:
            if not record.vector:
                continue
            r_arr = np.array(record.vector, dtype=np.float32)
            r_norm = np.linalg.norm(r_arr)
            if r_norm == 0:
                continue

            similarity = float(np.dot(q_arr, r_arr) / (q_norm * r_norm))
            if similarity >= min_similarity:
                scored_records.append((similarity * record.importance, record))

        # Sort by similarity score descending
        scored_records.sort(key=lambda x: x[0], reverse=True)
        return [rec for _, rec in scored_records[:top_k]]

    async def delete_memory(self, memory_id: str) -> bool:
        """Deletes a memory record by ID."""
        async with self._lock:
            if memory_id in self._memories:
                del self._memories[memory_id]
                self._save_to_disk()
                return True
        return False

    def _load_from_disk(self) -> None:
        """Loads serialized memory JSON records from disk."""
        if self.storage_path and os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        rec = MemoryRecord(
                            id=item["id"],
                            memory_type=MemoryType(item["memory_type"]),
                            content=item["content"],
                            vector=item.get("vector", []),
                            metadata=item.get("metadata", {}),
                            importance=item.get("importance", 1.0)
                        )
                        self._memories[rec.id] = rec
                logger.info("Vector store loaded from disk", count=len(self._memories))
            except Exception as e:
                logger.error("Failed to load vector store from disk", error=str(e))

    def _save_to_disk(self) -> None:
        """Persists memory records to disk in JSON format."""
        if not self.storage_path:
            return
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            data = [
                {
                    "id": rec.id,
                    "memory_type": rec.memory_type.value,
                    "content": rec.content,
                    "vector": rec.vector,
                    "metadata": rec.metadata,
                    "importance": rec.importance,
                    "timestamp": rec.timestamp.isoformat()
                }
                for rec in self._memories.values()
            ]
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error("Failed saving vector store to disk", error=str(e))
