"""
Pydantic Schemas for Enterprise Multi-Agent Orchestration Platform (Sprint 9).
Defines Agent roles, Agent metadata, Capability queries, Scheduler tasks, Consensus votes, SharedContext, and Telemetry.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field, ConfigDict
from app.tools.schemas import PermissionLevel


class AgentRole(str, Enum):
    COORDINATOR = "COORDINATOR"
    PLANNER = "PLANNER"
    RESEARCH = "RESEARCH"
    BROWSER = "BROWSER"
    DESKTOP = "DESKTOP"
    CODING = "CODING"
    MEMORY = "MEMORY"
    VISION = "VISION"
    VOICE = "VOICE"
    VERIFIER = "VERIFIER"


class AgentStatus(str, Enum):
    READY = "READY"
    BUSY = "BUSY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    OFFLINE = "OFFLINE"


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class AgentMessage(BaseModel):
    """Inter-agent communication message descriptor."""
    message_id: str = Field(default_factory=lambda: f"msg-{uuid.uuid4().hex[:8]}")
    sender_role: AgentRole
    recipient_role: AgentRole
    content: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    task_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentMetadata(BaseModel):
    """Registration descriptor for a specialized agent."""
    agent_id: str
    name: str
    role: AgentRole
    version: str = "1.0.0"
    description: str
    status: AgentStatus = AgentStatus.READY
    priority: int = 1
    availability: bool = True
    capabilities: List[str] = Field(default_factory=list)
    supported_tools: List[str] = Field(default_factory=list)
    supported_languages: List[str] = Field(default_factory=list)
    supported_frameworks: List[str] = Field(default_factory=list)
    estimated_cost_per_task: float = 0.01
    estimated_latency_ms: float = 150.0
    resource_usage_cpu_percent: float = 5.0
    permission_level: PermissionLevel = PermissionLevel.READ_ONLY
    last_heartbeat: datetime = Field(default_factory=datetime.utcnow)


class CapabilityQuery(BaseModel):
    """Query payload for CapabilityGraph selection."""
    required_capabilities: List[str]
    preferred_role: Optional[AgentRole] = None
    min_priority: int = 1
    max_latency_ms: float = 5000.0


class SharedContextPayload(BaseModel):
    """Immutable shared context dictionary passed to all executing agents."""
    workflow_id: str = Field(default_factory=lambda: f"wf-{uuid.uuid4().hex[:8]}")
    execution_id: str = Field(default_factory=lambda: f"exec-{uuid.uuid4().hex[:8]}")
    user_id: Optional[str] = None
    user_context: Dict[str, Any] = Field(default_factory=dict)
    planner_context: Dict[str, Any] = Field(default_factory=dict)
    memory_context: List[str] = Field(default_factory=list)
    security_context: Dict[str, Any] = Field(default_factory=dict)
    approval_context: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SubTaskSpec(BaseModel):
    """Task specification for agent execution."""
    subtask_id: str = Field(default_factory=lambda: f"sub-{uuid.uuid4().hex[:6]}")
    goal: str
    required_capability: str = "general_processing"
    assigned_agent: Optional[AgentRole] = None
    assigned_agent_id: Optional[str] = None
    priority: int = 1
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    result: Optional[Any] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: float = 30.0


class SwarmExecutionPlan(BaseModel):
    """Execution plan for multi-agent swarm."""
    plan_id: str = Field(default_factory=lambda: f"swarm-{uuid.uuid4().hex[:8]}")
    goal: str
    status: TaskStatus = TaskStatus.PENDING
    tasks: List[SubTaskSpec] = Field(default_factory=list)
    shared_memory_snapshot: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ConsensusVote(BaseModel):
    """Single agent vote in consensus engine."""
    agent_id: str
    role: AgentRole
    approved: bool
    confidence_score: float = Field(default=0.9, ge=0.0, le=1.0)
    vote_weight: float = 1.0
    reason: str = "Acceptance criteria verified."


class ConsensusResult(BaseModel):
    """Aggregated consensus voting outcome."""
    consensus_passed: bool
    overall_confidence: float
    total_votes: int
    positive_votes: int
    negative_votes: int
    escalated_to_human: bool = False
    votes: List[ConsensusVote] = Field(default_factory=list)


class AgentTaskTelemetry(BaseModel):
    """Telemetry performance metric descriptor for specialized agents."""
    agent_id: str
    role: AgentRole
    completed_count: int = 0
    failed_count: int = 0
    total_latency_ms: float = 0.0
    avg_latency_ms: float = 0.0
    uptime_seconds: float = 0.0
