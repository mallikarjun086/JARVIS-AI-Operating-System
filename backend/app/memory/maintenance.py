"""
Memory Maintenance Engine: Conversation Compression & Expiration Garbage Collection.
Delegates heavy compression to MemoryCompressor and cleanup to MemoryRepository.
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.memory.compressor import memory_compressor
from app.memory.repository import MemoryRepository
from app.memory.schemas import MemoryEntry


class MemoryMaintenanceEngine:
    """Handles conversation memory compression and TTL expiration cleanup."""

    @classmethod
    async def compress_conversation(
        cls,
        db: AsyncSession,
        conversation_turns: List[str],
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        project_id: Optional[str] = None,
        importance_score: float = 0.8,
        model: Optional[str] = None
    ) -> MemoryEntry:
        """
        Compresses multiple conversation turns into a high-density
        semantic long-term memory record using MemoryCompressor.
        """
        return await memory_compressor.compress_conversation(
            db=db,
            conversation_turns=conversation_turns,
            user_id=user_id,
            conversation_id=conversation_id,
            project_id=project_id,
            importance_score=importance_score,
            model=model
        )

    @classmethod
    async def cleanup_expired_memories(cls, db: AsyncSession) -> int:
        """Executes garbage collection pass purging expired records."""
        repo = MemoryRepository(db)
        return await repo.purge_expired_memories()


maintenance_engine = MemoryMaintenanceEngine()
