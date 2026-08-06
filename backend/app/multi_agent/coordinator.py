"""
Swarm Execution Coordinator (Sprint 9 Step 6).
Coordinates task distribution, progress reporting, verification routing, consensus evaluation, and rollback.
"""

from typing import Any, Dict, List, Optional, Tuple
import structlog

from app.multi_agent.consensus import consensus_engine
from app.multi_agent.context import shared_context_builder
from app.multi_agent.recovery import multi_agent_recovery
from app.multi_agent.scheduler import task_scheduler
from app.multi_agent.schemas import ConsensusResult, SharedContextPayload, SubTaskSpec, SwarmExecutionPlan, TaskStatus

logger = structlog.get_logger(__name__)


class ExecutionCoordinator:
    """Coordinates task distribution, verification, and failure recovery across specialized agents."""

    @classmethod
    async def coordinate_plan_execution(
        cls,
        plan: SwarmExecutionPlan,
        context: Optional[SharedContextPayload] = None
    ) -> Tuple[SwarmExecutionPlan, ConsensusResult]:
        """
        Coordinates full plan execution:
        1. Builds SharedContextPayload.
        2. Executes subtasks via TaskScheduler.
        3. Evaluates quality consensus via ConsensusEngine.
        4. Triggers failure recovery/rollback if consensus fails.
        """
        ctx = context or shared_context_builder.build_context()
        plan.status = TaskStatus.IN_PROGRESS
        logger.info("Coordinator starting swarm plan execution", plan_id=plan.plan_id, total_tasks=len(plan.tasks))

        # 1. Schedule & Execute Tasks
        executed_tasks = await task_scheduler.schedule_and_execute_plan(plan.tasks, ctx)
        plan.tasks = executed_tasks

        # Check for failures and attempt recovery reassignment
        for task in plan.tasks:
            if task.status == TaskStatus.FAILED and task.assigned_agent_id:
                multi_agent_recovery.record_agent_failure(task.assigned_agent_id)
                # Attempt reassignment
                task = await multi_agent_recovery.reassign_failed_task(task)

        # 2. Evaluate Consensus Quality Gate
        consensus_res = consensus_engine.evaluate_subtask_consensus(plan.tasks)

        if consensus_res.consensus_passed:
            plan.status = TaskStatus.VERIFIED
        else:
            plan.status = TaskStatus.REJECTED
            logger.warning("Swarm plan execution rejected by consensus quality gate", plan_id=plan.plan_id)

        return plan, consensus_res


execution_coordinator = ExecutionCoordinator()
