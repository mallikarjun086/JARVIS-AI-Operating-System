"""
Recovery Engine — Failure Recovery, Exponential Retry, Rollback Compensation, and Execution Resumption.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import structlog

from app.planner.schemas import PlanTask, RecoveryPolicy, RecoveryStrategy, SubTaskPriority
from app.tools.executor import execution_manager
from app.tools.schemas import ToolExecutionRequest

logger = structlog.get_logger(__name__)


class RecoveryReport(BaseModel):
    """Diagnostic recovery report following execution error."""
    task_id: str
    strategy_used: RecoveryStrategy
    success: bool
    message: str
    rolled_back_tasks: List[str] = Field(default_factory=list)


class RecoveryEngine:
    """Manages failure recovery policies, retries, and rollback compensations."""

    @classmethod
    def generate_recovery_policies(cls, subtasks: List[PlanTask]) -> List[RecoveryPolicy]:
        """Generates tailored recovery policies based on task priority."""
        policies: List[RecoveryPolicy] = []
        for task in subtasks:
            if task.priority == SubTaskPriority.CRITICAL:
                strat = RecoveryStrategy.RETRY
                backoff = 3.0
            elif task.priority == SubTaskPriority.HIGH:
                strat = RecoveryStrategy.RETRY
                backoff = 2.0
            else:
                strat = RecoveryStrategy.SKIP_NON_CRITICAL
                backoff = 1.0

            policies.append(
                RecoveryPolicy(
                    task_id=task.task_id,
                    strategy=strat,
                    max_retries=task.retry_policy.get("max_retries", 3),
                    backoff_seconds=backoff
                )
            )
        return policies

    @classmethod
    async def execute_rollback(
        cls,
        completed_tasks: List[PlanTask],
        task_outputs: Dict[str, Any],
        user_role: str = "user"
    ) -> List[str]:
        """
        Executes compensation/undo actions for completed tasks in reverse topological order.
        """
        rolled_back: List[str] = []
        reversed_tasks = list(reversed(completed_tasks))

        for task in reversed_tasks:
            if task.rollback_strategy == "NONE":
                continue

            logger.info("Executing task rollback", task_id=task.task_id, tool=task.tool_required)

            # E.g. if file was written, trigger delete_file
            if "write_file" in task.tool_required and "path" in task.inputs:
                rb_req = ToolExecutionRequest(
                    tool_name="filesystem.delete_file",
                    parameters={"path": task.inputs["path"]}
                )
                rb_res = await execution_manager.execute_tool(rb_req, user_role=user_role)
                if rb_res.status.value == "SUCCESS":
                    rolled_back.append(task.task_id)

        return rolled_back


recovery_engine = RecoveryEngine()
recovery_manager = recovery_engine  # Backward-compatible alias
FailureRecoveryManager = RecoveryEngine  # Backward-compatible alias
failure_recovery_manager = recovery_engine

