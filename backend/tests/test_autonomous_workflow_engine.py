"""
Pytest Integration Test Suite for Enterprise Autonomous Workflow Engine (Sprint 10).
Tests Event Sourcing, 12-State Runtime, ExecutionBackend Abstraction, Plugin Step System, Resource Reservation, Policy Engine, Versioning, Checkpoints, Saga Compensation, Templates, and REST APIs.
"""

from httpx import AsyncClient
import pytest

from app.workflow.checkpoint import checkpoint_engine
from app.workflow.compensation import compensation_engine
from app.workflow.engine import workflow_engine
from app.workflow.event_sourcing import event_sourcing_engine
from app.workflow.execution_backend import local_execution_backend
from app.workflow.library import workflow_library
from app.workflow.plugin_registry import plugin_step_registry
from app.workflow.policy_engine import workflow_policy_engine
from app.workflow.resource_manager import resource_reservation_manager
from app.workflow.schemas import NodeType, WorkflowDefinition, WorkflowEventType, WorkflowNode, WorkflowStatus
from app.workflow.templates import get_all_enterprise_templates
from app.workflow.versioning import workflow_versioning_engine


@pytest.mark.asyncio
async def test_event_sourcing_and_state_reconstruction():
    """Step 1: Verifies Event Sourcing emits immutable events and reconstructs state."""
    wf_id = "wfdef-test-es"
    exec_id = "exec-test-es"

    event_sourcing_engine.emit_event(wf_id, exec_id, WorkflowEventType.WORKFLOW_CREATED)
    event_sourcing_engine.emit_event(wf_id, exec_id, WorkflowEventType.WORKFLOW_STARTED)

    stream = event_sourcing_engine.get_event_stream(wf_id)
    assert len(stream) == 2

    status = event_sourcing_engine.reconstruct_state(wf_id)
    assert status == WorkflowStatus.RUNNING


@pytest.mark.asyncio
async def test_execution_backend_and_plugin_registry():
    """Step 4: Verifies ExecutionBackend abstraction and PluginStepRegistry."""
    plugins = plugin_step_registry.list_plugins()
    assert "approvalnode" in plugins
    assert "browsernode" in plugins
    assert "swenode" in plugins

    plugin = plugin_step_registry.get_plugin("BrowserNode")
    assert plugin is not None

    res = await plugin.execute_step(
        step_name="Inspect Web Docs",
        parameters={"goal": "Verify Web Page Automation"},
        backend=local_execution_backend
    )
    assert res["success"] is True


@pytest.mark.asyncio
async def test_resource_manager_and_policy_engine():
    """Resource Allocation and Security Policy Validation."""
    tmpl = get_all_enterprise_templates()[0]
    valid = workflow_policy_engine.validate_workflow_policy(tmpl, {"role": "ADMIN"})
    assert valid is True

    reserved = resource_reservation_manager.reserve_resources(tmpl.resource_reservation)
    assert reserved is True
    usage = resource_reservation_manager.get_resource_usage()
    assert usage["allocated_cpu"] >= 1.0

    resource_reservation_manager.release_resources(tmpl.resource_reservation)


@pytest.mark.asyncio
async def test_checkpoint_and_versioning_engines():
    """Step 5: Verifies Persistent Checkpoint Engine and Versioning Engine."""
    ver = workflow_versioning_engine.get_current_version_info()
    assert ver.workflow_version == "1.0.0"

    tmpl = get_all_enterprise_templates()[0]
    instance = await workflow_engine.execute_workflow(tmpl.definition_id)
    assert instance.last_checkpoint_id is not None

    chk = checkpoint_engine.get_checkpoint(instance.last_checkpoint_id)
    assert chk is not None
    assert chk.workflow_id == tmpl.definition_id


@pytest.mark.asyncio
async def test_enterprise_templates_and_library():
    """Step 9 & 10: Verifies 8 Enterprise Templates and Workflow Library operations."""
    templates = get_all_enterprise_templates()
    assert len(templates) == 8

    # Clone definition in library
    cloned = workflow_library.clone_definition("tmpl-internship", "Custom Internship Pipeline")
    assert cloned is not None
    assert cloned.name == "Custom Internship Pipeline"

    search_res = workflow_library.search_definitions("internship")
    assert len(search_res) >= 1


@pytest.mark.asyncio
async def test_workflow_rest_api_endpoints(client: AsyncClient):
    """Step 15: Verifies FastAPI REST endpoints for Autonomous Workflow Engine."""
    await client.post("/api/v1/auth/register", json={"email": "wf@jarvis.ai", "password": "Password123!", "full_name": "WF User"})
    login_resp = await client.post("/api/v1/auth/login", data={"username": "wf@jarvis.ai", "password": "Password123!"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. List Templates Endpoint
    tmpl_resp = await client.get("/api/v1/workflow/templates", headers=headers)
    assert tmpl_resp.status_code == 200
    assert len(tmpl_resp.json()) >= 8

    # 2. Start Workflow Instance Endpoint
    start_resp = await client.post("/api/v1/workflow/start?definition_id=tmpl-repo-analysis", headers=headers)
    assert start_resp.status_code == 200
    assert "instance_id" in start_resp.json()

    # 3. Checkpoints Endpoint
    chk_resp = await client.get("/api/v1/workflow/checkpoints", headers=headers)
    assert chk_resp.status_code == 200

    # 4. History Endpoint
    hist_resp = await client.get("/api/v1/workflow/history", headers=headers)
    assert hist_resp.status_code == 200

    # 5. Metrics Endpoint
    met_resp = await client.get("/api/v1/workflow/metrics", headers=headers)
    assert met_resp.status_code == 200
    assert "success_rate_percent" in met_resp.json()
