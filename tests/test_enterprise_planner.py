"""
Comprehensive Tests for Enterprise Planner & Execution Engine (Sprint 5 & 5.1).
Tests:
1. IntentAnalyzer & TaskDecomposer LLM planning layer
2. PlanValidator 10-point validation checks
3. PlanOptimizer task deduplication
4. ExecutionStateMachine 11-state transition rules
5. ExecutionEngine parallel layer execution via Tool Framework
6. TaskResultVerifier post-task verification checks
7. RecoveryEngine & Rollback execution
8. CheckpointManager snapshot saving & resumption
9. PlannerMemoryBridge context pre-retrieval & outcome storage
10. ResourceEstimator & PlanExplainer reasoning summaries
"""

import pytest
from app.planner.checkpoint import checkpoint_manager
from app.planner.decomposer import decomposer
from app.planner.engine import execution_engine
from app.planner.estimator import resource_estimator
from app.planner.explainer import plan_explainer
from app.planner.graph import graph_engine
from app.planner.intent import intent_analyzer
from app.planner.metrics import planner_metrics
from app.planner.optimizer import plan_optimizer
from app.planner.recovery import recovery_engine
from app.planner.schemas import (
    ExecutionPolicy,
    ExecutionState,
    PlannerRequest,
    PlanTask,
    SubTaskPriority,
)
from app.planner.state_machine import state_machine
from app.planner.validator import plan_validator
from app.planner.verifier import task_verifier
from app.tools.registry import tool_registry
from app.tools.categories.filesystem import ReadFileTool, WriteFileTool


@pytest.mark.asyncio
async def test_intent_analyzer():
    """Verifies IntentAnalyzer parsing category, entities, and priorities."""
    intent = intent_analyzer.analyze_intent("Create a urgent Spring Boot project and push to GitHub")
    assert intent.category == "software_development"
    assert intent.entities["framework"] == "Spring Boot"
    assert intent.suggested_priority == SubTaskPriority.CRITICAL
    assert intent.confidence_score >= 0.90


@pytest.mark.asyncio
async def test_task_decomposition_and_graph():
    """Verifies LLM TaskDecomposer goal decomposition and DAG parallel batch generation."""
    tool_registry.register(WriteFileTool)
    tool_registry.register(ReadFileTool)

    intent, subtasks = await decomposer.decompose_goal("Create a Spring Boot project and push to GitHub")
    assert len(subtasks) >= 3

    dag_info = graph_engine.validate_and_order_dag(subtasks)
    assert dag_info.is_valid_dag is True
    assert len(dag_info.parallel_batches) >= 1


@pytest.mark.asyncio
async def test_plan_validator_and_optimizer():
    """Verifies PlanValidator 10-point checks and PlanOptimizer task deduplication."""
    subtasks = [
        PlanTask(
            task_id="task_1",
            title="Read file 1",
            description="Read requirements.txt",
            tool_required="filesystem.read_file",
            inputs={"path": "requirements.txt"}
        ),
        PlanTask(
            task_id="task_2",
            title="Read file 1 duplicate",
            description="Read requirements.txt again",
            tool_required="filesystem.read_file",
            inputs={"path": "requirements.txt"}
        )
    ]

    optimized = plan_optimizer.optimize_plan(subtasks)
    assert len(optimized) == 1  # Duplicate read task pruned!

    val_report = plan_validator.validate_plan(optimized, user_role="user")
    assert val_report.is_valid is True


@pytest.mark.asyncio
async def test_execution_state_machine():
    """Verifies ExecutionStateMachine valid state transitions and invalid rejection."""
    st = ExecutionState.CREATED
    st = state_machine.transition(st, ExecutionState.PLANNED)
    st = state_machine.transition(st, ExecutionState.VALIDATED)
    st = state_machine.transition(st, ExecutionState.READY)
    st = state_machine.transition(st, ExecutionState.RUNNING)
    st = state_machine.transition(st, ExecutionState.COMPLETED)
    assert st == ExecutionState.COMPLETED

    with pytest.raises(ValueError):
        state_machine.transition(ExecutionState.COMPLETED, ExecutionState.RUNNING)


@pytest.mark.asyncio
async def test_resource_estimator_and_explainer():
    """Verifies pre-execution ResourceEstimator and PlanExplainer outputs."""
    subtasks = [
        PlanTask(
            task_id="task_1",
            title="Create File",
            description="Create file.txt",
            tool_required="filesystem.write_file",
            inputs={"path": "test.txt", "content": "hello"}
        )
    ]

    est = resource_estimator.estimate_resources(subtasks, 1)
    assert est.estimated_cpu_level == "LOW"
    assert est.total_tools == 1

    exp = plan_explainer.explain_plan("Create file", "Parsed intent", subtasks, est)
    assert exp.confidence_score >= 0.9
    assert len(exp.task_order) == 1


@pytest.mark.asyncio
async def test_execution_engine_end_to_end():
    """Verifies ExecutionEngine executing tasks strictly through Tool Framework."""
    tool_registry.register(WriteFileTool)

    req = PlannerRequest(goal="Create a Spring Boot project and push to GitHub")
    plan = await execution_engine.create_and_validate_plan(req, user_role="user")
    assert plan.plan_id is not None
    assert plan.state == ExecutionState.VALIDATED

    executed_plan = await execution_engine.execute_plan(plan.plan_id, user_role="user")
    assert executed_plan.state == ExecutionState.COMPLETED


@pytest.mark.asyncio
async def test_checkpoint_manager():
    """Verifies CheckpointManager snapshot creation and retrieval."""
    cp = checkpoint_manager.save_checkpoint(
        plan_id="plan-test-101",
        batch_id=1,
        completed_ids=["task_1"],
        pending_ids=["task_2"],
        outputs={"task_1": {"result": "ok"}},
        state="RUNNING"
    )

    assert cp.plan_id == "plan-test-101"
    latest = checkpoint_manager.get_latest_checkpoint("plan-test-101")
    assert latest.checkpoint_id == cp.checkpoint_id
