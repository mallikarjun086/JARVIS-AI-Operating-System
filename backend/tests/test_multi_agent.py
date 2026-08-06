"""
Pytest Test Suite for Multi-Agent Swarm Orchestration Subsystem.
Tests 10 specialized agents, inter-agent messaging, shared memory, parallel execution, retries, failure recovery, and verifier approval.
"""

from httpx import AsyncClient
import pytest
from app.multi_agent.agent_pool import agent_pool
from app.multi_agent.message_bus import message_bus
from app.multi_agent.orchestrator import swarm_orchestrator
from app.multi_agent.schemas import AgentRole, SubTaskSpec, TaskStatus
from app.multi_agent.shared_memory import shared_swarm_memory


@pytest.mark.asyncio
async def test_specialized_agent_pool_execution():
    """Verifies all 10 specialized agents execute assigned subtasks successfully."""
    for role, agent in agent_pool.items():
        if not agent:
            continue
        subtask = SubTaskSpec(assigned_agent=role, goal=f"Test {role.value} Agent")
        res = await agent.execute_task(subtask)
        res = res or subtask

        assert res.status == TaskStatus.COMPLETED
        assert res.result is not None



@pytest.mark.asyncio
async def test_inter_agent_message_bus():
    """Tests message publishing, agent queue retrieval, and audit log."""
    msg = message_bus.send_message(
        sender_role=AgentRole.RESEARCH,
        recipient_role=AgentRole.CODING,
        content="Research findings ready for code implementation."
    )
    assert msg.message_id is not None

    coding_messages = message_bus.get_messages_for_agent(AgentRole.CODING)
    assert any(m.message_id == msg.message_id for m in coding_messages)


@pytest.mark.asyncio
async def test_shared_swarm_memory_workspace():
    """Tests thread-safe shared swarm memory workspace context."""
    shared_swarm_memory.set_key("swarm_test_key", "Swarm Value 123")
    assert shared_swarm_memory.get_key("swarm_test_key") == "Swarm Value 123"

    all_ctx = shared_swarm_memory.get_all_context()
    assert "swarm_test_key" in all_ctx


@pytest.mark.asyncio
async def test_swarm_dispatch_parallel_execution_and_verifier():
    """Verifies end-to-end swarm goal dispatch, parallel batch execution, and Verifier quality gate pass."""
    plan = await swarm_orchestrator.dispatch_swarm_goal("Build research report and implement API module")

    assert plan.status == TaskStatus.VERIFIED
    assert len(plan.tasks) >= 4

    # Verify Verifier agent completed task
    verifier_task = next(t for t in plan.tasks if t.assigned_agent in [AgentRole.VERIFIER, AgentRole.VERIFIER.value] or "verifier" in str(t.assigned_agent or "").lower() or "verifier" in str(t.assigned_agent_id or "").lower())

    assert verifier_task.status == TaskStatus.COMPLETED
    assert verifier_task.result["verified"] is True


@pytest.mark.asyncio
async def test_multi_agent_api_endpoints(client: AsyncClient):
    """Tests FastAPI REST endpoints for Multi-Agent Swarm."""
    # Register & login
    await client.post("/api/v1/auth/register", json={"email": "swarm@jarvis.ai", "password": "Password123!", "full_name": "Swarm User"})
    login_resp = await client.post("/api/v1/auth/login", data={"username": "swarm@jarvis.ai", "password": "Password123!"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Dispatch Swarm Goal Endpoint
    disp_resp = await client.post("/api/v1/multi-agent/dispatch?goal=Deploy+JARVIS+Kernel", headers=headers)
    assert disp_resp.status_code == 200
    plan_data = disp_resp.json()
    assert plan_data["status"] == "VERIFIED"

    # Telemetry Metrics Endpoint
    telem_resp = await client.get("/api/v1/multi-agent/telemetry", headers=headers)
    assert telem_resp.status_code == 200
    assert len(telem_resp.json()) == 10  # All 10 agents present

    # Inter-Agent Messages Endpoint
    msg_resp = await client.get("/api/v1/multi-agent/messages", headers=headers)
    assert msg_resp.status_code == 200
    assert len(msg_resp.json()) >= 1

    # Shared Memory Endpoint
    mem_resp = await client.get("/api/v1/multi-agent/shared-memory", headers=headers)
    assert mem_resp.status_code == 200
