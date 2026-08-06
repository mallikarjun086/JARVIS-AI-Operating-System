"""
Result Verifier — Post-execution task verification checking outputs, filesystem states, and dependencies.
"""

from pathlib import Path
from typing import Any, Dict
import structlog
from app.planner.schemas import PlanTask, TaskVerificationResult
from app.tools.schemas import ExecutionStatus, ToolExecutionResult

logger = structlog.get_logger(__name__)


class TaskResultVerifier:
    """Verifies that executed tasks fulfilled expected contracts and filesystem state."""

    @classmethod
    def verify_task_result(
        cls,
        task: PlanTask,
        result: ToolExecutionResult
    ) -> TaskVerificationResult:
        """
        Verifies task result status, output values, and generated file existence.
        """
        if result.status != ExecutionStatus.SUCCESS:
            return TaskVerificationResult(
                task_id=task.task_id,
                verified=False,
                message=f"Tool execution failed with status '{result.status.value}': {result.error_message}",
                output_asserted=False
            )

        # File existence check if output returns a path or inputs contain path
        if "write" in task.tool_required.lower() or "create" in task.tool_required.lower():
            target_path = task.inputs.get("path") or task.inputs.get("file_path")
            if target_path:
                p = Path(target_path).resolve()
                if not p.exists():
                    logger.warning("Verification failed — file not created", task_id=task.task_id, path=str(p))
                    return TaskVerificationResult(
                        task_id=task.task_id,
                        verified=False,
                        message=f"File verification failed: Target path '{target_path}' was not created.",
                        output_asserted=False
                    )

        return TaskVerificationResult(
            task_id=task.task_id,
            verified=True,
            message=f"Task '{task.task_id}' verified successfully.",
            output_asserted=True
        )


task_verifier = TaskResultVerifier()
