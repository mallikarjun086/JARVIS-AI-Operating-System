"""
Pydantic Schemas for Enterprise Autonomous Workflow Engine Subsystem (Sprint 10).
Defines Event Sourcing events, 12-state WorkflowStatus, DAG Nodes, Definitions, Checkpoints, Compensation Policies, Versioning, and Resource Reservations.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field, ConfigDict


class NodeType(str, Enum):
    ACTION = "ACTION"
    CONDITION = "CONDITION"
    LOOP = "LOOP"
    HUMAN_APPROVAL = "HUMAN_APPROVAL"
    TIMER = "TIMER"
    DELAY = "DELAY"
    SUB_WORKFLOW = "SUB_WORKFLOW"
    FRAGMENT = "FRAGMENT"
    PLUGIN_STEP = "PLUGIN_STEP"
    ROLLBACK = "ROLLBACK"


class WorkflowStatus(str, Enum):
    """12 Lifecycle states for Workflow Runtime."""
    CREATED = "CREATED"
    VALIDATED = "VALIDATED"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    PAUSED_FOR_APPROVAL = "WAITING_APPROVAL"
    PAUSED = "PAUSED"
    RETRYING = "RETRYING"
    ROLLING_BACK = "ROLLING_BACK"
    ROLLED_BACK = "FAILED"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"



class WorkflowEventType(str, Enum):
    """Immutable Event Sourcing Event Types."""
    WORKFLOW_CREATED = "WorkflowCreated"
    WORKFLOW_VALIDATED = "WorkflowValidated"
    WORKFLOW_STARTED = "WorkflowStarted"
    TASK_SCHEDULED = "TaskScheduled"
    TASK_STARTED = "TaskStarted"
    TASK_COMPLETED = "TaskCompleted"
    TASK_FAILED = "TaskFailed"
    RETRY_STARTED = "RetryStarted"
    APPROVAL_REQUESTED = "ApprovalRequested"
    APPROVAL_GRANTED = "ApprovalGranted"
    APPROVAL_REJECTED = "ApprovalRejected"
    ROLLBACK_STARTED = "RollbackStarted"
    ROLLBACK_COMPLETED = "RollbackCompleted"
    WORKFLOW_PAUSED = "WorkflowPaused"
    WORKFLOW_RESUMED = "WorkflowResumed"
    WORKFLOW_COMPLETED = "WorkflowCompleted"
    WORKFLOW_ARCHIVED = "WorkflowArchived"


class WorkflowEvent(BaseModel):
    """Immutable Event Sourcing Record."""
    event_id: str = Field(default_factory=lambda: f"wfevt-{uuid.uuid4().hex[:8]}")
    workflow_id: str
    execution_id: str
    event_type: WorkflowEventType
    source: str = "WorkflowRuntime"
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class VersionInfo(BaseModel):
    """Workflow Versioning Metadata."""
    workflow_version: str = "1.0.0"
    template_version: str = "1.0.0"
    schema_version: str = "1.0.0"
    migration_version: str = "1.0.0"


class ResourceReservation(BaseModel):
    """Pre-execution Resource Reservation Request."""
    cpu_cores: float = 1.0
    ram_mb: float = 512.0
    gpu_units: float = 0.0
    browser_sessions: int = 0
    desktop_sessions: int = 0
    llm_budget_tokens: int = 50000


class WorkflowNode(BaseModel):
    """DAG Workflow Node Specification."""
    node_id: str
    node_type: NodeType
    name: str
    plugin_name: Optional[str] = Field(default=None, description="Plugin step identifier (e.g. 'BrowserNode', 'SWENode')")
    action_name: Optional[str] = None
    condition_expr: Optional[str] = None
    loop_items_key: Optional[str] = None
    retry_limit: int = 3
    timeout_seconds: float = 300.0
    compensation_action: Optional[str] = None
    next_nodes: List[str] = Field(default_factory=list)


class WorkflowDefinition(BaseModel):
    """Workflow Definition Blueprint."""
    definition_id: str = Field(default_factory=lambda: f"wfdef-{uuid.uuid4().hex[:8]}")
    name: str
    description: str
    nodes: List[WorkflowNode]
    version_info: VersionInfo = Field(default_factory=VersionInfo)
    resource_reservation: ResourceReservation = Field(default_factory=ResourceReservation)
    cron_schedule: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WorkflowCheckpoint(BaseModel):
    """Persistent Snapshot Checkpoint."""
    checkpoint_id: str = Field(default_factory=lambda: f"chk-{uuid.uuid4().hex[:8]}")
    workflow_id: str
    execution_id: str
    checkpoint_number: int = 1
    version_info: VersionInfo
    completed_tasks: List[str] = Field(default_factory=list)
    pending_tasks: List[str] = Field(default_factory=list)
    running_tasks: List[str] = Field(default_factory=list)
    shared_context: Dict[str, Any] = Field(default_factory=dict)
    memory_references: List[str] = Field(default_factory=list)
    verification_results: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class WorkflowInstance(BaseModel):
    """Active Workflow Instance State."""
    model_config = ConfigDict(from_attributes=True)

    instance_id: str = Field(default_factory=lambda: f"wfinst-{uuid.uuid4().hex[:8]}")
    definition_id: str
    execution_id: str = Field(default_factory=lambda: f"exec-{uuid.uuid4().hex[:8]}")
    name: str
    status: WorkflowStatus = WorkflowStatus.CREATED
    version_info: VersionInfo = Field(default_factory=VersionInfo)
    current_node_id: Optional[str] = None
    variables: Dict[str, Any] = Field(default_factory=dict)
    completed_node_ids: List[str] = Field(default_factory=list)
    pending_approval_id: Optional[str] = None
    last_checkpoint_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
