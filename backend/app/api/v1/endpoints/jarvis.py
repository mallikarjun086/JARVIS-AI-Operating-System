"""
FastAPI Endpoints for JARVIS Unified Multimodal Command Center.
Endpoints:
- POST /jarvis/execute — Synchronous unified command execution & intent routing
- GET /jarvis/stream — Server-Sent Events (SSE) streaming execution updates
- POST /jarvis/approve — High-risk command operator approval gate decision
- GET /jarvis/history — Session conversation memory persistence (last 20 interactions)
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from app.api.deps import get_current_user
from app.jarvis.orchestrator import jarvis_orchestrator
from app.jarvis.schemas import (
    ApprovalDecision,
    JarvisCommandRequest,
    JarvisCommandResponse,
)
from app.models.user import User

router = APIRouter()


@router.post("/execute", response_model=JarvisCommandResponse, summary="Execute Multimodal Natural Language Command")
async def execute_command(
    req: JarvisCommandRequest,
    current_user: User = Depends(get_current_user)
) -> JarvisCommandResponse:
    """
    Executes a natural language command by routing it through the Task Planner DAG,
    10-Agent Swarm, Vector Memory Vault, and Tool Registry. Enforces RBAC & Approval Gates.
    """
    user_role = "superuser" if current_user.is_superuser else "user"
    return await jarvis_orchestrator.execute_command(
        req=req,
        user_id=str(current_user.id),
        user_role=user_role
    )


@router.get("/stream", summary="Stream Execution Updates via Server-Sent Events (SSE)")
async def stream_command(
    command: str = Query(..., description="Natural language command prompt"),
    session_id: Optional[str] = Query(default=None, description="Optional session ID"),
    current_user: User = Depends(get_current_user)
):
    """
    Streams real-time step execution updates using Server-Sent Events (SSE).
    """
    user_role = "superuser" if current_user.is_superuser else "user"
    return StreamingResponse(
        jarvis_orchestrator.stream_command_execution(command=command, session_id=session_id, user_role=user_role),
        media_type="text/event-stream"
    )


@router.post("/approve", summary="Authorize or Reject High-Risk Action")
async def approve_command(
    decision: ApprovalDecision,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Processes operator approval authorization or rejection for pending high-risk commands.
    """
    return jarvis_orchestrator.process_approval_decision(decision)


@router.get("/history", summary="Get Conversation History Persistence (Last 20 Interactions)")
async def get_history(
    session_id: str = Query(..., description="Session ID to retrieve history for"),
    limit: int = Query(default=20, ge=1, le=50, description="Max history limit"),
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    Retrieves persisted conversation interactions for target session (up to 20 interactions).
    """
    return jarvis_orchestrator.get_session_history(session_id=session_id, limit=limit)
