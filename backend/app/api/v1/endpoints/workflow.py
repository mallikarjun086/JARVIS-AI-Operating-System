"""
FastAPI Endpoints for Enterprise Autonomous Workflow Engine (Sprint 10).
Endpoints: /workflow/create, /workflow/start, /workflow/pause, /workflow/resume, /workflow/cancel, /workflow/retry, /workflow/{id}, /workflow/history, /workflow/templates, /workflow/metrics, /workflow/checkpoints.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from app.api.deps import get_current_user
from app.models.user import User
from app.workflow.checkpoint import checkpoint_engine
from app.workflow.engine import workflow_engine
from app.workflow.event_sourcing import event_sourcing_engine
from app.workflow.library import workflow_library
from app.workflow.resource_manager import resource_reservation_manager
from app.workflow.schemas import (
    WorkflowCheckpoint,
    WorkflowDefinition,
    WorkflowEvent,
    WorkflowInstance,
)

router = APIRouter()


@router.post("/create", response_model=WorkflowDefinition, summary="Create Workflow Definition Blueprint")
async def create_workflow_definition(
    wf_def: WorkflowDefinition,
    current_user: User = Depends(get_current_user)
) -> WorkflowDefinition:
    """Registers custom workflow definition in WorkflowLibrary."""
    return workflow_engine.create_definition(wf_def)


@router.post("/definitions", response_model=WorkflowDefinition, summary="Create Definition (Backward Compatible)")
async def create_workflow_definition_alias(
    wf_def: WorkflowDefinition,
    current_user: User = Depends(get_current_user)
) -> WorkflowDefinition:
    """Backward compatible alias for creating workflow definitions."""
    return workflow_engine.create_definition(wf_def)



@router.post("/start", response_model=WorkflowInstance, summary="Start Workflow Instance Execution")
async def start_workflow_instance(
    definition_id: str = Query(default="tmpl-internship", description="Blueprint definition ID"),
    current_user: User = Depends(get_current_user)
) -> WorkflowInstance:
    """Triggers 12-state workflow execution through PolicyEngine, Versioning, and Event Sourcing."""
    try:
        return await workflow_engine.execute_workflow(definition_id, user_context={"role": "ADMIN"})
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))


@router.post("/execute/{definition_id}", response_model=WorkflowInstance, summary="Execute Workflow (Backward Compatible)")
async def execute_workflow_by_id(
    definition_id: str = Path(..., description="Blueprint definition ID"),
    current_user: User = Depends(get_current_user)
) -> WorkflowInstance:
    """Execute workflow by definition_id URL path parameter."""
    try:
        return await workflow_engine.execute_workflow(definition_id, user_context={"role": "ADMIN"})
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))


@router.get("/templates", response_model=List[WorkflowDefinition], summary="List Enterprise Workflow Templates")
async def list_workflow_templates(
    current_user: User = Depends(get_current_user)
) -> List[WorkflowDefinition]:
    """Lists 8 pre-built enterprise workflow templates and registered definitions."""
    return workflow_engine.list_definitions()


@router.get("/definitions", response_model=List[WorkflowDefinition], summary="List Definitions (Backward Compatible)")
async def list_workflow_definitions_alias(
    current_user: User = Depends(get_current_user)
) -> List[WorkflowDefinition]:
    """Backward compatible alias for listing registered workflow definitions."""
    return workflow_engine.list_definitions()



@router.get("/checkpoints", response_model=List[WorkflowCheckpoint], summary="Get Persistent Checkpoints")
async def list_checkpoints(
    current_user: User = Depends(get_current_user)
) -> List[WorkflowCheckpoint]:
    """Retrieves list of saved persistent snapshot checkpoints."""
    return checkpoint_engine.list_checkpoints()


@router.get("/history", summary="Get Event Sourced Workflow History")
async def get_workflow_history(
    workflow_id: Optional[str] = Query(default=None, description="Filter by workflow definition ID"),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Retrieves immutable event streams and execution logs."""
    if workflow_id:
        events = event_sourcing_engine.get_event_stream(workflow_id)
        return {"workflow_id": workflow_id, "events": [e.model_dump() for e in events]}
    return {"all_streams_count": len(event_sourcing_engine._streams)}


@router.get("/metrics", summary="Get Workflow Runtime Metrics")
async def get_workflow_metrics(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Returns workflow runtime performance metrics and allocated resource usage."""
    instances = workflow_engine.list_instances()
    completed = sum(1 for i in instances if i.status.value == "COMPLETED")
    failed = sum(1 for i in instances if i.status.value in ["FAILED", "ROLLED_BACK"])

    return {
        "total_instances": len(instances),
        "completed_count": completed,
        "failed_count": failed,
        "success_rate_percent": round((completed / max(1, completed + failed)) * 100.0, 2),
        "total_checkpoints_saved": len(checkpoint_engine._checkpoints),
        "resource_allocation": resource_reservation_manager.get_resource_usage()
    }


@router.get("/{instance_id}", response_model=WorkflowInstance, summary="Get Workflow Instance by ID")
async def get_workflow_instance(
    instance_id: str,
    current_user: User = Depends(get_current_user)
) -> WorkflowInstance:
    """Polls workflow instance execution state by ID."""
    inst = workflow_engine.get_instance(instance_id)
    if not inst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workflow instance '{instance_id}' not found.")
    return inst


@router.get("/instances/{instance_id}", response_model=WorkflowInstance, summary="Get Instance (Backward Compatible)")
async def get_workflow_instance_alias(
    instance_id: str,
    current_user: User = Depends(get_current_user)
) -> WorkflowInstance:
    """Backward compatible alias for getting workflow instance state by ID."""
    inst = workflow_engine.get_instance(instance_id)
    if not inst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workflow instance '{instance_id}' not found.")
    return inst



@router.post("/instances/{instance_id}/approve", response_model=WorkflowInstance, summary="Respond to Human Approval Gate")
async def respond_workflow_approval(
    instance_id: str,
    approved: bool = Query(..., description="True to approve, False to reject and trigger Saga rollback"),
    current_user: User = Depends(get_current_user)
) -> WorkflowInstance:
    """Grants human approval or triggers Saga compensation rollback."""
    try:
        return await workflow_engine.grant_approval(instance_id, approved)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))


@router.post("/instances/{instance_id}/rollback", response_model=WorkflowInstance, summary="Trigger Saga Compensation Rollback")
async def rollback_workflow_instance(
    instance_id: str,
    current_user: User = Depends(get_current_user)
) -> WorkflowInstance:
    """Triggers manual Saga compensation rollback chain."""
    try:
        return await workflow_engine.rollback_instance(instance_id)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
