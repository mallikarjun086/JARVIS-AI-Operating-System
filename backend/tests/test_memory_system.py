"""
Pytest Test Suite for Long-Term and Multi-Tier Memory Subsystem.
Tests EVERY memory operation: short-term, conversation, semantic search, ranking, compression, and TTL expiration.
"""

import asyncio
from datetime import datetime, timedelta
from httpx import AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.memory.maintenance import maintenance_engine
from app.memory.ranking import ranking_engine
from app.memory.repository import MemoryRepository
from app.memory.schemas import MemoryCategory, MemoryCreate, MemoryQuery
from app.memory.vector_adapter import vector_adapter


@pytest.mark.asyncio
async def test_memory_creation_and_vector_embedding(db_session: AsyncSession):
    """Tests creating short-term and long-term memory entries with vector embeddings."""
    repo = MemoryRepository(db_session)

    mem_in = MemoryCreate(
        content="JARVIS AI Operating System uses Clean Architecture.",
        category=MemoryCategory.LONG_TERM_EPISODIC,
        importance_score=0.9,
        metadata={"domain": "architecture"}
    )

    mem = await repo.create_memory(mem_in, user_id="test_user_1")
    assert mem.id is not None
    assert len(mem.vector) == 384
    assert mem.importance_score == 0.9
    assert mem.category == MemoryCategory.LONG_TERM_EPISODIC


@pytest.mark.asyncio
async def test_semantic_search_and_ranking(db_session: AsyncSession):
    """Tests hybrid semantic search and multi-factor ranking calculations."""
    repo = MemoryRepository(db_session)

    mem1 = await repo.create_memory(
        MemoryCreate(content="Recipes for baking chocolate chip cookies.", category=MemoryCategory.SEMANTIC, importance_score=0.2),
        user_id="test_user_2"
    )
    mem2 = await repo.create_memory(
        MemoryCreate(content="PostgreSQL database query optimization techniques.", category=MemoryCategory.SEMANTIC, importance_score=0.9),
        user_id="test_user_2"
    )

    query = MemoryQuery(query="PostgreSQL query database optimization", top_k=2)
    candidates = await repo.list_active_memories(user_id="test_user_2")

    q_vector = vector_adapter.generate_embedding(query.query)
    ranked_results = ranking_engine.rank_memories(query, q_vector, candidates)

    assert len(ranked_results) >= 1
    top_result = ranked_results[0]
    assert "PostgreSQL" in top_result.entry.content
    assert top_result.ranked_score > 0.4
    assert top_result.vector_similarity > 0.0


@pytest.mark.asyncio
async def test_memory_compression(db_session: AsyncSession):
    """Tests compressing multiple conversation turns into a long-term semantic memory."""
    turns = [
        "User: How do we configure PostgreSQL async pool?",
        "Assistant: Use create_async_engine with asyncpg driver and pool_pre_ping=True.",
        "User: Excellent, thank you!"
    ]

    compressed_mem = await maintenance_engine.compress_conversation(
        db=db_session,
        conversation_turns=turns,
        user_id="test_user_3",
        importance_score=0.85
    )

    assert compressed_mem.category == MemoryCategory.SEMANTIC
    assert "Compressed Knowledge" in compressed_mem.content
    assert compressed_mem.importance_score == 0.85


@pytest.mark.asyncio
async def test_memory_expiration_and_cleanup(db_session: AsyncSession):
    """Tests TTL expiration enforcement and garbage collection purge pass."""
    repo = MemoryRepository(db_session)

    # 1. Create entry with 1 second TTL
    mem_ttl = await repo.create_memory(
        MemoryCreate(content="Transient short term session data.", category=MemoryCategory.SHORT_TERM, ttl_seconds=1),
        user_id="test_user_4"
    )

    # Manually expire entry in database
    mem_model = await db_session.get(repo._to_schema(mem_ttl).__class__ if False else None or __import__('app.models.memory', fromlist=['MemoryRecordModel']).MemoryRecordModel, mem_ttl.id)
    if mem_model:
        mem_model.expires_at = datetime.utcnow() - timedelta(seconds=10)
        await db_session.commit()

    # Purge expired records
    purged_count = await maintenance_engine.cleanup_expired_memories(db_session)
    assert purged_count >= 1


@pytest.mark.asyncio
async def test_memory_api_endpoints(client: AsyncClient):
    """Tests REST endpoints for memory create, ranked search, compression, and deletion."""
    # Register & login
    await client.post("/api/v1/auth/register", json={"email": "memuser@jarvis.ai", "password": "Password123!", "full_name": "Memory User"})
    login_resp = await client.post("/api/v1/auth/login", data={"username": "memuser@jarvis.ai", "password": "Password123!"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Memory Endpoint
    create_payload = {
        "content": "API Demonstration memory entry for long-term storage.",
        "category": "LONG_TERM_EPISODIC",
        "importance_score": 0.88
    }
    c_resp = await client.post("/api/v1/memory", json=create_payload, headers=headers)
    assert c_resp.status_code == 201
    mem_id = c_resp.json()["id"]

    # 2. Query Memory Endpoint
    q_payload = {"query": "API Demonstration memory", "top_k": 3}
    q_resp = await client.post("/api/v1/memory/query", json=q_payload, headers=headers)
    assert q_resp.status_code == 200
    results = q_resp.json()
    assert len(results) >= 1
    assert "ranked_score" in results[0]

    # 3. Compress Endpoint
    comp_payload = {"conversation_turns": ["User: Hello", "Assistant: Hi there!"]}
    comp_resp = await client.post("/api/v1/memory/compress", json=comp_payload, headers=headers)
    assert comp_resp.status_code == 200

    # 4. Cleanup Endpoint
    clean_resp = await client.post("/api/v1/memory/cleanup", headers=headers)
    assert clean_resp.status_code == 200

    # 5. Delete Endpoint
    del_resp = await client.delete(f"/api/v1/memory/{mem_id}", headers=headers)
    assert del_resp.status_code == 200
