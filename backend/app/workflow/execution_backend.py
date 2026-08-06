"""
ExecutionBackend Abstraction (Sprint 10).
Abstract ExecutionBackend interface decoupling Workflow Runtime from FastAPI and tool framework details.
Workflow Runtime MUST depend on this abstraction.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import structlog

logger = structlog.get_logger(__name__)


class ExecutionBackend(ABC):
    """Abstract interface for workflow step execution backends."""

    @abstractmethod
    async def dispatch_step_task(
        self,
        goal: str,
        capability: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Dispatches step task execution through execution provider."""
        pass


class LocalExecutionBackend(ExecutionBackend):
    """Default local execution backend dispatching tasks through MultiAgentOrchestrator."""

    async def dispatch_step_task(
        self,
        goal: str,
        capability: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Dispatches step goal through Multi-Agent Orchestrator."""
        logger.info("LocalExecutionBackend dispatching step goal to MultiAgentOrchestrator", goal=goal, capability=capability)
        try:
            from app.multi_agent.orchestrator import swarm_orchestrator
            plan = await swarm_orchestrator.dispatch_swarm_goal(goal)
            return {
                "success": plan.status.value in ["VERIFIED", "COMPLETED", "IN_PROGRESS"],
                "plan_id": plan.plan_id,
                "status": plan.status.value,
                "goal": goal
            }
        except Exception as e:
            logger.error("LocalExecutionBackend step dispatch error", goal=goal, error=str(e))
            return {"success": False, "error": str(e), "goal": goal}


local_execution_backend = LocalExecutionBackend()
