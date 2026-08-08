"""
Automated Pytest Suite for JARVIS Unified Multimodal Command Center.
Validates:
1. Synchronous natural language command execution & intent routing (POST /api/v1/jarvis/execute).
2. Conversation session history persistence (last 20 interactions).
3. Risk evaluation & high-risk operator approval gate (POST /api/v1/jarvis/approve).
4. SSE Streaming generator events (GET /api/v1/jarvis/stream).
"""

import pytest
import pytest_asyncio

from app.jarvis.orchestrator import jarvis_orchestrator
from app.jarvis.schemas import ApprovalDecision, CommandRiskLevel, JarvisCommandRequest


@pytest.mark.asyncio
async def test_jarvis_orchestrator_low_risk_execution():
    """Validates low-risk natural language command execution and step generation."""
    req = JarvisCommandRequest(
        command="Build microservice REST API for user order processing",
        session_id="test_sess_01",
        voice_input=False
    )
    resp = await jarvis_orchestrator.execute_command(req=req, user_role="user")

    assert resp.status == "COMPLETED"
    assert resp.session_id == "test_sess_01"
    assert len(resp.steps) == 4
    assert resp.steps[0].agent_role == "MEMORY"
    assert resp.steps[1].agent_role == "PLANNER"
    assert resp.steps[3].agent_role == "VERIFIER"
    assert resp.generated_code is not None
    assert "APIRouter" in resp.generated_code


@pytest.mark.asyncio
async def test_jarvis_session_history_persistence():
    """Validates conversation memory persistence for the last 20 interactions."""
    session_id = "test_persistence_sess"
    for i in range(25):
        req = JarvisCommandRequest(command=f"Interaction task {i}", session_id=session_id)
        await jarvis_orchestrator.execute_command(req)

    history = jarvis_orchestrator.get_session_history(session_id, limit=20)
    assert len(history) == 20
    assert "Interaction task 24" in history[-1]["user"]


@pytest.mark.asyncio
async def test_jarvis_high_risk_approval_gate():
    """Validates RBAC approval gate requirement and operator authorization decision."""
    req = JarvisCommandRequest(
        command="Delete database table and shutdown server",
        session_id="approval_test_sess"
    )
    resp = await jarvis_orchestrator.execute_command(req=req, user_role="user")

    assert resp.status == "REQUIRES_APPROVAL"
    assert resp.risk_level == CommandRiskLevel.CRITICAL
    assert resp.approval_required is not None

    approval_id = resp.approval_required.approval_id

    # Test rejection
    rej_decision = ApprovalDecision(approval_id=approval_id, approved=False, reason="Denied by test runner")
    rej_res = jarvis_orchestrator.process_approval_decision(rej_decision)
    assert rej_res["status"] == "REJECTED"


@pytest.mark.asyncio
async def test_jarvis_sse_streaming():
    """Validates Server-Sent Events (SSE) streaming execution events generator."""
    events = []
    async for chunk in jarvis_orchestrator.stream_command_execution(command="Test research query", session_id="stream_sess"):
        events.append(chunk)

    assert len(events) >= 5
    assert "START" in events[0]
    assert "COMPLETE" in events[-1]
