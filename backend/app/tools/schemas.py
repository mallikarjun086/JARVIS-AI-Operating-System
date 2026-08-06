"""
Pydantic Schemas for Enterprise Tool Framework.
Defines permission levels, execution statuses, audit logging structures, and tool metadata formats.
"""

from datetime import datetime
from enum import Enum, IntEnum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class PermissionLevel(IntEnum):
    """
    Permission authorization levels for the Security & Tool Framework.
    Higher level = higher security restriction.
    """
    READ_ONLY = 0      # Safe read operations (read_file, list_dir, status)
    USER_READ = 0      # Backward-compatible alias for READ_ONLY
    WRITE = 1          # Write operations (write_file, create_dir, delete)

    NETWORK = 2        # Web search, HTTP requests, external API calls
    SYSTEM = 3         # Command execution, system process control
    DANGEROUS = 4      # High-risk operations requiring explicit user approval
    ADMIN = 5          # Administrative system policy & security configuration
    CRITICAL_SYSTEM = 5 # Backward-compatible alias for ADMIN



class ExecutionStatus(str, Enum):
    """Tool execution lifecycle status codes."""
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    TIMEOUT = "TIMEOUT"
    CANCELLED = "CANCELLED"
    ROLLED_BACK = "ROLLED_BACK"


class ToolMetadata(BaseModel):
    """Metadata descriptor detailing a registered tool's specification."""
    name: str = Field(..., description="Unique tool identifier name (e.g. filesystem.read_file)")
    description: str = Field(..., description="Detailed natural language description for LLMs")
    category: str = Field(default="system", description="Tool category (filesystem, terminal, git, browser, etc.)")
    version: str = Field(default="1.0.0", description="Semantic version of tool implementation")
    permission_level: PermissionLevel = Field(default=PermissionLevel.READ_ONLY)
    tags: List[str] = Field(default_factory=list)
    timeout_seconds: float = Field(default=30.0, ge=0.1)
    max_retries: int = Field(default=3, ge=0, le=10)
    requires_approval: bool = Field(default=False, description="True if manual user confirmation is required")
    input_schema_json: Dict[str, Any] = Field(default_factory=dict)
    output_schema_json: Dict[str, Any] = Field(default_factory=dict)


class ToolExecutionRequest(BaseModel):
    """Request payload to execute a specific tool."""
    tool_name: str = Field(..., description="Unique tool identifier name")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Input parameters dictionary")
    request_id: Optional[str] = Field(default=None, description="Optional correlation request UUID")
    workflow_id: Optional[str] = Field(default=None, description="Optional parent workflow UUID")
    timeout_seconds: Optional[float] = Field(default=None, description="Custom timeout override in seconds")
    max_retries: Optional[int] = Field(default=None, description="Custom max retries override")
    approval_granted: bool = Field(default=False, description="True if explicit user approval was granted")


class ToolExecutionResult(BaseModel):
    """Normalized output execution result payload."""
    request_id: Optional[str] = None
    workflow_id: Optional[str] = None
    tool_name: str
    status: ExecutionStatus
    output: Optional[Any] = None
    error_message: Optional[str] = None
    execution_time_seconds: float = 0.0
    retry_count: int = 0
    rolled_back: bool = False
    approval_source: Optional[str] = None

    @property
    def output_data(self) -> Optional[Any]:
        return self.output



class ParallelToolRequest(BaseModel):
    """Batch payload to execute multiple tool requests concurrently."""
    requests: List[ToolExecutionRequest] = Field(..., description="List of individual tool execution requests")


class AuditLogEntry(BaseModel):
    """Structured audit trail record for every tool execution attempt."""
    id: str
    request_id: Optional[str] = None
    workflow_id: Optional[str] = None
    tool_name: str
    user_id: Optional[str] = None
    user_role: str
    permission_level: PermissionLevel
    parameters: Dict[str, Any]
    status: ExecutionStatus
    execution_time_seconds: float
    retry_count: int
    rolled_back: bool
    approval_source: Optional[str] = None
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ToolHealthReport(BaseModel):
    """Health check diagnostic report for registered tools."""
    tool_name: str
    category: str
    healthy: bool
    version: str
    permission_level: PermissionLevel
    error_details: Optional[str] = None
