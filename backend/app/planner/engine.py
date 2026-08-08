"""
Enterprise Execution Engine & Orchestrator.
Executes plan tasks layer-by-layer strictly through Sprint 4 Tool Framework (ToolExecutionManager).
Enforces ExecutionState transitions, ExecutionPolicy rules, Checkpointing, Verifiers, and Memory storage.
"""

import asyncio
import hashlib
import json
import time
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.planner.checkpoint import checkpoint_manager
from app.planner.context import ExecutionContext
from app.planner.decomposer import decomposer
from app.planner.explainer import plan_explainer
from app.planner.estimator import resource_estimator
from app.planner.graph import graph_engine
from app.planner.memory_bridge import memory_bridge
from app.planner.metrics import planner_metrics
from app.planner.optimizer import plan_optimizer
from app.planner.recovery import recovery_engine
from app.planner.schemas import (
    ExecutionPolicy,
    ExecutionState,
    ExecutionPlan,
    PlannerRequest,
    PlanTask,
)
from app.planner.state_machine import state_machine
from app.planner.validator import plan_validator
from app.planner.verifier import task_verifier
from app.tools.executor import execution_manager
from app.tools.schemas import ToolExecutionRequest

logger = structlog.get_logger(__name__)


class ExecutionEngine:
    """
    Central Execution Engine managing the lifecycle of ExecutionPlan instances.
    """

    def __init__(self) -> None:
        self._plans: Dict[str, ExecutionPlan] = {}  # {plan_id -> ExecutionPlan}
        self._task_outputs: Dict[str, Dict[str, Any]] = {}  # {plan_id -> {task_id -> output}}
        self._pause_events: Dict[str, asyncio.Event] = {}  # {plan_id -> Event}
        self._cancel_flags: Dict[str, bool] = {}  # {plan_id -> bool}

    async def create_plan(self, goal: str, **kwargs: Any) -> ExecutionPlan:
        """Backward-compatible create_plan helper."""
        return await self.create_and_validate_plan(goal=goal, **kwargs)

    async def create_and_validate_plan(

        self,
        req: Optional[PlannerRequest | str] = None,
        db: Optional[AsyncSession] = None,
        user_role: str = "user",
        user_id: Optional[str] = None,
        **kwargs: Any
    ) -> ExecutionPlan:
        """Full 8-stage plan generation pipeline."""
        if req is None:
            goal_str = kwargs.get("goal") or kwargs.get("title") or "Default execution plan goal"
            req = PlannerRequest(goal=goal_str)
        elif isinstance(req, str):
            req = PlannerRequest(goal=req)
        start_time = time.time()



        mem_context = []
        if db:
            mem_context = await memory_bridge.retrieve_context_memories(db, req.goal, user_id=user_id)

        intent, raw_subtasks = await decomposer.decompose_goal(req.goal, req.system_context, mem_context)
        subtasks = plan_optimizer.optimize_plan(raw_subtasks)
        batches = graph_engine.build_execution_batches(subtasks)
        dag_info = graph_engine.validate_and_order_dag(subtasks)
        val_report = plan_validator.validate_plan(subtasks, user_role=user_role)

        estimate = resource_estimator.estimate_resources(subtasks, len(batches))
        explanation = plan_explainer.explain_plan(req.goal, intent.primary_goal, subtasks, estimate)

        checksum_src = f"{req.goal}:{[t.task_id for t in subtasks]}"
        checksum = hashlib.sha256(checksum_src.encode("utf-8")).hexdigest()[:16]

        plan = ExecutionPlan(
            goal=req.goal,
            intent_summary=intent.primary_goal,
            generated_by_model="gpt-3.5-turbo",
            subtasks=subtasks,
            execution_graph=batches,
            topological_order=dag_info.topological_order,
            state=ExecutionState.CREATED,
            policy=req.execution_policy,
            is_valid_dag=dag_info.is_valid_dag,
            resource_estimate=estimate,
            explanation=explanation,
            checksum=checksum,
            recovery_policies=recovery_engine.generate_recovery_policies(subtasks)
        )

        plan.state = state_machine.transition(plan.state, ExecutionState.PLANNED)
        if val_report.is_valid:
            target_state = ExecutionState.WAITING_APPROVAL if val_report.approval_required else ExecutionState.VALIDATED
            plan.state = state_machine.transition(plan.state, target_state)
        else:
            plan.state = state_machine.transition(plan.state, ExecutionState.FAILED)

        planning_ms = (time.time() - start_time) * 1000.0
        planner_metrics.record_plan_generated(planning_ms)

        self._plans[plan.plan_id] = plan
        return plan

    create_plan_async = create_and_validate_plan

    def create_plan(self, goal: str = "Default Goal", **kwargs: Any) -> ExecutionPlan:
        """Synchronous create_plan helper for task planner integration."""
        title = kwargs.get("title", goal)
        goal_str = kwargs.get("goal", goal)
        plan_id = f"plan-{uuid.uuid4().hex[:8]}"
        plan = ExecutionPlan(
            plan_id=plan_id,
            goal=goal_str,
            intent_summary=title,
            state=ExecutionState.CREATED,
            subtasks=[]
        )
        plan.state = ExecutionState.PLANNED



        self._plans[plan_id] = plan
        return plan




    async def execute_plan(
        self,
        plan_id: str,
        db: Optional[AsyncSession] = None,
        user_role: str = "user",
        user_id: Optional[str] = None,
        approval_granted: bool = False
    ) -> ExecutionPlan:
        """
        Executes an ExecutionPlan layer-by-layer strictly through Sprint 4 Tool Framework.
        """
        plan = self._plans.get(plan_id)
        if not plan:
            raise ValueError(f"ExecutionPlan '{plan_id}' not found.")

        # State transition READY -> RUNNING
        if plan.state == ExecutionState.WAITING_APPROVAL and approval_granted:
            plan.state = state_machine.transition(plan.state, ExecutionState.READY)
        elif plan.state == ExecutionState.VALIDATED:
            plan.state = state_machine.transition(plan.state, ExecutionState.READY)

        plan.state = state_machine.transition(plan.state, ExecutionState.RUNNING)
        start_time = time.time()

        exec_ctx = ExecutionContext(
            user_id=user_id,
            user_role=user_role,
            approval_granted=approval_granted
        )

        task_map = {t.task_id: t for t in plan.subtasks}
        completed_task_ids: List[str] = []
        completed_tasks_list: List[PlanTask] = []
        outputs: Dict[str, Any] = {}

        self._task_outputs[plan_id] = outputs
        self._cancel_flags[plan_id] = False
        pause_event = asyncio.Event()
        pause_event.set()  # Unpaused initially
        self._pause_events[plan_id] = pause_event

        retries_total = 0
        rollbacks_total = 0
        verifications_failed = 0

        # Process execution batches
        for batch in plan.execution_graph:
            # Check Cancellation
            if self._cancel_flags.get(plan_id, False):
                plan.state = state_machine.transition(plan.state, ExecutionState.CANCELLED)
                break

            # Check Pause
            await pause_event.wait()

            # Save Checkpoint
            pending_ids = [t.task_id for t in plan.subtasks if t.task_id not in completed_task_ids]
            checkpoint_manager.save_checkpoint(
                plan_id=plan.plan_id,
                batch_id=batch.batch_id,
                completed_ids=completed_task_ids,
                pending_ids=pending_ids,
                outputs=outputs,
                state=plan.state.value
            )

            # Build Tool Execution Requests for parallel tasks in this batch layer
            batch_tasks = [task_map[tid] for tid in batch.parallel_task_ids if tid in task_map]
            tool_requests = [
                ToolExecutionRequest(
                    tool_name=t.tool_required,
                    parameters=t.inputs,
                    request_id=f"{plan.plan_id}-{t.task_id}",
                    workflow_id=plan.plan_id,
                    timeout_seconds=t.estimated_runtime_seconds * 10,
                    approval_granted=approval_granted
                )
                for t in batch_tasks
            ]

            # Execute batch concurrently via Tool Framework!
            results = await execution_manager.execute_parallel(
                tool_requests,
                context=exec_ctx.to_tool_context(),
                user_role=user_role,
                user_id=user_id
            )

            # Process task results & verifications
            batch_failed = False
            for t, res in zip(batch_tasks, results):
                retries_total += res.retry_count

                # Result Verifier
                ver_res = task_verifier.verify_task_result(t, res)
                if not ver_res.verified:
                    verifications_failed += 1
                    logger.warning("Task verification failed", task_id=t.task_id, message=ver_res.message)
                    if not t.is_optional:
                        batch_failed = True

                if res.status.value == "SUCCESS" and ver_res.verified:
                    completed_task_ids.append(t.task_id)
                    completed_tasks_list.append(t)
                    outputs[t.task_id] = res.output

            if batch_failed:
                if plan.policy == ExecutionPolicy.FAIL_FAST:
                    plan.state = state_machine.transition(plan.state, ExecutionState.ROLLING_BACK)
                    rb_ids = await recovery_engine.execute_rollback(completed_tasks_list, outputs, user_role=user_role)
                    rollbacks_total += len(rb_ids)
                    plan.state = state_machine.transition(plan.state, ExecutionState.FAILED)
                    break

        if plan.state == ExecutionState.RUNNING:
            plan.state = state_machine.transition(plan.state, ExecutionState.COMPLETED)

        elapsed_ms = (time.time() - start_time) * 1000.0
        planner_metrics.record_plan_execution(
            execution_ms=elapsed_ms,
            status=plan.state.value,
            retries=retries_total,
            rollbacks=rollbacks_total,
            verifications_failed=verifications_failed
        )

        # Store in Memory Engine
        if db:
            await memory_bridge.store_execution_outcome(db=db, plan=plan, success=(plan.state == ExecutionState.COMPLETED), user_id=user_id)

        return plan

    def get_plan(self, plan_id: str) -> Optional[ExecutionPlan]:
        return self._plans.get(plan_id)

    def list_history(self) -> List[ExecutionPlan]:
        return list(self._plans.values())

    def pause_plan(self, plan_id: str) -> bool:
        if plan_id in self._pause_events:
            self._pause_events[plan_id].clear()
            plan = self._plans.get(plan_id)
            if plan and plan.state == ExecutionState.RUNNING:
                plan.state = state_machine.transition(plan.state, ExecutionState.PAUSED)
            return True
        return False

    def resume_plan(self, plan_id: str) -> bool:
        if plan_id in self._pause_events:
            self._pause_events[plan_id].set()
            plan = self._plans.get(plan_id)
            if plan and plan.state == ExecutionState.PAUSED:
                plan.state = state_machine.transition(plan.state, ExecutionState.RUNNING)
            return True
        return False

    def cancel_plan(self, plan_id: str) -> bool:
        if plan_id in self._cancel_flags:
            self._cancel_flags[plan_id] = True
            if plan_id in self._pause_events:
                self._pause_events[plan_id].set()  # Unpause so loop terminates
            return True
        return False


execution_engine = ExecutionEngine()
TaskPlannerEngine = ExecutionEngine
TaskPlanner = ExecutionEngine
task_planner = execution_engine

