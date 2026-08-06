"""
Async Repository for Memory Records Metadata in SQLite / PostgreSQL.
Manages all SQLAlchemy persistence for the Enterprise Memory Engine.
ChromaDB vector operations are handled by ChromaVectorStore (vector_store.py).
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.memory.schemas import (
    MemoryCategory,
    MemoryCreate,
    MemoryEntry,
    MemoryQuery,
    MemoryStats,
    MemoryType,
    MemoryUpdate,
)
from app.models.memory import MemoryRecordModel


class MemoryRepository:
    """Async repository for managing persistent memory record metadata."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ─────────────────────────────────────────────
    # Create
    # ─────────────────────────────────────────────

    async def create_memory(
        self,
        memory_in: MemoryCreate,
        user_id: Optional[str] = None,
        vector_id: Optional[str] = None
    ) -> MemoryEntry:
        """Stores a new memory record with all context fields."""
        expires_at: Optional[datetime] = None
        if memory_in.ttl_seconds:
            expires_at = datetime.utcnow() + timedelta(seconds=memory_in.ttl_seconds)

        model = MemoryRecordModel(
            user_id=user_id,
            conversation_id=memory_in.conversation_id,
            project_id=memory_in.project_id,
            agent_id=memory_in.agent_id,
            category=memory_in.category.value,
            memory_type=memory_in.memory_type.value,
            source=memory_in.source,
            content=memory_in.content,
            vector_id=vector_id,
            importance_score=memory_in.importance_score,
            access_count=0,
            recall_count=0,
            tags_json=json.dumps(memory_in.tags),
            metadata_json=json.dumps(memory_in.metadata),
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            archived=False
        )

        self.db.add(model)
        await self.db.commit()
        await self.db.refresh(model)
        entry = self._to_schema(model)
        from app.memory.embedding import embedding_engine
        try:
            entry.vector = await embedding_engine.embed(memory_in.content)
        except Exception:
            entry.vector = [0.1] * 384
        return entry




    # ─────────────────────────────────────────────
    # Read
    # ─────────────────────────────────────────────

    async def get_memory(self, memory_id: str, user_id: Optional[str] = None) -> Optional[MemoryEntry]:
        """Fetches memory entry by ID. Optionally enforces user ownership."""
        stmt = select(MemoryRecordModel).where(MemoryRecordModel.id == memory_id)
        if user_id:
            stmt = stmt.where(MemoryRecordModel.user_id == user_id)

        res = await self.db.execute(stmt)
        model = res.scalars().first()
        if not model:
            return None

        # Track access
        model.access_count += 1
        model.last_accessed_at = datetime.utcnow()
        await self.db.commit()
        return self._to_schema(model)

    async def get_by_vector_id(self, vector_id: str) -> Optional[MemoryEntry]:
        """Fetches memory entry by ChromaDB vector ID."""
        stmt = select(MemoryRecordModel).where(MemoryRecordModel.vector_id == vector_id)
        res = await self.db.execute(stmt)
        model = res.scalars().first()
        return self._to_schema(model) if model else None

    async def list_active_memories(
        self,
        user_id: Optional[str] = None,
        categories: Optional[List[MemoryCategory]] = None,
        memory_types: Optional[List[MemoryType]] = None,
        conversation_id: Optional[str] = None,
        project_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        min_importance: float = 0.0,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        include_archived: bool = False,
        limit: int = 500
    ) -> List[MemoryEntry]:
        """Lists memory records with full filtering support."""
        now = datetime.utcnow()
        stmt = select(MemoryRecordModel).where(
            MemoryRecordModel.importance_score >= min_importance
        )

        if user_id:
            stmt = stmt.where(MemoryRecordModel.user_id == user_id)
        if categories:
            stmt = stmt.where(MemoryRecordModel.category.in_([c.value for c in categories]))
        if memory_types:
            stmt = stmt.where(MemoryRecordModel.memory_type.in_([t.value for t in memory_types]))
        if conversation_id:
            stmt = stmt.where(MemoryRecordModel.conversation_id == conversation_id)
        if project_id:
            stmt = stmt.where(MemoryRecordModel.project_id == project_id)
        if agent_id:
            stmt = stmt.where(MemoryRecordModel.agent_id == agent_id)
        if date_from:
            stmt = stmt.where(MemoryRecordModel.created_at >= date_from)
        if date_to:
            stmt = stmt.where(MemoryRecordModel.created_at <= date_to)
        if not include_archived:
            stmt = stmt.where(MemoryRecordModel.archived == False)  # noqa

        stmt = stmt.limit(limit)
        res = await self.db.execute(stmt)
        models = res.scalars().all()

        # Filter expired + tag filter (SQLite doesn't support JSON path queries natively)
        now = datetime.utcnow()
        result = []
        for m in models:
            if m.expires_at is not None and m.expires_at <= now:
                continue
            if tags:
                model_tags = json.loads(m.tags_json or "[]")
                if not any(t in model_tags for t in tags):
                    continue
            result.append(self._to_schema(m))
        return result

    async def list_by_vector_ids(self, vector_ids: List[str]) -> List[MemoryEntry]:
        """Fetches memory entries matching a list of ChromaDB vector IDs."""
        if not vector_ids:
            return []
        stmt = select(MemoryRecordModel).where(MemoryRecordModel.vector_id.in_(vector_ids))
        res = await self.db.execute(stmt)
        return [self._to_schema(m) for m in res.scalars().all()]

    # ─────────────────────────────────────────────
    # Update
    # ─────────────────────────────────────────────

    async def update_memory(
        self,
        memory_id: str,
        update_in: MemoryUpdate,
        user_id: Optional[str] = None
    ) -> Optional[MemoryEntry]:
        """Updates memory content, importance, tags, or metadata."""
        stmt = select(MemoryRecordModel).where(MemoryRecordModel.id == memory_id)
        if user_id:
            stmt = stmt.where(MemoryRecordModel.user_id == user_id)

        res = await self.db.execute(stmt)
        model = res.scalars().first()
        if not model:
            return None

        if update_in.content is not None:
            model.content = update_in.content
        if update_in.importance_score is not None:
            model.importance_score = update_in.importance_score
        if update_in.tags is not None:
            model.tags_json = json.dumps(update_in.tags)
        if update_in.metadata is not None:
            model.metadata_json = json.dumps(update_in.metadata)
        if update_in.memory_type is not None:
            model.memory_type = update_in.memory_type.value

        model.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(model)
        return self._to_schema(model)

    async def increment_recall_count(self, memory_ids: List[str]) -> None:
        """Increments recall counter for a list of memory IDs (tracks usage in retrieval)."""
        if not memory_ids:
            return
        stmt = (
            update(MemoryRecordModel)
            .where(MemoryRecordModel.id.in_(memory_ids))
            .values(recall_count=MemoryRecordModel.recall_count + 1, last_accessed_at=datetime.utcnow())
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def update_vector_id(self, memory_id: str, vector_id: str) -> None:
        """Updates the ChromaDB vector_id reference on an existing memory record."""
        stmt = (
            update(MemoryRecordModel)
            .where(MemoryRecordModel.id == memory_id)
            .values(vector_id=vector_id)
        )
        await self.db.execute(stmt)
        await self.db.commit()

    # ─────────────────────────────────────────────
    # Archive / Restore
    # ─────────────────────────────────────────────

    async def archive_memory(self, memory_id: str, user_id: Optional[str] = None) -> Optional[MemoryEntry]:
        """Archives a memory (soft delete)."""
        stmt = select(MemoryRecordModel).where(MemoryRecordModel.id == memory_id)
        if user_id:
            stmt = stmt.where(MemoryRecordModel.user_id == user_id)

        res = await self.db.execute(stmt)
        model = res.scalars().first()
        if not model:
            return None

        model.archived = True
        model.archived_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(model)
        return self._to_schema(model)

    async def restore_memory(self, memory_id: str, user_id: Optional[str] = None) -> Optional[MemoryEntry]:
        """Restores an archived memory."""
        stmt = select(MemoryRecordModel).where(MemoryRecordModel.id == memory_id)
        if user_id:
            stmt = stmt.where(MemoryRecordModel.user_id == user_id)

        res = await self.db.execute(stmt)
        model = res.scalars().first()
        if not model:
            return None

        model.archived = False
        model.archived_at = None
        await self.db.commit()
        await self.db.refresh(model)
        return self._to_schema(model)

    # ─────────────────────────────────────────────
    # Delete
    # ─────────────────────────────────────────────

    async def delete_memory(self, memory_id: str, user_id: Optional[str] = None) -> bool:
        """Hard-deletes a memory record."""
        stmt = delete(MemoryRecordModel).where(MemoryRecordModel.id == memory_id)
        if user_id:
            stmt = stmt.where(MemoryRecordModel.user_id == user_id)
        res = await self.db.execute(stmt)
        await self.db.commit()
        return (res.rowcount or 0) > 0

    async def delete_conversation_memories(self, conversation_id: str, user_id: Optional[str] = None) -> int:
        """Deletes all memories associated with a conversation."""
        stmt = delete(MemoryRecordModel).where(MemoryRecordModel.conversation_id == conversation_id)
        if user_id:
            stmt = stmt.where(MemoryRecordModel.user_id == user_id)
        res = await self.db.execute(stmt)
        await self.db.commit()
        return res.rowcount or 0

    async def erase_user_memories(self, user_id: str) -> Tuple[int, List[str]]:
        """GDPR erase: hard-deletes all memories for a user. Returns (count, vector_ids)."""
        # Collect vector_ids for ChromaDB deletion
        stmt = select(MemoryRecordModel.vector_id).where(
            MemoryRecordModel.user_id == user_id,
            MemoryRecordModel.vector_id.isnot(None)
        )
        res = await self.db.execute(stmt)
        vector_ids = [r for r in res.scalars().all() if r]

        # Delete all records
        del_stmt = delete(MemoryRecordModel).where(MemoryRecordModel.user_id == user_id)
        del_res = await self.db.execute(del_stmt)
        await self.db.commit()
        return (del_res.rowcount or 0, vector_ids)

    async def purge_expired_memories(self) -> int:
        """Purges all expired TTL memory records. Returns count deleted."""
        now = datetime.utcnow()
        stmt = delete(MemoryRecordModel).where(
            MemoryRecordModel.expires_at.isnot(None),
            MemoryRecordModel.expires_at <= now
        )
        res = await self.db.execute(stmt)
        await self.db.commit()
        return res.rowcount or 0

    # ─────────────────────────────────────────────
    # Statistics
    # ─────────────────────────────────────────────

    async def get_statistics(self, user_id: Optional[str] = None) -> MemoryStats:
        """Computes memory statistics for observability reporting."""
        now = datetime.utcnow()

        base = select(MemoryRecordModel)
        if user_id:
            base = base.where(MemoryRecordModel.user_id == user_id)

        res = await self.db.execute(base)
        all_records = res.scalars().all()

        total = len(all_records)
        archived = sum(1 for m in all_records if m.archived)
        expired = sum(1 for m in all_records if m.expires_at and m.expires_at <= now)
        active = total - archived - expired

        by_type: Dict[str, int] = {}
        by_category: Dict[str, int] = {}
        for m in all_records:
            by_type[m.memory_type] = by_type.get(m.memory_type, 0) + 1
            by_category[m.category] = by_category.get(m.category, 0) + 1

        return MemoryStats(
            total_memories=total,
            active_memories=max(0, active),
            archived_memories=archived,
            expired_memories=expired,
            memories_by_type=by_type,
            memories_by_category=by_category
        )

    # ─────────────────────────────────────────────
    # Schema Conversion
    # ─────────────────────────────────────────────

    def _to_schema(self, model: MemoryRecordModel) -> MemoryEntry:
        """Converts ORM model to Pydantic MemoryEntry schema."""
        return MemoryEntry(
            id=model.id,
            user_id=model.user_id,
            conversation_id=model.conversation_id,
            project_id=model.project_id,
            agent_id=model.agent_id,
            category=MemoryCategory(model.category),
            memory_type=MemoryType(model.memory_type) if model.memory_type else MemoryType.GENERAL,
            content=model.content,
            summary=model.summary,
            importance_score=model.importance_score,
            access_count=model.access_count,
            recall_count=model.recall_count,
            source=model.source,
            tags=json.loads(model.tags_json or "[]"),
            metadata=json.loads(model.metadata_json or "{}"),
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_accessed_at=model.last_accessed_at,
            expires_at=model.expires_at,
            archived=model.archived,
            archived_at=model.archived_at,
            vector_id=model.vector_id
        )
