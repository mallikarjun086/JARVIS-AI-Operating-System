"""
Unit Tests for Vector Memory Store and Embeddings.
"""

import pytest
from jarvis.domain.entities import MemoryRecord
from jarvis.domain.value_objects import MemoryType
from jarvis.infrastructure.llm.llm_gateway import LLMGateway
from jarvis.infrastructure.memory.vector_store import VectorMemoryStore


@pytest.mark.asyncio
async def test_vector_memory_add_and_search():
    """Verifies adding records to vector store and searching by semantic similarity."""
    llm = LLMGateway(fallback_mode=True)
    vstore = VectorMemoryStore(llm_provider=llm)

    rec1 = MemoryRecord(
        memory_type=MemoryType.SEMANTIC,
        content="JARVIS AI Operating System uses Hexagonal Clean Architecture.",
        importance=1.0
    )
    rec2 = MemoryRecord(
        memory_type=MemoryType.EPISODIC,
        content="Recipes for baking chocolate chip cookies in oven.",
        importance=1.0
    )

    await vstore.add_memory(rec1)
    await vstore.add_memory(rec2)

    results = await vstore.search_memory(query="Clean Architecture AI OS", top_k=1, min_similarity=0.1)
    assert len(results) >= 1
    assert "Clean Architecture" in results[0].content
