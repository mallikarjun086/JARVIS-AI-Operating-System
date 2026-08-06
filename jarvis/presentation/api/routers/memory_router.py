"""
API Router for Vector & Episodic Memory Store Operations.
"""

from typing import List
from fastapi import APIRouter, Request, status
from jarvis.application.dto import AddMemoryRequest, MemoryResponse, SearchMemoryRequest
from jarvis.application.use_cases.memory_use_cases import AddMemoryUseCase, SearchMemoryUseCase

router = APIRouter(prefix="/api/v1/memory", tags=["Vector Memory Store"])


@router.post("", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED, summary="Add Memory Record")
async def add_memory(req: AddMemoryRequest, request: Request) -> MemoryResponse:
    """Embeds and indexes a new memory entry."""
    vector_store = request.app.state.vector_store
    llm_provider = request.app.state.llm_provider
    use_case = AddMemoryUseCase(vector_store=vector_store, llm_provider=llm_provider)
    return await use_case.execute(req)


@router.post("/search", response_model=List[MemoryResponse], summary="Semantic Memory Search")
async def search_memory(req: SearchMemoryRequest, request: Request) -> List[MemoryResponse]:
    """Retrieves top-k relevant memory records using vector similarity."""
    vector_store = request.app.state.vector_store
    use_case = SearchMemoryUseCase(vector_store=vector_store)
    return await use_case.execute(req)
