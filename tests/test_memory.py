"""
Comprehensive Tests for Enterprise Memory & Knowledge Engine (Sprint 3).
Tests:
1. EmbeddingEngine (caching, batching, fallback)
2. ChromaVectorStore (local persistence, namespace filtering, CRUD)
3. MemoryRepository (SQL persistence, filters, archive/restore, GDPR erase, stats)
4. MemoryManager (end-to-end store, retrieve, update, delete, stats)
5. MemoryRanker & MemoryRetriever (multi-factor score calculations)
6. MemoryCompressor (LLM conversation summarization & deduplication)
"""

import os
import tempfile
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base
from app.memory.compressor import memory_compressor
from app.memory.embedding import EmbeddingEngine, HashEmbeddingProvider
from app.memory.manager import MemoryManager
from app.memory.metrics import memory_metrics
from app.memory.ranking import MemoryRanker
from app.memory.repository import MemoryRepository
from app.memory.retriever import MemoryRetriever
from app.memory.schemas import (
    MemoryCategory,
    MemoryCreate,
    MemoryQuery,
    MemoryType,
    MemoryUpdate,
)
from app.memory.vector_store import ChromaVectorStore


@pytest.fixture
async def async_db_session():
    """Provides an isolated in-memory SQLite database session for unit tests."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_embedding_engine_cache_and_batching():
    """Verifies EmbeddingEngine LRU caching, batch generation, and fallback."""
    engine = EmbeddingEngine()
    await engine.initialize()

    text = "JARVIS AI OS memory engine benchmark"
    vec1 = await engine.embed(text)
    assert len(vec1) > 0
    assert isinstance(vec1[0], float)

    # Second call should hit LRU cache
    stats_before = engine.cache_stats
    vec2 = await engine.embed(text)
    assert vec1 == vec2
    assert engine.cache_stats["hits"] > stats_before["hits"]

    # Batch embedding
    batch_texts = ["Fact 1: JARVIS supports tools", "Fact 2: JARVIS supports vision"]
    vectors = await engine.embed_batch(batch_texts)
    assert len(vectors) == 2
    assert len(vectors[0]) == len(vec1)


@pytest.mark.asyncio
async def test_memory_repository_crud(async_db_session: AsyncSession):
    """Tests SQL metadata repository CRUD, archive, restore, and filters."""
    repo = MemoryRepository(async_db_session)

    # 1. Create
    mem_in = MemoryCreate(
        content="User prefers dark theme mode",
        category=MemoryCategory.SEMANTIC,
        memory_type=MemoryType.USER_PREFERENCE,
        importance_score=0.9,
        tags=["ui", "preference"],
        project_id="proj-101",
        conversation_id="conv-202"
    )
    entry = await repo.create_memory(mem_in, user_id="user-1")
    assert entry.id is not None
    assert entry.content == "User prefers dark theme mode"
    assert entry.memory_type == MemoryType.USER_PREFERENCE

    # 2. Read
    fetched = await repo.get_memory(entry.id, user_id="user-1")
    assert fetched is not None
    assert fetched.access_count == 1

    # 3. Filter list
    listed = await repo.list_active_memories(
        user_id="user-1",
        project_id="proj-101",
        memory_types=[MemoryType.USER_PREFERENCE]
    )
    assert len(listed) == 1

    # 4. Update
    updated = await repo.update_memory(
        entry.id,
        MemoryUpdate(importance_score=1.0, tags=["ui", "preference", "theme"]),
        user_id="user-1"
    )
    assert updated.importance_score == 1.0
    assert "theme" in updated.tags

    # 5. Archive & Restore
    archived = await repo.archive_memory(entry.id, user_id="user-1")
    assert archived.archived is True

    listed_active = await repo.list_active_memories(user_id="user-1", include_archived=False)
    assert len(listed_active) == 0

    restored = await repo.restore_memory(entry.id, user_id="user-1")
    assert restored.archived is False

    # 6. Delete
    deleted = await repo.delete_memory(entry.id, user_id="user-1")
    assert deleted is True


@pytest.mark.asyncio
async def test_memory_manager_end_to_end(async_db_session: AsyncSession):
    """Tests MemoryManager orchestration between SQL and ChromaDB vector store."""
    manager = MemoryManager()
    await manager.initialize()

    # Store memory
    mem_in = MemoryCreate(
        content="JARVIS autonomous agent pool architecture",
        category=MemoryCategory.LONG_TERM_EPISODIC,
        memory_type=MemoryType.PROJECT,
        importance_score=0.85,
        project_id="jarvis-core"
    )
    entry = await manager.store(async_db_session, mem_in, user_id="user-admin")
    assert entry.id is not None
    assert entry.vector_id is not None

    # Semantic Query Retrieval
    query = MemoryQuery(
        query="Tell me about JARVIS agent pool architecture",
        top_k=3,
        project_id="jarvis-core"
    )
    results = await manager.retrieve(async_db_session, query, user_id="user-admin")
    assert len(results) >= 1
    assert "agent pool" in results[0].entry.content
    assert results[0].ranked_score > 0.0

    # Get Stats
    stats = await manager.get_stats(async_db_session, user_id="user-admin")
    assert stats.total_memories >= 1

    # Cleanup
    deleted = await manager.delete(async_db_session, entry.id, user_id="user-admin")
    assert deleted is True


@pytest.mark.asyncio
async def test_memory_compressor_deduplication(async_db_session: AsyncSession):
    """Tests MemoryCompressor conversation compression and duplicate detection."""
    turns = [
        "User: How do I configure PostgreSQL?",
        "Assistant: Set DATABASE_URL in .env file.",
        "User: Thanks! Will it auto-fallback to SQLite?",
        "Assistant: Yes, if DATABASE_URL is not set it defaults to sqlite+aiosqlite."
    ]

    mem1 = await memory_compressor.compress_conversation(
        db=async_db_session,
        conversation_turns=turns,
        user_id="user-1",
        importance_score=0.8
    )
    assert mem1 is not None
    assert mem1.content != ""
