"""
Tool Framework Telemetry & Observability Metrics.
Tracks tool execution counts, success/failure rates, average runtimes, timeouts, retries, and registered tools.
"""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class ToolMetricsManager:
    """Thread-safe metric counters for the Tool Framework."""

    total_executions: int = 0
    total_successes: int = 0
    total_failures: int = 0
    total_permission_denied: int = 0
    total_validation_errors: int = 0
    total_timeouts: int = 0
    total_retries: int = 0
    total_rollbacks: int = 0

    total_execution_time_seconds: float = 0.0

    # Per-tool breakdown
    tool_executions: Dict[str, int] = field(default_factory=dict)
    tool_failures: Dict[str, int] = field(default_factory=dict)
    tool_runtimes_seconds: Dict[str, float] = field(default_factory=dict)

    def record_execution(
        self,
        tool_name: str,
        status_value: str,
        elapsed_seconds: float,
        retry_count: int = 0,
        rolled_back: bool = False
    ) -> None:
        """Records execution statistics."""
        self.total_executions += 1
        self.total_execution_time_seconds += elapsed_seconds
        self.total_retries += retry_count

        if rolled_back:
            self.total_rollbacks += 1

        self.tool_executions[tool_name] = self.tool_executions.get(tool_name, 0) + 1
        self.tool_runtimes_seconds[tool_name] = self.tool_runtimes_seconds.get(tool_name, 0.0) + elapsed_seconds

        if status_value == "SUCCESS":
            self.total_successes += 1
        elif status_value == "PERMISSION_DENIED":
            self.total_permission_denied += 1
            self.total_failures += 1
            self.tool_failures[tool_name] = self.tool_failures.get(tool_name, 0) + 1
        elif status_value == "VALIDATION_ERROR":
            self.total_validation_errors += 1
            self.total_failures += 1
            self.tool_failures[tool_name] = self.tool_failures.get(tool_name, 0) + 1
        elif status_value == "TIMEOUT":
            self.total_timeouts += 1
            self.total_failures += 1
            self.tool_failures[tool_name] = self.tool_failures.get(tool_name, 0) + 1
        else:
            self.total_failures += 1
            self.tool_failures[tool_name] = self.tool_failures.get(tool_name, 0) + 1

    @property
    def success_rate(self) -> float:
        return round(self.total_successes / max(1, self.total_executions), 4)

    @property
    def failure_rate(self) -> float:
        return round(self.total_failures / max(1, self.total_executions), 4)

    @property
    def avg_runtime_seconds(self) -> float:
        return round(self.total_execution_time_seconds / max(1, self.total_executions), 4)

    def to_dict(self, registered_tools_count: int = 0, active_tools_count: int = 0) -> dict:
        """Returns structured metrics summary dictionary."""
        return {
            "total_executions": self.total_executions,
            "total_successes": self.total_successes,
            "total_failures": self.total_failures,
            "total_permission_denied": self.total_permission_denied,
            "total_validation_errors": self.total_validation_errors,
            "total_timeouts": self.total_timeouts,
            "total_retries": self.total_retries,
            "total_rollbacks": self.total_rollbacks,
            "success_rate": self.success_rate,
            "failure_rate": self.failure_rate,
            "avg_runtime_seconds": self.avg_runtime_seconds,
            "registered_tools": registered_tools_count,
            "active_tools": active_tools_count,
            "per_tool_executions": self.tool_executions,
            "per_tool_failures": self.tool_failures,
        }


tool_metrics = ToolMetricsManager()
