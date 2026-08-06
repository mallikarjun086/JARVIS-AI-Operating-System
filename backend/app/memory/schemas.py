"""
Pydantic Schemas for the Enterprise Memory & Knowledge Engine.
Covers all 11 memory types, full context fields, retrieval, ranking, and observability.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field, ConfigDict


# ─────────────────────────────────────────────────
# Enumerations
# ─────────────────────────────────────────────────

class MemoryCategory(str, Enum):
    SHORT_TERM = "SHORT_TERM"
    CONVERSATION = "CONVERSATION"
    LONG_TERM_EPISODIC = "LONG_TERM_EPISODIC"
    SEMANTIC = "SEMANTIC"


class MemoryType(str, Enum):
    CONVERSATION = "CONVERSATION"
    PROJECT = "PROJECT"
    KNOWLEDGE = "KNOWLEDGE"
    USER_PREFERENCE = "USER_PREFERENCE"
    TOOL_EXECUTION = "TOOL_EXECUTION"
    BROWSER = "BROWSER"
    CODE = "CODE"
    DOCUMENT = "DOCUMENT"
    WORKFLOW = "WORKFLOW"
    LONG_TERM = "LONG_TERM"
    SHORT_TERM = "SHORT_TERM"
    GENERAL = "GENERAL"


# ─────────────────────────────────────────────────
# Create / Update Schemas
# ─────────────────────────────────────────────────

class MemoryCreate(BaseModel):
    """Payload schema to create a memory record."""
    content: str = Field(..., description="Textual content to index")
    category: MemoryCategory = Field(default=MemoryCategory.LONG_TERM_EPISODIC)
    memory_type: MemoryType = Field(default=MemoryType.GENERAL)
    importance_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Memory importance weight")
    ttl_seconds: Optional[int] = Field(default=None, description="Optional time-to-live seconds before expiration")
    conversation_id: Optional[str] = Field(default=None, description="Source conversation ID")
    project_id: Optional[str] = Field(default=None, description="Associated project ID")
    agent_id: Optional[str] = Field(default=None, description="Originating agent ID")
    source: Optional[str] = Field(default=None, description="Origin source (e.g. user, system, browser)")
    tags: List[str] = Field(default_factory=list, description="Searchable tags")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MemoryUpdate(BaseModel):
    """Payload schema to update an existing memory record."""
    content: Optional[str] = None
    importance_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    memory_type: Optional[MemoryType] = None


# ─────────────────────────────────────────────────
# Query / Retrieval Schemas
# ─────────────────────────────────────────────────

class MemoryQuery(BaseModel):
    """Query schema for semantic search and ranked retrieval."""
    query: str = Field(..., description="Semantic search query string")
    top_k: int = Field(default=5, ge=1, le=50)
    min_importance: float = Field(default=0.0, ge=0.0, le=1.0)
    score_threshold: float = Field(default=0.0, ge=0.0, le=1.0, description="Minimum ranked score threshold")
    categories: Optional[List[MemoryCategory]] = Field(default=None, description="Optional category filter")
    memory_types: Optional[List[MemoryType]] = Field(default=None, description="Optional memory type filter")
    conversation_id: Optional[str] = Field(default=None)
    project_id: Optional[str] = Field(default=None)
    agent_id: Optional[str] = Field(default=None)
    tags: Optional[List[str]] = Field(default=None, description="Tag filter (OR logic)")
    date_from: Optional[datetime] = Field(default=None)
    date_to: Optional[datetime] = Field(default=None)
    include_archived: bool = Field(default=False)


# ─────────────────────────────────────────────────
# Entry / Result Schemas
# ─────────────────────────────────────────────────

class MemoryEntry(BaseModel):
    """Full representational schema for a memory entry."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None
    project_id: Optional[str] = None
    agent_id: Optional[str] = None
    category: MemoryCategory
    memory_type: MemoryType = MemoryType.GENERAL
    content: str
    summary: Optional[str] = None
    importance_score: float = 0.5
    access_count: int = 0
    recall_count: int = 0
    source: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    last_accessed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    archived: bool = False
    vector_id: Optional[str] = None
    vector: Optional[List[float]] = Field(default_factory=list)



class MemorySearchResult(BaseModel):
    """Ranked memory search result payload with scoring breakdown."""
    entry: MemoryEntry
    vector_similarity: float
    importance_score: float
    recency_score: float
    access_frequency_score: float
    ranked_score: float


# ─────────────────────────────────────────────────
# Maintenance / Compression Schemas
# ─────────────────────────────────────────────────

class MemoryCompressionRequest(BaseModel):
    """Payload to trigger conversation memory compression."""
    conversation_turns: List[str] = Field(..., description="Raw conversation turns to summarize")
    importance_score: float = Field(default=0.8, ge=0.0, le=1.0)
    conversation_id: Optional[str] = None
    project_id: Optional[str] = None


# ─────────────────────────────────────────────────
# Observability Schemas
# ─────────────────────────────────────────────────

class MemoryStats(BaseModel):
    """Memory engine observability statistics."""
    total_memories: int = 0
    active_memories: int = 0
    archived_memories: int = 0
    expired_memories: int = 0
    total_embeddings: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    cache_hit_rate: float = 0.0
    avg_vector_search_ms: float = 0.0
    avg_recall_latency_ms: float = 0.0
    total_compressions: int = 0
    total_archives: int = 0
    memories_by_type: Dict[str, int] = Field(default_factory=dict)
    memories_by_category: Dict[str, int] = Field(default_factory=dict)
