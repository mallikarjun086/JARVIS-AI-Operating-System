"""
Unified Telemetry Manager for Enterprise AI Operating System (Sprint 7.5).
Aggregates latencies, uptime, subsystem counts, success rates, retry rates, and recoveries across all operational layers.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict
import time


@dataclass
class SystemTelemetryManager:
    """Central Telemetry Collector aggregating operational metrics for all 7 subsystems."""

    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


    # Subsystem counters
    planner_plans_executed: int = 0
    planner_failures: int = 0
    memory_queries: int = 0
    memory_stores: int = 0
    tool_executions: int = 0
    tool_failures: int = 0
    browser_navigations: int = 0
    desktop_actions: int = 0
    llm_api_calls: int = 0
    security_gatekeeper_approvals: int = 0
    total_recoveries: int = 0
    total_rollbacks: int = 0

    # Latency accumulators (in milliseconds)
    planner_latency_ms: float = 0.0
    memory_latency_ms: float = 0.0
    browser_latency_ms: float = 0.0
    desktop_latency_ms: float = 0.0
    llm_latency_ms: float = 0.0

    def record_planner_execution(self, latency_ms: float, success: bool = True) -> None:
        self.planner_plans_executed += 1
        if not success:
            self.planner_failures += 1
        self.planner_latency_ms += latency_ms

    def record_memory_operation(self, is_store: bool, latency_ms: float) -> None:
        if is_store:
            self.memory_stores += 1
        else:
            self.memory_queries += 1
        self.memory_latency_ms += latency_ms

    def record_tool_execution(self, latency_ms: float, success: bool = True) -> None:
        self.tool_executions += 1
        if not success:
            self.tool_failures += 1

    def record_browser_operation(self, latency_ms: float) -> None:
        self.browser_navigations += 1
        self.browser_latency_ms += latency_ms

    def record_desktop_operation(self, latency_ms: float) -> None:
        self.desktop_actions += 1
        self.desktop_latency_ms += latency_ms

    def record_llm_call(self, latency_ms: float) -> None:
        self.llm_api_calls += 1
        self.llm_latency_ms += latency_ms

    def record_recovery(self) -> None:
        self.total_recoveries += 1

    @property
    def uptime_seconds(self) -> float:
        return round((datetime.now(timezone.utc) - self.start_time).total_seconds(), 2)


    @property
    def overall_success_rate(self) -> float:
        total_ops = self.planner_plans_executed + self.tool_executions
        if total_ops == 0:
            return 100.0
        failures = self.planner_failures + self.tool_failures
        return round((max(0, total_ops - failures) / total_ops) * 100.0, 2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uptime_seconds": self.uptime_seconds,
            "overall_success_rate": self.overall_success_rate,
            "counts": {
                "planner_plans_executed": self.planner_plans_executed,
                "planner_failures": self.planner_failures,
                "memory_queries": self.memory_queries,
                "memory_stores": self.memory_stores,
                "tool_executions": self.tool_executions,
                "tool_failures": self.tool_failures,
                "browser_navigations": self.browser_navigations,
                "desktop_actions": self.desktop_actions,
                "llm_api_calls": self.llm_api_calls,
                "security_gatekeeper_approvals": self.security_gatekeeper_approvals,
                "total_recoveries": self.total_recoveries,
                "total_rollbacks": self.total_rollbacks,
            },
            "avg_latencies_ms": {
                "planner": round(self.planner_latency_ms / max(1, self.planner_plans_executed), 2),
                "memory": round(self.memory_latency_ms / max(1, self.memory_queries + self.memory_stores), 2),
                "browser": round(self.browser_latency_ms / max(1, self.browser_navigations), 2),
                "desktop": round(self.desktop_latency_ms / max(1, self.desktop_actions), 2),
                "llm": round(self.llm_latency_ms / max(1, self.llm_api_calls), 2),
            }
        }


system_telemetry = SystemTelemetryManager()
