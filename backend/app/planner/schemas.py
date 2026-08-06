"""
Pydantic Schemas for Enterprise Planner & Execution Engine (Sprint 5 & 5.1).
Defines execution states, policies, plan tasks, resource estimates, plan explanations, and execution plans.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field, ConfigDict
from app.tools.schemas import PermissionLevel


class ExecutionState(str, Enum):
    """11 Lifecycle states for Execution State Machine."""
    CREATED = "CREATED"
    PLANNED = "PLANNED"
    VALIDATED = "VALIDATED"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    READY = "READY"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    RETRYING = "RETRYING"
    FAILED = "FAILED"
    ROLLING_BACK = "ROLLING_BACK"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ExecutionPolicy(str, Enum):
    """Execution policy rules governing plan execution behavior."""
    FAIL_FAST = "FAIL_FAST"
    CONTINUE_ON_ERROR = "CONTINUE_ON_ERROR"
    BEST_EFFORT = "BEST_EFFORT"
    MANUAL_APPROVAL = "MANUAL_APPROVAL"
    RETRY_WITH_BACKOFF = "RETRY_WITH_BACKOFF"
    STOP_ON_PERMISSION_FAILURE = "STOP_ON_PERMISSION_FAILURE"


class SubTaskPriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"


class RecoveryStrategy(str, Enum):
    RETRY = "RETRY"
    SKIP_NON_CRITICAL = "SKIP_NON_CRITICAL"
    ALTERNATIVE_BRANCH = "ALTERNATIVE_BRANCH"
    ROLLBACK = "ROLLBACK"


class PlanTask(BaseModel):
    """Granular executable task node within execution graph."""
    task_id: str = Field(default_factory=lambda: f"task_{uuid.uuid4().hex[:8]}", description="Unique subtask identifier")

    def __init__(self, **data: Any) -> None:
        if "id" in data and "task_id" not in data:
            data["task_id"] = data.pop("id")
        super().__init__(**data)

    @property
    def id(self) -> str:
        return self.task_id


    title: str = Field(default="", description="Short title of action")
    description: str = Field(default="", description="Detailed instructions for task execution")
    tool_required: str = Field(default="system.health", description="Required tool name from Tool Registry (e.g. filesystem.write_file)")
    permission_level: PermissionLevel = Field(default=PermissionLevel.READ_ONLY, description="Mandatory minimum permission level")

    inputs: Dict[str, Any] = Field(default_factory=dict, description="Input parameters passed to Tool Framework")
    outputs_expected: Dict[str, Any] = Field(default_factory=dict, description="Expected output key specification")
    dependencies: List[str] = Field(default_factory=list, description="Prerequisite task IDs")
    priority: SubTaskPriority = Field(default=SubTaskPriority.NORMAL)
    estimated_runtime_seconds: float = Field(default=1.0, ge=0.1)
    retry_policy: Dict[str, Any] = Field(default_factory=lambda: {"max_retries": 3, "backoff_seconds": 2.0})
    rollback_strategy: str = Field(default="NONE", description="NONE, FILE_DELETE, REVERT_STATE")
    is_optional: bool = Field(default=False, description="True if task failure can be skipped")
    condition_expr: Optional[str] = Field(default=None, description="Optional conditional expression for task execution")


# Backward-compatible SubTask alias
SubTask = PlanTask


class ResourceEstimate(BaseModel):
    """Pre-execution resource consumption and runtime estimate."""
    estimated_cpu_level: str = "LOW"
    estimated_memory_mb: float = 64.0
    estimated_network_calls: int = 0
    estimated_disk_ops: int = 0
    estimated_runtime_seconds: float = 5.0
    total_tools: int = 0
    parallel_batches: int = 0
    max_permission_level: PermissionLevel = PermissionLevel.READ_ONLY


class PlanExplanation(BaseModel):
    """Human-readable explanation of plan reasoning and risk assessment."""
    goal: str
    reasoning_summary: str
    task_order: List[str]
    dependency_explanation: str
    estimated_runtime: str
    permission_requirements: str
    risk_assessment: str
    confidence_score: float = Field(default=0.95, ge=0.0, le=1.0)


class ExecutionBatch(BaseModel):
    """Batch of independent subtasks executable concurrently in parallel."""
    batch_id: int
    parallel_task_ids: List[str] = Field(..., description="IDs of subtasks running concurrently")


class RecoveryPolicy(BaseModel):
    """Failure recovery rules per task."""
    task_id: str
    strategy: RecoveryStrategy = Field(default=RecoveryStrategy.RETRY)
    max_retries: int = 3
    backoff_seconds: float = 2.0


class PlanValidationReport(BaseModel):
    """Structured validation report returned by PlanValidator."""
    is_valid: bool
    missing_tools: List[str] = Field(default_factory=list)
    missing_dependencies: List[str] = Field(default_factory=list)
    circular_dependencies: List[List[str]] = Field(default_factory=list)
    permission_violations: List[str] = Field(default_factory=list)
    unsafe_executions: List[str] = Field(default_factory=list)
    approval_required: bool = False
    validation_messages: List[str] = Field(default_factory=list)


class ExecutionPlan(BaseModel):
    """Complete, structured, and versioned JSON execution plan."""
    model_config = ConfigDict(from_attributes=True)

    plan_id: str = Field(default_factory=lambda: f"plan-{uuid.uuid4().hex[:8]}")
    version: str = Field(default="1.0.0")
    planner_version: str = Field(default="5.1.0")
    goal: str = Field(..., description="Original natural language user goal")
    intent_summary: str = Field(..., description="Parsed high-level intent summary")
    generated_by_model: str = Field(default="gpt-3.5-turbo")
    subtasks: List[PlanTask]
    execution_graph: List[ExecutionBatch] = Field(default_factory=list, description="Parallel execution batch ordering")
    topological_order: List[str] = Field(default_factory=list, description="Flat sequential DAG order")

    state: ExecutionState = Field(default=ExecutionState.CREATED)
    policy: ExecutionPolicy = Field(default=ExecutionPolicy.FAIL_FAST)
    is_valid_dag: bool = True
    resource_estimate: ResourceEstimate = Field(default_factory=ResourceEstimate)
    explanation: PlanExplanation = Field(default_factory=lambda: PlanExplanation(
        goal="", reasoning_summary="", task_order=[], dependency_explanation="",
        estimated_runtime="", permission_requirements="", risk_assessment=""
    ))
    checksum: str = Field(default="", description="SHA-256 fingerprint for plan reproducibility")
    recovery_policies: List[RecoveryPolicy] = Field(default_factory=list)
    @property
    def status(self) -> Any:
        return self.state

    created_at: datetime = Field(default_factory=datetime.utcnow)

    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PlannerRequest(BaseModel):
    """Request payload to generate an ExecutionPlan."""
    goal: str = Field(..., example="Create a Spring Boot project and push to GitHub.", description="Natural language goal")
    execution_policy: ExecutionPolicy = Field(default=ExecutionPolicy.FAIL_FAST)
    allow_parallel: bool = Field(default=True, description="Detect and group parallel task execution batches")
    system_context: Optional[str] = Field(default=None, description="Optional extra system context")


class PlanExecuteRequest(BaseModel):
    """Request payload to start executing a validated plan."""
    plan_id: str = Field(..., description="Target execution plan ID")
    approval_granted: bool = Field(default=False, description="True if explicit user approval granted for sensitive tools")


class DAGValidationResponse(BaseModel):
    """Response payload for DAG graph validation."""
    is_valid_dag: bool
    topological_order: List[str]
    circular_dependencies: List[List[str]] = Field(default_factory=list)
    parallel_batches: List[List[str]] = Field(default_factory=list)


class TaskVerificationResult(BaseModel):
    """Verification result returned after executing a task."""
    task_id: str
    verified: bool
    message: str
    output_asserted: bool = True
