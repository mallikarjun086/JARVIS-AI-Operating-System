"""
Plan Optimizer — Merges duplicate tasks, prunes redundant steps, and optimizes parallel execution layers.
"""

from typing import List, Set
import structlog
from app.planner.schemas import PlanTask

logger = structlog.get_logger(__name__)


class PlanOptimizer:
    """Optimizes task execution plans to reduce latency and execution cost."""

    @classmethod
    def optimize_plan(cls, subtasks: List[PlanTask]) -> List[PlanTask]:
        """
        Deduplicates identical read operations and optimizes task dependencies.
        """
        seen_signatures: Set[str] = set()
        optimized: List[PlanTask] = []

        for task in subtasks:
            # Generate task signature (tool + inputs)
            sig = f"{task.tool_required}:{sorted(task.inputs.items())}"
            if "read" in task.tool_required.lower() and sig in seen_signatures:
                logger.info("Optimizer pruned duplicate read task", task_id=task.task_id, tool=task.tool_required)
                continue

            seen_signatures.add(sig)
            optimized.append(task)

        return optimized


plan_optimizer = PlanOptimizer()
