"""
Multi-Agent Swarm Orchestration Engine (Sprint 9).
Orchestrates task decomposition, parallel execution batching, dynamic capability resolution, shared memory sync, and consensus voting.
"""

import asyncio
from typing import Dict, List, Optional
import structlog

from app.multi_agent.capability_graph import capability_graph
from app.multi_agent.context import shared_context_builder
from app.multi_agent.coordinator import execution_coordinator
from app.multi_agent.agent_pool import agent_pool
from app.multi_agent.registry import agent_registry
from app.multi_agent.schemas import (
    AgentRole,
    AgentTaskTelemetry,
    SubTaskSpec,
    SwarmExecutionPlan,
    TaskStatus,
)
from app.multi_agent.shared_memory import shared_swarm_memory

logger = structlog.get_logger(__name__)


class MultiAgentOrchestrator:
    """Central orchestrator managing 10-agent swarm execution lifecycle."""

    def __init__(self) -> None:
        self._plans: Dict[str, SwarmExecutionPlan] = {}

    async def dispatch_swarm_goal(self, goal: str) -> SwarmExecutionPlan:
        """
        Main entrypoint:
        1. Decomposes goal into specialized subtasks.
        2. Routes through ExecutionCoordinator & TaskScheduler.
        3. Evaluates Consensus Voting quality gate.
        """
        # 1. Decompose Subtasks
        sub1_id = f"sub_1"
        sub2_id = f"sub_2"
        sub3_id = f"sub_3"
        sub4_id = f"sub_4"

        plan = SwarmExecutionPlan(
            goal=goal,
            status=TaskStatus.IN_PROGRESS,
            tasks=[
                SubTaskSpec(subtask_id=sub1_id, required_capability="web_research", assigned_agent=AgentRole.RESEARCH, goal=f"Research requirement specifications for '{goal}'"),
                SubTaskSpec(subtask_id=sub2_id, required_capability="browser_automation", assigned_agent=AgentRole.BROWSER, goal=f"Inspect documentation via Browser for '{goal}'"),
                SubTaskSpec(subtask_id=sub3_id, required_capability="code_refactoring", assigned_agent=AgentRole.CODING, goal=f"Implement software module for '{goal}'", dependencies=[sub1_id, sub2_id]),
                SubTaskSpec(subtask_id=sub4_id, required_capability="quality_verification", assigned_agent=AgentRole.VERIFIER, goal="Quality Gate Consensus Verification", dependencies=[sub3_id])
            ]
        )
        self._plans[plan.plan_id] = plan

        # 2. Build Shared Context & Coordinate Execution
        ctx = shared_context_builder.build_context(user_context={"goal": goal})
        plan, consensus_res = await execution_coordinator.coordinate_plan_execution(plan, ctx)

        plan.shared_memory_snapshot = shared_swarm_memory.get_all_context()
        logger.info("Dispatched and completed swarm plan execution", plan_id=plan.plan_id, status=plan.status.value)
        return plan

    def get_plan(self, plan_id: str) -> Optional[SwarmExecutionPlan]:
        """Retrieves plan state by ID."""
        return self._plans.get(plan_id)

    def list_plans(self) -> List[SwarmExecutionPlan]:
        """Lists active and past swarm execution plans."""
        return list(self._plans.values())

    def get_agent_telemetry(self) -> List[AgentTaskTelemetry]:
        """Returns live performance metrics for all registered agents."""
        telemetry = []
        for meta in agent_registry.list_agents():
            agent = agent_registry.get_agent(meta.agent_id)
            if agent:
                avg_lat = round(agent.total_latency_ms / max(1, agent.completed_count + agent.failed_count), 2)
                telemetry.append(
                    AgentTaskTelemetry(
                        agent_id=meta.agent_id,
                        role=meta.role,
                        completed_count=agent.completed_count,
                        failed_count=agent.failed_count,
                        total_latency_ms=agent.total_latency_ms,
                        avg_latency_ms=avg_lat
                    )
                )
        return telemetry


swarm_orchestrator = MultiAgentOrchestrator()
