"""
Strongly Typed ExecutionContext for Enterprise Planner & Execution Engine.
Carries correlation IDs, security privileges, user roles, approval tokens, and telemetry context.
"""

import uuid
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ExecutionContext(BaseModel):
    """
    Strongly typed ExecutionContext passed to every task execution.
    """
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: Optional[str] = None
    execution_id: str = Field(default_factory=lambda: f"exec-{uuid.uuid4().hex[:8]}")
    conversation_id: Optional[str] = None
    memory_session_id: Optional[str] = None
    user_id: Optional[str] = None
    user_role: str = Field(default="user")
    agent_id: str = Field(default="planner_agent")
    approval_token: Optional[str] = None
    approval_granted: bool = Field(default=False)
    execution_mode: str = Field(default="STANDARD")
    security_context: Dict[str, Any] = Field(default_factory=dict)
    planner_version: str = Field(default="5.1.0")

    def to_tool_context(self) -> Dict[str, Any]:
        """Converts ExecutionContext into context dictionary passed to Tool Framework."""
        return {
            "request_id": self.request_id,
            "workflow_id": self.workflow_id,
            "execution_id": self.execution_id,
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
            "user_role": self.user_role,
            "agent_id": self.agent_id,
            "approval_token": self.approval_token,
            "approval_granted": self.approval_granted,
            "security_context": self.security_context,
            "planner_version": self.planner_version,
        }
