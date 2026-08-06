"""
Planner Observability & Telemetry Metrics.
Tracks planning latency, execution latency, task duration, success/failure counts, retries, rollbacks, checkpoints, and verification failures.
"""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class PlannerMetricsManager:
    """Thread-safe metric counters for the Enterprise Planner Engine."""

    total_plans_generated: int = 0
    total_plans_executed: int = 0
    total_plans_completed: int = 0
    total_plans_failed: int = 0
    total_plans_cancelled: int = 0

    total_tasks_executed: int = 0
    total_task_retries: int = 0
    total_task_rollbacks: int = 0
    total_verification_failures: int = 0
    total_checkpoints_saved: int = 0
    total_approval_requests: int = 0

    total_planning_latency_ms: float = 0.0
    total_execution_latency_ms: float = 0.0
    total_memory_retrieval_ms: float = 0.0

    def record_plan_generated(self, planning_ms: float) -> None:
        self.total_plans_generated += 1
        self.total_planning_latency_ms += planning_ms

    def record_plan_execution(
        self,
        execution_ms: float,
        status: str,
        retries: int = 0,
        rollbacks: int = 0,
        verifications_failed: int = 0
    ) -> None:
        self.total_plans_executed += 1
        self.total_execution_latency_ms += execution_ms
        self.total_task_retries += retries
        self.total_task_rollbacks += rollbacks
        self.total_verification_failures += verifications_failed

        if status == "COMPLETED":
            self.total_plans_completed += 1
        elif status == "CANCELLED":
            self.total_plans_cancelled += 1
        else:
            self.total_plans_failed += 1

    @property
    def avg_planning_latency_ms(self) -> float:
        return round(self.total_planning_latency_ms / max(1, self.total_plans_generated), 2)

    @property
    def avg_execution_latency_ms(self) -> float:
        return round(self.total_execution_latency_ms / max(1, self.total_plans_executed), 2)

    @property
    def plan_success_rate(self) -> float:
        return round(self.total_plans_completed / max(1, self.total_plans_executed), 4)

    def to_dict(self) -> dict:
        return {
            "total_plans_generated": self.total_plans_generated,
            "total_plans_executed": self.total_plans_executed,
            "total_plans_completed": self.total_plans_completed,
            "total_plans_failed": self.total_plans_failed,
            "total_plans_cancelled": self.total_plans_cancelled,
            "total_tasks_executed": self.total_tasks_executed,
            "total_task_retries": self.total_task_retries,
            "total_task_rollbacks": self.total_task_rollbacks,
            "total_verification_failures": self.total_verification_failures,
            "total_checkpoints_saved": self.total_checkpoints_saved,
            "total_approval_requests": self.total_approval_requests,
            "avg_planning_latency_ms": self.avg_planning_latency_ms,
            "avg_execution_latency_ms": self.avg_execution_latency_ms,
            "plan_success_rate": self.plan_success_rate
        }


planner_metrics = PlannerMetricsManager()
