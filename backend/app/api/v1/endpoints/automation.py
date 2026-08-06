"""
FastAPI Endpoints for Desktop Automation Subsystem.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_current_user
from app.automation.manager import automation_manager
from app.automation.perception import perception_engine
from app.automation.safety import safety_engine
from app.automation.schemas import (
    AutomationRequest,
    AutomationResponse,
    EmergencyStopStatus,
    OCRResult,
    ScreenCaptureResult,
    WindowInfo,
)
from app.models.user import User

router = APIRouter()


@router.post("/execute", response_model=AutomationResponse, summary="Execute Desktop Automation Action")
async def execute_desktop_action(
    req: AutomationRequest,
    current_user: User = Depends(get_current_user)
) -> AutomationResponse:
    """Executes mouse, keyboard, clipboard, or window automation action with safety checks."""
    return await automation_manager.execute_action(req)


@router.post("/undo/{action_id}", summary="Revert Reversible Action")
async def undo_desktop_action(
    action_id: str,
    current_user: User = Depends(get_current_user)
):
    """Reverts a previously logged reversible action back to its pre-execution state."""
    success = await safety_engine.execute_undo(action_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reversible action '{action_id}' not found or already undone."
        )
    return {"message": f"Action '{action_id}' successfully reverted."}


@router.post("/emergency-stop", response_model=EmergencyStopStatus, summary="Trigger Safety Emergency Stop Switch")
async def trigger_emergency_stop(
    reason: str = "User panic button triggered.",
    current_user: User = Depends(get_current_user)
) -> EmergencyStopStatus:
    """Instantly aborts running operations and halts all automation actions."""
    safety_engine.trigger_emergency_stop(reason=reason)
    return safety_engine.get_emergency_status()


@router.post("/resume", response_model=EmergencyStopStatus, summary="Resume Automation Operation")
async def resume_automation(
    current_user: User = Depends(get_current_user)
) -> EmergencyStopStatus:
    """Resumes automation operation after emergency stop."""
    safety_engine.resume_operation()
    return safety_engine.get_emergency_status()


@router.get("/windows", response_model=List[WindowInfo], summary="List Active Desktop Windows")
async def list_windows(
    current_user: User = Depends(get_current_user)
) -> List[WindowInfo]:
    """Enumerates open desktop windows, handle IDs (HWND), titles, and coordinates."""
    return perception_engine.detect_open_windows()


@router.post("/screen-capture", response_model=ScreenCaptureResult, summary="Take Screen Capture")
async def take_screen_capture(
    current_user: User = Depends(get_current_user)
) -> ScreenCaptureResult:
    """Captures screen buffer and returns Base64 PNG image."""
    return perception_engine.capture_screen()


@router.post("/ocr", response_model=OCRResult, summary="Perform OCR Text Extraction")
async def extract_ocr_text(
    current_user: User = Depends(get_current_user)
) -> OCRResult:
    """Extracts text and bounding box locations from screen capture buffer."""
    return perception_engine.extract_ocr_text()
