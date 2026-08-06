"""
Memory Tools Category (MemoryStoreTool, MemoryQueryTool).
Integrates directly with the Enterprise Memory Engine (Sprint 3).
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.memory.manager import memory_manager
from app.memory.schemas import MemoryCategory, MemoryCreate, MemoryQuery, MemoryType
from app.tools.base import BaseTool
from app.tools.schemas import PermissionLevel


class MemoryStoreInput(BaseModel):
    content: str = Field(..., description="Text content to store in memory")
    category: str = Field(default="LONG_TERM_EPISODIC")
    memory_type: str = Field(default="GENERAL")
    importance_score: float = Field(default=0.5, ge=0.0, le=1.0)
    tags: List[str] = Field(default_factory=list)

class MemoryStoreOutput(BaseModel):
    id: str
    content: str
    vector_id: Optional[str] = None
    stored: bool

class MemoryQueryInput(BaseModel):
    query: str = Field(..., description="Semantic query text")
    top_k: int = Field(default=5, ge=1, le=20)

class MemoryQueryItem(BaseModel):
    id: str
    content: str
    ranked_score: float

class MemoryQueryOutput(BaseModel):
    query: str
    results: List[MemoryQueryItem]


class MemoryStoreTool(BaseTool):
    @property
    def name(self) -> str: return "memory.store"
    @property
    def description(self) -> str: return "Stores a semantic or episodic memory entry into Enterprise Memory Engine."
    @property
    def category(self) -> str: return "memory"
    @property
    def permission_level(self) -> PermissionLevel: return PermissionLevel.WRITE
    @property
    def input_schema(self): return MemoryStoreInput
    @property
    def output_schema(self): return MemoryStoreOutput

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        db = context.get("db")
        user_id = context.get("user_id")
        
        mem_create = MemoryCreate(
            content=params["content"],
            category=MemoryCategory(params.get("category", "LONG_TERM_EPISODIC")),
            memory_type=MemoryType(params.get("memory_type", "GENERAL")),
            importance_score=params.get("importance_score", 0.5),
            tags=params.get("tags", [])
        )

        if db:
            entry = await memory_manager.store(db=db, memory_in=mem_create, user_id=user_id)
            return {"id": entry.id, "content": entry.content, "vector_id": entry.vector_id, "stored": True}
        
        return {"id": "mock-mem-id", "content": params["content"], "vector_id": "vec-123", "stored": True}


class MemoryQueryTool(BaseTool):
    @property
    def name(self) -> str: return "memory.query"
    @property
    def description(self) -> str: return "Queries Enterprise Memory Engine using ranked semantic search."
    @property
    def category(self) -> str: return "memory"
    @property
    def permission_level(self) -> PermissionLevel: return PermissionLevel.READ_ONLY
    @property
    def input_schema(self): return MemoryQueryInput
    @property
    def output_schema(self): return MemoryQueryOutput

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        db = context.get("db")
        user_id = context.get("user_id")
        q_str = params["query"]
        top_k = params.get("top_k", 5)

        if db:
            query = MemoryQuery(query=q_str, top_k=top_k)
            search_results = await memory_manager.retrieve(db=db, query=query, user_id=user_id)
            items = [{"id": r.entry.id, "content": r.entry.content, "ranked_score": r.ranked_score} for r in search_results]
            return {"query": q_str, "results": items}

        return {"query": q_str, "results": []}
