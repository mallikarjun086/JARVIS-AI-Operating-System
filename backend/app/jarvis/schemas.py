"""
Pydantic Schemas for JARVIS Unified Command Center & Orchestration Engine.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CommandRiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class JarvisCommandRequest(BaseModel):
    command: str = Field(..., description="Natural language command or prompt from user")
    session_id: Optional[str] = Field(default=None, description="Optional conversation session ID")
    voice_input: bool = Field(default=False, description="Whether command originated from speech STT")
    auto_execute: bool = Field(default=True, description="Whether to execute subtasks automatically")
    bypass_approval: bool = Field(default=False, description="Whether superuser bypassed approval gate")


class ApprovalRequestPayload(BaseModel):
    approval_id: str
    command: str
    risk_level: CommandRiskLevel
    action_summary: str
    target_tool: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class ApprovalDecision(BaseModel):
    approval_id: str
    approved: bool
    reason: Optional[str] = None


class JarvisExecutionStepEvent(BaseModel):
    step_id: int
    agent_role: str
    title: str
    status: str  # PENDING, RUNNING, COMPLETED, FAILED, REQUIRES_APPROVAL
    message: str
    details: Optional[Dict[str, Any]] = None
    latency_ms: float = 0.0


class JarvisCommandResponse(BaseModel):
    session_id: str
    command: str
    status: str  # COMPLETED, REQUIRES_APPROVAL, FAILED
    response_text: str
    risk_level: CommandRiskLevel
    steps: List[JarvisExecutionStepEvent] = []
    approval_required: Optional[ApprovalRequestPayload] = None
    generated_code: Optional[str] = None
    memories_retrieved: int = 0
    total_execution_ms: float = 0.0
