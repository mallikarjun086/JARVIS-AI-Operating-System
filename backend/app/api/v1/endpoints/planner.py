"""
FastAPI Endpoints for Enterprise Planner & Execution Engine.
Endpoints: POST /plan, POST /execute, GET /history, GET /metrics, GET /{id}, POST /{id}/pause, POST /{id}/resume, POST /{id}/cancel, POST /validate.
"""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.planner.engine import execution_engine
from app.planner.graph import DependencyGraphEngine
from app.planner.metrics import planner_metrics
from app.planner.schemas import (
    DAGValidationResponse,
    ExecutionPlan,
    PlanExecuteRequest,
    PlannerRequest,
    PlanTask,
)

router = APIRouter()


@router.post("/plan", response_model=ExecutionPlan, summary="Generate Execution Plan JSON")
async def create_execution_plan(
    req: PlannerRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ExecutionPlan:
    """
    Converts natural language goal into structured ExecutionPlan JSON.
    Pre-retrieves memory context, runs LLM planning, validates DAG, and generates resource estimates & explanations.
    """
    user_role = "superuser" if current_user.is_superuser else "user"
    return await execution_engine.create_and_validate_plan(
        req=req,
        db=db,
        user_role=user_role,
        user_id=current_user.id
    )


@router.post("/execute", response_model=ExecutionPlan, summary="Execute Validated Plan")
async def execute_plan(
    req: PlanExecuteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ExecutionPlan:
    """
    Executes a validated ExecutionPlan layer-by-layer strictly through Sprint 4 Tool Framework.
    """
    user_role = "superuser" if current_user.is_superuser else "user"
    try:
        return await execution_engine.execute_plan(
            plan_id=req.plan_id,
            db=db,
            user_role=user_role,
            user_id=current_user.id,
            approval_granted=req.approval_granted
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))


@router.get("/history", response_model=List[ExecutionPlan], summary="List Execution Plan History")
async def list_plan_history(
    current_user: User = Depends(get_current_user)
) -> List[ExecutionPlan]:
    """Lists past generated and executed plan instances."""
    return execution_engine.list_history()


@router.get("/metrics", response_model=Dict[str, Any], summary="Get Planner Observability Metrics")
async def get_planner_metrics(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Returns planning latency, execution latency, success rates, retries, rollbacks, and checkpoints."""
    return planner_metrics.to_dict()


@router.post("/validate", response_model=DAGValidationResponse, summary="Validate Subtask DAG Graph")
async def validate_subtask_dag(
    subtasks: List[PlanTask],
    current_user: User = Depends(get_current_user)
) -> DAGValidationResponse:
    """Validates if a list of tasks forms a valid Directed Acyclic Graph (DAG)."""
    return DependencyGraphEngine.validate_and_order_dag(subtasks)


@router.get("/{plan_id}", response_model=ExecutionPlan, summary="Get Execution Plan Status")
async def get_plan_status(
    plan_id: str,
    current_user: User = Depends(get_current_user)
) -> ExecutionPlan:
    """Fetches status, state machine phase, and progress for a specific execution plan."""
    plan = execution_engine.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ExecutionPlan '{plan_id}' not found.")
    return plan


@router.post("/{plan_id}/pause", summary="Pause Active Execution Plan")
async def pause_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user)
):
    """Pauses active plan execution loop."""
    paused = execution_engine.pause_plan(plan_id)
    if not paused:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Active plan '{plan_id}' not found.")
    return {"message": f"ExecutionPlan '{plan_id}' paused successfully."}


@router.post("/{plan_id}/resume", summary="Resume Paused Execution Plan")
async def resume_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user)
):
    """Resumes paused plan execution loop."""
    resumed = execution_engine.resume_plan(plan_id)
    if not resumed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Paused plan '{plan_id}' not found.")
    return {"message": f"ExecutionPlan '{plan_id}' resumed successfully."}


@router.post("/{plan_id}/cancel", summary="Cancel Execution Plan")
async def cancel_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user)
):
    """Cancels execution plan and triggers rollback if needed."""
    cancelled = execution_engine.cancel_plan(plan_id)
    if not cancelled:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Plan '{plan_id}' not found.")
    return {"message": f"ExecutionPlan '{plan_id}' cancellation requested."}
