"""
Data Transfer Objects (DTOs) for API Requests and Responses in JARVIS AI OS.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from jarvis.domain.value_objects import MemoryType, ProcessStatus, TaskPriority, ToolPermission


class CreateProcessRequest(BaseModel):
    """Request schema to initialize a new agent process."""
    agent_name: str = Field(..., example="DeveloperAgent", description="Identifier name of agent")
    role: str = Field(default="Autonomous Software Engineer", description="System prompt persona/role")
    goal: str = Field(..., example="Create a Python utility script", description="Target task objective")
    priority: TaskPriority = Field(default=TaskPriority.NORMAL, description="Queue scheduling priority")
    max_steps: int = Field(default=10, ge=1, le=50, description="Max execution step loops")
    permissions: List[ToolPermission] = Field(
        default_factory=lambda: [ToolPermission.READ_ONLY, ToolPermission.FILE_WRITE],
        description="Assigned tool execution permissions"
    )


class ProcessResponse(BaseModel):
    """Response schema for agent process details."""
    process_id: str
    agent_name: str
    role: str
    status: ProcessStatus
    goal: str
    priority: TaskPriority
    current_step: int
    max_steps: int
    history: List[Dict[str, Any]]
    result: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class AddMemoryRequest(BaseModel):
    """Request schema to store memory."""
    content: str = Field(..., description="Text content to embed and index")
    memory_type: MemoryType = Field(default=MemoryType.EPISODIC)
    importance: float = Field(default=1.0, ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SearchMemoryRequest(BaseModel):
    """Request schema to search memory."""
    query: str = Field(..., description="Semantic search query string")
    top_k: int = Field(default=5, ge=1, le=20)
    min_similarity: float = Field(default=0.4, ge=0.0, le=1.0)


class MemoryResponse(BaseModel):
    """Response schema for stored memory unit."""
    id: str
    memory_type: MemoryType
    content: str
    metadata: Dict[str, Any]
    timestamp: datetime
    importance: float


class ExecuteToolRequest(BaseModel):
    """Request schema to execute a system tool directly."""
    tool_name: str = Field(..., description="Registered tool name")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Input parameters")


class HealthResponse(BaseModel):
    """System status and telemetry overview."""
    status: str = "HEALTHY"
    app_name: str
    version: str
    active_processes: int
    total_processes: int
    uptime_seconds: float
    environment: str
