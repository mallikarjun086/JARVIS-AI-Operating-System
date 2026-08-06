"""
Multi-Agent Failure Recovery & Circuit Breaker Engine (Sprint 9 Step 12).
Handles agent heartbeats, task reassignment to fallback agents, circuit breaker triggers, and workflow resume/rollback.
"""

from typing import Dict, Optional
import structlog

from app.multi_agent.capability_graph import capability_graph
from app.multi_agent.registry import agent_registry
from app.multi_agent.schemas import AgentStatus, SubTaskSpec, TaskStatus

logger = structlog.get_logger(__name__)


class MultiAgentRecoveryEngine:
    """Circuit breaker and failure recovery engine for multi-agent execution."""

    def __init__(self) -> None:
        self._consecutive_failures: Dict[str, int] = {}
        self._circuit_open: Dict[str, bool] = {}

    def record_agent_failure(self, agent_id: str) -> bool:
        """Records agent failure and opens circuit breaker if failures >= 3."""
        cnt = self._consecutive_failures.get(agent_id, 0) + 1
        self._consecutive_failures[agent_id] = cnt

        if cnt >= 3:
            self._circuit_open[agent_id] = True
            agent = agent_registry.get_agent(agent_id)
            if agent:
                agent.metadata.status = AgentStatus.UNHEALTHY
                agent.metadata.availability = False
            logger.error("Circuit breaker OPEN for failing agent", agent_id=agent_id, failure_count=cnt)
            return True  # Circuit triggered
        return False

    def record_agent_success(self, agent_id: str) -> None:
        """Resets agent failure counter on successful execution."""
        self._consecutive_failures[agent_id] = 0
        self._circuit_open[agent_id] = False
        agent = agent_registry.get_agent(agent_id)
        if agent and agent.metadata.status == AgentStatus.UNHEALTHY:
            agent.metadata.status = AgentStatus.READY
            agent.metadata.availability = True

    async def reassign_failed_task(self, subtask: SubTaskSpec) -> SubTaskSpec:
        """Reassigns a failed task to an alternative fallback agent exposing the capability."""
        logger.info("Attempting task reassignment to fallback agent", subtask_id=subtask.subtask_id)
        candidates = capability_graph.find_candidates_for_capability(subtask.required_capability)
        
        # Filter out current failing agent
        fallbacks = [c for c in candidates if c.metadata.agent_id != subtask.assigned_agent_id]
        if not fallbacks:
            subtask.status = TaskStatus.FAILED
            subtask.error_message = "No fallback agent available for task reassignment."
            return subtask

        fallback_agent = fallbacks[0]
        subtask.assigned_agent = fallback_agent.metadata.role
        subtask.assigned_agent_id = fallback_agent.metadata.agent_id
        subtask.status = TaskStatus.PENDING
        subtask.retry_count += 1
        logger.info("Reassigned task to fallback agent", subtask_id=subtask.subtask_id, fallback_agent=fallback_agent.metadata.agent_id)
        return subtask


multi_agent_recovery = MultiAgentRecoveryEngine()
