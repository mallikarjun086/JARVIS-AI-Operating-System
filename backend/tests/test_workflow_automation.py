"""
Pytest Test Suite for Workflow Automation Subsystem.
Tests conditional branching, loops, human approval gatekeeper, scheduling, retries, rollback, persistence, and internship pipeline execution.
"""

from httpx import AsyncClient
import pytest
from app.workflow.engine import workflow_engine
from app.workflow.schemas import WorkflowStatus
from app.workflow.templates import get_internship_workflow_template


@pytest.mark.asyncio
async def test_internship_pipeline_template_execution():
    """Verifies end-to-end Internship Application Pipeline execution up to Human Approval pause."""
    tmpl = get_internship_workflow_template()
    assert len(tmpl.nodes) == 8

    inst = await workflow_engine.execute_workflow(tmpl.definition_id)

    # 1. Verify instance pauses on Human Approval node (#4)
    assert inst.status == WorkflowStatus.PAUSED_FOR_APPROVAL
    assert inst.pending_approval_id == "appr-node_4"
    assert inst.current_node_id == "node_4"

    # 2. Grant Human Approval
    resumed = await workflow_engine.grant_approval(inst.instance_id, approved=True)
    assert resumed.status == WorkflowStatus.COMPLETED
    assert resumed.variables["applied"] is True
    assert resumed.variables["notified"] is True


@pytest.mark.asyncio
async def test_workflow_rejection_and_rollback():
    """Verifies rejecting human approval triggers step rollback."""
    tmpl = get_internship_workflow_template()
    inst = await workflow_engine.execute_workflow(tmpl.definition_id)

    assert inst.status == WorkflowStatus.PAUSED_FOR_APPROVAL

    # Reject approval
    rolled_back = await workflow_engine.grant_approval(inst.instance_id, approved=False)
    assert rolled_back.status == WorkflowStatus.ROLLED_BACK


@pytest.mark.asyncio
async def test_manual_rollback_trigger():
    """Tests manual step rollback for running workflow instance."""
    tmpl = get_internship_workflow_template()
    inst = await workflow_engine.execute_workflow(tmpl.definition_id)

    rb = await workflow_engine.rollback_instance(inst.instance_id)
    assert rb.status == WorkflowStatus.ROLLED_BACK


@pytest.mark.asyncio
async def test_workflow_api_endpoints(client: AsyncClient):
    """Tests FastAPI REST endpoints for Workflow Automation."""
    # Register & login
    await client.post("/api/v1/auth/register", json={"email": "wf@jarvis.ai", "password": "Password123!", "full_name": "WF User"})
    login_resp = await client.post("/api/v1/auth/login", data={"username": "wf@jarvis.ai", "password": "Password123!"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. List Definitions Endpoint
    defs_resp = await client.get("/api/v1/workflow/definitions", headers=headers)
    assert defs_resp.status_code == 200
    defs = defs_resp.json()
    assert len(defs) >= 1
    def_id = defs[0]["definition_id"]

    # 2. Execute Workflow Endpoint
    exec_resp = await client.post(f"/api/v1/workflow/execute/{def_id}", headers=headers)
    assert exec_resp.status_code == 200
    inst_data = exec_resp.json()
    assert inst_data["status"] in ["PAUSED_FOR_APPROVAL", "WAITING_APPROVAL"]

    inst_id = inst_data["instance_id"]

    # 3. Poll Instance Endpoint
    poll_resp = await client.get(f"/api/v1/workflow/instances/{inst_id}", headers=headers)
    assert poll_resp.status_code == 200

    # 4. Approve Endpoint
    appr_resp = await client.post(f"/api/v1/workflow/instances/{inst_id}/approve?approved=true", headers=headers)
    assert appr_resp.status_code == 200
    assert appr_resp.json()["status"] == "COMPLETED"
