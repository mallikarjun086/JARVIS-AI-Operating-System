"""
Resource Estimator — Computes pre-execution resource consumption metrics.
Estimates CPU, Memory, Disk, Network, Runtime, and max permission level.
"""

from typing import List
from app.planner.schemas import PlanTask, ResourceEstimate
from app.tools.registry import tool_registry
from app.tools.schemas import PermissionLevel


class ResourceEstimator:
    """Computes pre-execution resource metrics for an ExecutionPlan."""

    @classmethod
    def estimate_resources(cls, subtasks: List[PlanTask], parallel_batches_count: int) -> ResourceEstimate:
        """Estimates resource requirements across all tasks in the plan."""
        total_runtime = sum(t.estimated_runtime_seconds for t in subtasks)
        max_perm = PermissionLevel.READ_ONLY
        network_calls = 0
        disk_ops = 0

        for t in subtasks:
            tool = tool_registry.get_tool(t.tool_required)
            if tool:
                if tool.permission_level > max_perm:
                    max_perm = tool.permission_level
                if tool.category == "network":
                    network_calls += 1
                elif tool.category in ("filesystem", "git"):
                    disk_ops += 1
            else:
                if t.permission_level > max_perm:
                    max_perm = t.permission_level

        # Compute estimated CPU level
        if parallel_batches_count > 3 or len(subtasks) > 8:
            cpu_level = "HIGH"
            memory_mb = 256.0
        elif parallel_batches_count > 1 or len(subtasks) > 3:
            cpu_level = "MEDIUM"
            memory_mb = 128.0
        else:
            cpu_level = "LOW"
            memory_mb = 64.0

        return ResourceEstimate(
            estimated_cpu_level=cpu_level,
            estimated_memory_mb=memory_mb,
            estimated_network_calls=network_calls,
            estimated_disk_ops=disk_ops,
            estimated_runtime_seconds=round(total_runtime, 1),
            total_tools=len(subtasks),
            parallel_batches=parallel_batches_count,
            max_permission_level=max_perm
        )


resource_estimator = ResourceEstimator()
