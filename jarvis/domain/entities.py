"""
Domain Entities for JARVIS AI Operating System.
Fully typed, immutable domain models built with Pydantic v2.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field, ConfigDict
from jarvis.domain.value_objects import MemoryType, ProcessStatus, TaskPriority, ToolPermission


class ToolDefinition(BaseModel):
    """Definition of an executable capability in the AI OS."""
    model_config = ConfigDict(frozen=True)

    name: str = Field(..., description="Unique tool identifier name")
    description: str = Field(..., description="Human and LLM readable tool description")
    parameters_schema: Dict[str, Any] = Field(default_factory=dict, description="JSON schema of accepted parameters")
    permission_required: ToolPermission = Field(default=ToolPermission.READ_ONLY, description="Required execution privilege")


class ToolResult(BaseModel):
    """Result payload returned by a system tool execution."""
    model_config = ConfigDict(frozen=True)

    tool_name: str
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time_ms: float = 0.0


class MemoryRecord(BaseModel):
    """An indexed unit of memory in the vector & episodic memory store."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    memory_type: MemoryType = Field(default=MemoryType.EPISODIC)
    content: str = Field(..., description="Textual content stored in memory")
    vector: List[float] = Field(default_factory=list, description="Vector embedding representation")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Contextual tags and metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    importance: float = Field(default=1.0, ge=0.0, le=1.0, description="Memory relevance weight")


class TaskContext(BaseModel):
    """Execution context and state history of an autonomous agent task."""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    goal: str = Field(..., description="Target objective for the agent process")
    priority: TaskPriority = Field(default=TaskPriority.NORMAL)
    status: ProcessStatus = Field(default=ProcessStatus.CREATED)
    max_steps: int = Field(default=10, ge=1, le=50, description="Maximum execution step iterations")
    current_step: int = Field(default=0, ge=0)
    history: List[Dict[str, Any]] = Field(default_factory=list, description="Execution step trajectory log")
    result: Optional[str] = Field(default=None, description="Final output summary")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def add_step_log(self, step_number: int, action: str, output: Any, status: str = "SUCCESS") -> None:
        """Appends a completed execution step to task history."""
        self.history.append({
            "step": step_number,
            "action": action,
            "output": output,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.current_step = step_number
        self.updated_at = datetime.utcnow()


class AgentProcess(BaseModel):
    """Primary process control block (PCB) for an active agent thread."""
    process_id: str = Field(default_factory=lambda: f"proc-{uuid.uuid4().hex[:8]}")
    agent_name: str = Field(..., description="Name of the assigned autonomous agent")
    role: str = Field(default="Autonomous Assistant", description="System prompt persona/role")
    status: ProcessStatus = Field(default=ProcessStatus.CREATED)
    task_context: TaskContext
    permissions: List[ToolPermission] = Field(
        default_factory=lambda: [ToolPermission.READ_ONLY],
        description="Assigned execution privileges"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    def update_status(self, new_status: ProcessStatus) -> None:
        """Updates process lifecycle status."""
        self.status = new_status
        self.task_context.status = new_status
        if new_status in (ProcessStatus.COMPLETED, ProcessStatus.FAILED, ProcessStatus.CANCELLED):
            self.completed_at = datetime.utcnow()


class KernelMetrics(BaseModel):
    """System-wide operational metrics and resource consumption state."""
    total_processes: int = 0
    active_processes: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    total_tokens_used: int = 0
    average_latency_ms: float = 0.0
    uptime_seconds: float = 0.0
