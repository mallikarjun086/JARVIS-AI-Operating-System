"""
Pytest Test Suite for Intelligent Task Planner & DAG Execution Graph.
"""

from httpx import AsyncClient
import pytest
from app.planner.decomposer import TaskDecomposer
from app.planner.graph import DependencyGraphEngine
from app.planner.recovery import FailureRecoveryManager
from app.planner.schemas import SubTask, SubTaskPriority


@pytest.mark.asyncio
async def test_spring_boot_intent_decomposition():
    """Verifies intent decomposition for Spring Boot + GitHub goal."""
    intent, tasks = await TaskDecomposer.decompose_goal("Create a Spring Boot project and push to GitHub.")

    assert "Spring Boot" in str(intent) or "Spring Boot" in getattr(intent, "primary_goal", "") or getattr(intent, "category", "") == "software_development"

    assert len(tasks) == 5
    assert tasks[0].id == "task_1"
    assert tasks[-1].id == "task_5"
    assert tasks[-1].priority == SubTaskPriority.CRITICAL


@pytest.mark.asyncio
async def test_dag_topological_order_and_parallel_batches():
    """Verifies Kahn's algorithm topological sorting and parallel batch grouping."""
    t1 = SubTask(id="task_1", title="T1", description="", priority=SubTaskPriority.HIGH, dependencies=[])
    t2 = SubTask(id="task_2", title="T2", description="", priority=SubTaskPriority.HIGH, dependencies=["task_1"])
    t3 = SubTask(id="task_3", title="T3", description="", priority=SubTaskPriority.NORMAL, dependencies=["task_1"])
    t4 = SubTask(id="task_4", title="T4", description="", priority=SubTaskPriority.CRITICAL, dependencies=["task_2", "task_3"])

    dag_info = DependencyGraphEngine.validate_and_order_dag([t1, t2, t3, t4])

    assert dag_info.is_valid_dag is True
    assert dag_info.topological_order == ["task_1", "task_2", "task_3", "task_4"] or dag_info.topological_order == ["task_1", "task_3", "task_2", "task_4"]

    batches = DependencyGraphEngine.build_execution_batches([t1, t2, t3, t4])
    assert len(batches) == 3
    assert batches[0].parallel_task_ids == ["task_1"]
    assert set(batches[1].parallel_task_ids) == {"task_2", "task_3"}  # Parallel Batch!
    assert batches[2].parallel_task_ids == ["task_4"]


@pytest.mark.asyncio
async def test_circular_dependency_detection():
    """Verifies detection and rejection of circular dependency loops."""
    c1 = SubTask(id="t_a", title="A", description="", dependencies=["t_b"])
    c2 = SubTask(id="t_b", title="B", description="", dependencies=["t_a"])

    dag_info = DependencyGraphEngine.validate_and_order_dag([c1, c2])

    assert dag_info.is_valid_dag is False
    assert len(dag_info.circular_dependencies) > 0


@pytest.mark.asyncio
async def test_failure_recovery_policies():
    """Verifies recovery strategy generation per task priority."""
    t_crit = SubTask(id="tc", title="C", description="", priority=SubTaskPriority.CRITICAL)
    t_norm = SubTask(id="tn", title="N", description="", priority=SubTaskPriority.NORMAL)

    policies = FailureRecoveryManager.generate_recovery_policies([t_crit, t_norm])
    assert len(policies) == 2
    assert policies[0].strategy.value == "RETRY"
    assert policies[1].strategy.value == "SKIP_NON_CRITICAL"


@pytest.mark.asyncio
async def test_planner_api_endpoints(client: AsyncClient):
    """Tests /api/v1/planner/plan REST API endpoint."""
    # Register & login
    await client.post("/api/v1/auth/register", json={"email": "planuser@jarvis.ai", "password": "Password123!", "full_name": "Planner User"})
    login_resp = await client.post("/api/v1/auth/login", data={"username": "planuser@jarvis.ai", "password": "Password123!"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Generate Plan
    plan_payload = {"goal": "Create a Spring Boot project and push to GitHub."}
    p_resp = await client.post("/api/v1/planner/plan", json=plan_payload, headers=headers)
    assert p_resp.status_code == 200
    plan_data = p_resp.json()

    assert plan_data["is_valid_dag"] is True
    assert len(plan_data["subtasks"]) == 5
    assert len(plan_data["execution_graph"]) >= 3
    assert len(plan_data["recovery_policies"]) == 5
