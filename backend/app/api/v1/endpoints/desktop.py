"""
FastAPI Endpoints for Enterprise Desktop Automation Engine (Sprint 7 & 7.1).
Endpoints: GET /status, GET /windows, GET /processes, POST /action, POST /launch, POST /close, POST /screenshot, POST /ocr, GET /metrics, POST /recorder/start, POST /recorder/stop, GET /approvals, POST /approvals/{id}/respond.
"""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.api.deps import get_current_user
from app.desktop.app_manager import app_manager
from app.desktop.manager import desktop_manager
from app.desktop.metrics import desktop_metrics
from app.desktop.ocr import ocr_engine
from app.desktop.perception import perception_engine
from app.desktop.recorder import RecordedWorkflow, workflow_recorder
from app.desktop.safety import desktop_safety_gatekeeper
from app.desktop.schemas import (
    DesktopActionRequest,
    DesktopActionResponse,
    DesktopActionType,
    HumanApprovalRequest,
    OCRResult,
    ProcessInfo,
    WindowInfo,
)
from app.desktop.window_manager import window_manager
from app.models.user import User

router = APIRouter()


@router.get("/status", summary="Get Desktop Manager Health & Display Status")
async def get_desktop_status(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Returns desktop manager health diagnostics, display monitors, and active session status."""
    return await desktop_manager.get_health_status()


@router.get("/windows", response_model=List[WindowInfo], summary="List Active Desktop Windows")
async def list_windows(
    current_user: User = Depends(get_current_user)
) -> List[WindowInfo]:
    """Lists enumerated visible desktop windows."""
    return window_manager.list_windows()


@router.get("/processes", response_model=List[ProcessInfo], summary="List Running Application Processes")
async def list_processes(
    current_user: User = Depends(get_current_user)
) -> List[ProcessInfo]:
    """Lists running system application processes."""
    return app_manager.list_processes()


@router.post("/action", response_model=DesktopActionResponse, summary="Execute Desktop Automation Action")
async def execute_desktop_action(
    req: DesktopActionRequest,
    current_user: User = Depends(get_current_user)
) -> DesktopActionResponse:
    """Executes mouse, keyboard, window, or clipboard action with Safety Gatekeeper interception."""
    return await desktop_manager.execute_action(req)


@router.post("/launch", response_model=DesktopActionResponse, summary="Launch Desktop Application")
async def launch_application(
    app_name_or_path: str = Query(..., description="Executable path or system alias (e.g. 'code', 'chrome', 'cmd')"),
    current_user: User = Depends(get_current_user)
) -> DesktopActionResponse:
    """Launches a desktop application."""
    req = DesktopActionRequest(action_type=DesktopActionType.LAUNCH_APP, app_name_or_path=app_name_or_path)
    return await desktop_manager.execute_action(req)


@router.post("/close", response_model=DesktopActionResponse, summary="Close Application / Window")
async def close_application(
    app_name_or_path: str = Query(..., description="Executable path or PID to terminate"),
    current_user: User = Depends(get_current_user)
) -> DesktopActionResponse:
    """Terminates an application process or closes window."""
    req = DesktopActionRequest(action_type=DesktopActionType.CLOSE_APP, app_name_or_path=app_name_or_path)
    return await desktop_manager.execute_action(req)


@router.post("/screenshot", summary="Capture Desktop Display Screenshot")
async def capture_screenshot(
    x: int = Query(default=0),
    y: int = Query(default=0),
    width: int = Query(default=1920),
    height: int = Query(default=1080),
    current_user: User = Depends(get_current_user)
):
    """Captures desktop screen or region screenshot as Base64 encoded PNG string."""
    b64 = perception_engine.capture_screen(x=x, y=y, width=width, height=height)
    return {"image_base64": b64}


@router.post("/ocr", response_model=OCRResult, summary="Perform OCR Text Detection")
async def perform_ocr(
    current_user: User = Depends(get_current_user)
) -> OCRResult:
    """Performs OCR text detection on active screen capture display."""
    return ocr_engine.extract_text()


@router.get("/metrics", response_model=Dict[str, Any], summary="Get Desktop Telemetry Metrics")
async def get_desktop_metrics(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Returns telemetry metrics (launches, window ops, input events, OCR latencies)."""
    return desktop_metrics.to_dict()


@router.post("/recorder/start", summary="Start Desktop Workflow Recording")
async def start_recording(
    current_user: User = Depends(get_current_user)
):
    """Starts recording desktop automation steps."""
    workflow_recorder.start_recording()
    return {"message": "Desktop workflow recording started."}


@router.post("/recorder/stop", response_model=RecordedWorkflow, summary="Stop Workflow Recording & Export Script")
async def stop_recording(
    workflow_name: str = Query(default="Recorded_Workflow"),
    current_user: User = Depends(get_current_user)
) -> RecordedWorkflow:
    """Stops workflow recording and exports RecordedWorkflow script."""
    return workflow_recorder.stop_recording(workflow_name)


@router.get("/approvals", response_model=List[HumanApprovalRequest], summary="List Pending High-Risk Approvals")
async def list_pending_approvals(
    current_user: User = Depends(get_current_user)
) -> List[HumanApprovalRequest]:
    """Lists pending human approval tickets for high-risk native desktop actions."""
    return desktop_safety_gatekeeper.list_pending_approvals()


@router.post("/approvals/{approval_id}/respond", response_model=HumanApprovalRequest, summary="Approve or Reject High-Risk Ticket")
async def respond_approval(
    approval_id: str,
    approved: bool = Query(..., description="True to approve execution, False to reject"),
    current_user: User = Depends(get_current_user)
) -> HumanApprovalRequest:
    """Grants authorization or rejects a pending high-risk desktop action ticket."""
    ticket = desktop_safety_gatekeeper.respond_to_approval(approval_id, approved)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Approval ticket '{approval_id}' not found."
        )
    return ticket
