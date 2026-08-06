"""
Application Use Cases for AI OS Vector & Episodic Memory Store.
"""

from typing import List
from jarvis.application.dto import AddMemoryRequest, MemoryResponse, SearchMemoryRequest
from jarvis.domain.entities import MemoryRecord
from jarvis.domain.exceptions import VectorStoreError
from jarvis.domain.ports import LLMProviderPort, VectorStorePort


class AddMemoryUseCase:
    """Use case to embed and add a memory record to the vector index."""

    def __init__(
        self,
        vector_store: VectorStorePort,
        llm_provider: LLMProviderPort
    ) -> None:
        self.vector_store = vector_store
        self.llm_provider = llm_provider

    async def execute(self, request: AddMemoryRequest) -> MemoryResponse:
        embedding = await self.llm_provider.generate_embedding(request.content)
        record = MemoryRecord(
            memory_type=request.memory_type,
            content=request.content,
            vector=embedding,
            metadata=request.metadata,
            importance=request.importance
        )

        await self.vector_store.add_memory(record)

        return MemoryResponse(
            id=record.id,
            memory_type=record.memory_type,
            content=record.content,
            metadata=record.metadata,
            timestamp=record.timestamp,
            importance=record.importance
        )


class SearchMemoryUseCase:
    """Use case to search relevant memories by semantic similarity query."""

    def __init__(self, vector_store: VectorStorePort) -> None:
        self.vector_store = vector_store

    async def execute(self, request: SearchMemoryRequest) -> List[MemoryResponse]:
        memories = await self.vector_store.search_memory(
            query=request.query,
            top_k=request.top_k,
            min_similarity=request.min_similarity
        )

        return [
            MemoryResponse(
                id=mem.id,
                memory_type=mem.memory_type,
                content=mem.content,
                metadata=mem.metadata,
                timestamp=mem.timestamp,
                importance=mem.importance
            )
            for mem in memories
        ]
