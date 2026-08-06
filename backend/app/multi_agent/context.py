"""
SharedContext Builder for Multi-Agent Platform (Sprint 9 Step 8).
Constructs immutable, thread-safe SharedContextPayload objects passed to every executing agent.
Contains WorkflowContext, ExecutionContext, MemoryContext, SecurityContext, PlannerContext, UserContext, ApprovalContext.
"""

from typing import Any, Dict, List, Optional
from app.multi_agent.schemas import SharedContextPayload


class SharedContextBuilder:
    """Builder creating immutable shared context for multi-agent workflows."""

    @classmethod
    def build_context(
        cls,
        user_id: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None,
        planner_context: Optional[Dict[str, Any]] = None,
        memory_context: Optional[List[str]] = None,
        security_context: Optional[Dict[str, Any]] = None,
        approval_context: Optional[Dict[str, Any]] = None
    ) -> SharedContextPayload:
        """Constructs SharedContextPayload."""
        return SharedContextPayload(
            user_id=user_id,
            user_context=user_context or {},
            planner_context=planner_context or {},
            memory_context=memory_context or [],
            security_context=security_context or {"permissions": "NORMAL"},
            approval_context=approval_context or {}
        )


shared_context_builder = SharedContextBuilder()
