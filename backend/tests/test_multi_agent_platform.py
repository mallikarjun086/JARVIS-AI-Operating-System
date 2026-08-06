"""
Pytest Integration Test Suite for Enterprise Multi-Agent Orchestration Platform (Sprint 9).
Tests BaseAgent Framework, AgentRegistry, CapabilityGraph, TaskScheduler, ExecutionCoordinator, SharedContext, ConsensusEngine, Recovery, and REST APIs.
"""

from httpx import AsyncClient
import pytest

from app.multi_agent.agent_pool import coding_agent, planner_agent, verifier_agent
from app.multi_agent.capability_graph import capability_graph
from app.multi_agent.consensus import consensus_engine
from app.multi_agent.context import shared_context_builder
from app.multi_agent.orchestrator import swarm_orchestrator
from app.multi_agent.recovery import multi_agent_recovery
from app.multi_agent.registry import agent_registry
from app.multi_agent.scheduler import task_scheduler
from app.multi_agent.schemas import AgentRole, SubTaskSpec, TaskStatus


@pytest.mark.asyncio
async def test_agent_registry_and_base_agent():
    """Step 2 & 3: Verifies BaseAgent framework and AgentRegistry methods."""
    registered = agent_registry.list_agents()
    assert len(registered) == 10

    planner = agent_registry.get_by_role(AgentRole.PLANNER)
    assert planner is not None
    assert planner.metadata.agent_id == "agent-planner"

    health = await planner.health_check()
    assert health["status"] == "READY"
    assert health["agent_id"] == "agent-planner"

    all_health = await agent_registry.get_all_health()
    assert len(all_health) == 10


@pytest.mark.asyncio
async def test_capability_graph_dynamic_selection():
    """Step 4: Verifies CapabilityGraph resolves capability queries dynamically."""
    selected_coding = capability_graph.select_agent_for_capability("code_refactoring")
    assert selected_coding is not None
    assert selected_coding.metadata.role == AgentRole.CODING

    selected_browser = capability_graph.select_agent_for_capability("browser_automation")
    assert selected_browser is not None
    assert selected_browser.metadata.role == AgentRole.BROWSER

    mapping = capability_graph.get_capability_mapping()
    assert "web_research" in mapping
    assert "code_refactoring" in mapping


@pytest.mark.asyncio
async def test_task_scheduler_and_parallel_execution():
    """Step 5 & 10: Verifies TaskScheduler parallel batching and dependency graph execution."""
    ctx = shared_context_builder.build_context(user_context={"task": "parallel_test"})

    sub1 = SubTaskSpec(subtask_id="sub_1", required_capability="web_research", goal="Research docs")
    sub2 = SubTaskSpec(subtask_id="sub_2", required_capability="code_refactoring", goal="Refactor module", dependencies=["sub_1"])

    tasks = await task_scheduler.schedule_and_execute_plan([sub1, sub2], ctx)
    assert len(tasks) == 2
    assert tasks[0].status == TaskStatus.COMPLETED
    assert tasks[1].status == TaskStatus.COMPLETED


@pytest.mark.asyncio
async def test_consensus_engine_voting():
    """Step 11: Verifies ConsensusEngine voting and confidence scoring."""
    sub1 = SubTaskSpec(subtask_id="sub_1", goal="Task 1", status=TaskStatus.COMPLETED)
    sub2 = SubTaskSpec(subtask_id="sub_2", goal="Task 2", status=TaskStatus.VERIFIED)

    res = consensus_engine.evaluate_subtask_consensus([sub1, sub2])
    assert res.consensus_passed is True
    assert res.overall_confidence > 0.80
    assert res.total_votes >= 2


@pytest.mark.asyncio
async def test_failure_recovery_circuit_breaker():
    """Step 12: Verifies Circuit Breaker and fallback task reassignment."""
    agent_id = "agent-coding"
    is_open = multi_agent_recovery.record_agent_failure(agent_id)
    assert is_open is False

    multi_agent_recovery.record_agent_failure(agent_id)
    is_open = multi_agent_recovery.record_agent_failure(agent_id)
    assert is_open is True  # 3rd failure opens circuit breaker

    # Test reassignment
    sub = SubTaskSpec(subtask_id="sub_fail", required_capability="code_refactoring", assigned_agent_id=agent_id, goal="Fix code")
    reassigned = await multi_agent_recovery.reassign_failed_task(sub)
    assert reassigned.status in [TaskStatus.PENDING, TaskStatus.FAILED]

    # Reset circuit
    multi_agent_recovery.record_agent_success(agent_id)


@pytest.mark.asyncio
async def test_orchestrator_end_to_end_swarm_goal():
    """Step 6 & 10: Verifies end-to-end MultiAgentOrchestrator goal dispatch."""
    plan = await swarm_orchestrator.dispatch_swarm_goal("Build and verify new microservice module")
    assert plan.plan_id is not None
    assert plan.status in [TaskStatus.VERIFIED, TaskStatus.IN_PROGRESS]
    assert len(plan.tasks) == 4


@pytest.mark.asyncio
async def test_multi_agent_rest_api_endpoints(client: AsyncClient):
    """Step 15: Verifies FastAPI REST endpoints for Multi-Agent Platform."""
    await client.post("/api/v1/auth/register", json={"email": "agent@jarvis.ai", "password": "Password123!", "full_name": "Agent User"})
    login_resp = await client.post("/api/v1/auth/login", data={"username": "agent@jarvis.ai", "password": "Password123!"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. List Agents Endpoint
    agents_resp = await client.get("/api/v1/multi-agent/agents", headers=headers)
    assert agents_resp.status_code == 200
    assert len(agents_resp.json()) == 10

    # 2. Get Agent Health Endpoint
    health_resp = await client.get("/api/v1/multi-agent/agents/health", headers=headers)
    assert health_resp.status_code == 200

    # 3. Get Capabilities Endpoint
    caps_resp = await client.get("/api/v1/multi-agent/agents/capabilities", headers=headers)
    assert caps_resp.status_code == 200
    assert "web_research" in caps_resp.json()

    # 4. Dispatch Swarm Workflow Endpoint
    flow_resp = await client.post("/api/v1/multi-agent/agents/workflow?goal=Verify+Swarm+Workflow", headers=headers)
    assert flow_resp.status_code == 200
    assert "plan_id" in flow_resp.json()

    # 5. Get Metrics Endpoint
    met_resp = await client.get("/api/v1/multi-agent/agents/metrics", headers=headers)
    assert met_resp.status_code == 200
    assert len(met_resp.json()) == 10
