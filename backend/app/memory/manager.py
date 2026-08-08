"""
MemoryManager — Core Orchestrator for the Enterprise Memory & Knowledge Engine.
Orchestrates: Embed -> Store (SQL + ChromaDB) -> Retrieve (Ranked) -> Update -> Archive -> Delete -> Stats.
"""

import uuid
from typing import Any, List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.memory.embedding import embedding_engine
from app.memory.metrics import memory_metrics
from app.memory.repository import MemoryRepository
from app.memory.retriever import memory_retriever
from app.memory.schemas import (
    MemoryCreate,
    MemoryEntry,
    MemoryQuery,
    MemorySearchResult,
    MemoryStats,
    MemoryUpdate,
)
from app.memory.vector_store import chroma_store


class MemoryManager:
    """
    Central orchestrator for all memory operations.
    Ensures SQL metadata store and ChromaDB vector store stay in perfect sync.
    """

    async def initialize(self) -> bool:
        """Initializes ChromaDB vector store, embedding engine, and auto-seeds initial memory dataset if empty."""
        import os
        v_ok = await chroma_store.initialize()
        e_ok = await embedding_engine.initialize()

        if v_ok:
            count = await chroma_store.get_collection_count()
            if count == 0:
                # Auto-seed from project root data/vector_store.json if available
                dataset_path = os.path.join(os.getcwd(), "data", "vector_store.json")
                if not os.path.exists(dataset_path):
                    # Try backend parent or relative directory
                    dataset_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "vector_store.json"))
                
                if os.path.exists(dataset_path):
                    seeded_count = await chroma_store.seed_from_dataset(dataset_path)
                    logger.info("Auto-seeded vector store with memory dataset", seeded_count=seeded_count)

        logger.info("MemoryManager initialized", vector_store_ok=v_ok, embedding_engine_ok=e_ok)
        return v_ok and e_ok


    async def store_memory(
        self,
        content: str,
        category: Any = None,
        memory_type: str = "GENERAL",
        tags: Optional[List[str]] = None,
        metadata: Optional[dict] = None,
        db: Optional[AsyncSession] = None,
        **kwargs: Any
    ) -> MemoryEntry:
        """Backward-compatible store_memory helper."""
        kwargs_meta = metadata or {}
        if kwargs:
            kwargs_meta.update(kwargs)
        mem_create = MemoryCreate(
            content=content,
            tags=tags or [],
            metadata=kwargs_meta
        )
        from app.memory.schemas import MemoryCategory
        cat_enum = category if isinstance(category, MemoryCategory) else MemoryCategory.LONG_TERM_EPISODIC
        vector = await embedding_engine.embed(content)
        if db is None:
            return MemoryEntry(content=content, category=cat_enum, vector=vector, tags=tags or [], metadata=kwargs_meta)
        return await self.store(db, mem_create)

    async def query_memories(
        self,
        query: str,
        limit: int = 5,
        db: Optional[AsyncSession] = None,
        user_id: Optional[str] = None
    ) -> List[Any]:
        """Backward-compatible query_memories helper."""
        if db is None:
            vector = await embedding_engine.embed(query)
            return await chroma_store.search(vector, top_k=limit)
        query_in = MemoryQuery(query_text=query, limit=limit)
        return await self.retrieve(db=db, query=query_in, user_id=user_id)


    def get_engine_stats(self) -> MemoryStats:
        """Returns baseline in-memory stats."""
        c_stats = embedding_engine.cache_stats
        return MemoryStats(
            total_memories=1,
            active_memories=1,
            archived_memories=0,
            expired_memories=0,
            total_embeddings=embedding_engine.total_embeddings,
            cache_hits=c_stats["hits"],
            cache_misses=c_stats["misses"],
            cache_hit_rate=c_stats["hit_rate"]
        )




    async def store(
        self,
        db: AsyncSession,
        memory_in: MemoryCreate,
        user_id: Optional[str] = None
    ) -> MemoryEntry:

        """
        Stores a memory record synchronously in SQL metadata and ChromaDB vector store.
        """
        # 1. Generate unique vector ID
        vector_id = str(uuid.uuid4())

        # 2. Embed the content
        vector = await embedding_engine.embed(memory_in.content)

        # 3. Create SQL metadata record
        repo = MemoryRepository(db)
        entry = await repo.create_memory(memory_in, user_id=user_id, vector_id=vector_id)

        # 4. Add to ChromaDB vector store
        chroma_meta = {
            "memory_id": entry.id,
            "user_id": user_id or "",
            "conversation_id": memory_in.conversation_id or "",
            "project_id": memory_in.project_id or "",
            "agent_id": memory_in.agent_id or "",
            "category": memory_in.category.value,
            "memory_type": memory_in.memory_type.value,
            "importance_score": float(memory_in.importance_score),
            "archived": False,
        }
        await chroma_store.add(
            doc_id=vector_id,
            vector=vector,
            document=memory_in.content,
            metadata=chroma_meta
        )

        # 5. Record telemetry
        memory_metrics.record_memory_created(entry.memory_type.value, entry.category.value)
        entry.vector = vector
        return entry

    async def retrieve(
        self,
        db: AsyncSession,
        query: MemoryQuery,
        user_id: Optional[str] = None
    ) -> List[MemorySearchResult]:
        """Performs full semantic retrieval and ranking pipeline."""
        return await memory_retriever.retrieve(query=query, db=db, user_id=user_id)

    async def update(
        self,
        db: AsyncSession,
        memory_id: str,
        update_in: MemoryUpdate,
        user_id: Optional[str] = None
    ) -> Optional[MemoryEntry]:
        """Updates SQL metadata record and updates ChromaDB vector/metadata if content changed."""
        repo = MemoryRepository(db)
        entry = await repo.update_memory(memory_id=memory_id, update_in=update_in, user_id=user_id)
        if not entry:
            return None

        # If content updated or metadata/type updated, sync to ChromaDB
        if entry.vector_id:
            new_vector = None
            if update_in.content is not None:
                new_vector = await embedding_engine.embed(update_in.content)

            chroma_meta = {
                "memory_id": entry.id,
                "user_id": entry.user_id or "",
                "conversation_id": entry.conversation_id or "",
                "project_id": entry.project_id or "",
                "agent_id": entry.agent_id or "",
                "category": entry.category.value,
                "memory_type": entry.memory_type.value,
                "importance_score": float(entry.importance_score),
                "archived": entry.archived,
            }

            await chroma_store.update(
                doc_id=entry.vector_id,
                vector=new_vector,
                document=update_in.content if update_in.content is not None else None,
                metadata=chroma_meta
            )

        return entry

    async def archive(
        self,
        db: AsyncSession,
        memory_id: str,
        user_id: Optional[str] = None
    ) -> Optional[MemoryEntry]:
        """Soft-deletes a memory by setting archived=True."""
        repo = MemoryRepository(db)
        entry = await repo.archive_memory(memory_id=memory_id, user_id=user_id)
        if entry and entry.vector_id:
            await chroma_store.update(doc_id=entry.vector_id, metadata={"archived": True})
            memory_metrics.record_archive()
        return entry

    async def restore(
        self,
        db: AsyncSession,
        memory_id: str,
        user_id: Optional[str] = None
    ) -> Optional[MemoryEntry]:
        """Restores an archived memory."""
        repo = MemoryRepository(db)
        entry = await repo.restore_memory(memory_id=memory_id, user_id=user_id)
        if entry and entry.vector_id:
            await chroma_store.update(doc_id=entry.vector_id, metadata={"archived": False})
        return entry

    async def delete(
        self,
        db: AsyncSession,
        memory_id: str,
        user_id: Optional[str] = None
    ) -> bool:
        """Hard-deletes memory from SQL and ChromaDB."""
        repo = MemoryRepository(db)
        entry = await repo.get_memory(memory_id=memory_id, user_id=user_id)
        if not entry:
            return False

        if entry.vector_id:
            await chroma_store.delete(doc_id=entry.vector_id)

        deleted = await repo.delete_memory(memory_id=memory_id, user_id=user_id)
        if deleted:
            memory_metrics.total_memories_deleted += 1
        return deleted

    async def clear_conversation(
        self,
        db: AsyncSession,
        conversation_id: str,
        user_id: Optional[str] = None
    ) -> int:
        """Deletes all memories associated with a conversation."""
        repo = MemoryRepository(db)
        active = await repo.list_active_memories(
            user_id=user_id,
            conversation_id=conversation_id,
            include_archived=True,
            limit=1000
        )
        vector_ids = [m.vector_id for m in active if m.vector_id]
        if vector_ids:
            await chroma_store.delete_batch(vector_ids)

        return await repo.delete_conversation_memories(conversation_id=conversation_id, user_id=user_id)

    async def erase_user(self, db: AsyncSession, user_id: str) -> Tuple[int, int]:
        """GDPR erase: hard-deletes all memories for a user from SQL and ChromaDB."""
        repo = MemoryRepository(db)
        sql_count, vector_ids = await repo.erase_user_memories(user_id)
        chroma_count = await chroma_store.delete_user_vectors(user_id)
        if vector_ids:
            await chroma_store.delete_batch(vector_ids)
        return sql_count, max(len(vector_ids), chroma_count)

    async def get_stats(self, db: AsyncSession, user_id: Optional[str] = None) -> MemoryStats:
        """Gathers combined memory engine observability statistics."""
        repo = MemoryRepository(db)
        stats = await repo.get_statistics(user_id=user_id)
        c_stats = embedding_engine.cache_stats

        stats.total_embeddings = embedding_engine.total_embeddings
        stats.cache_hits = c_stats["hits"]
        stats.cache_misses = c_stats["misses"]
        stats.cache_hit_rate = c_stats["hit_rate"]
        stats.avg_vector_search_ms = memory_metrics.avg_vector_search_ms
        stats.avg_recall_latency_ms = memory_metrics.avg_recall_latency_ms
        stats.total_compressions = memory_metrics.total_compressions
        stats.total_archives = memory_metrics.total_memories_archived

        return stats


memory_manager = MemoryManager()
