"""
Pydantic Schemas for Desktop Automation Subsystem.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field, ConfigDict


class AutomationActionType(str, Enum):
    MOUSE_MOVE = "MOUSE_MOVE"
    MOUSE_CLICK = "MOUSE_CLICK"
    MOUSE_SCROLL = "MOUSE_SCROLL"
    KEY_PRESS = "KEY_PRESS"
    KEY_TYPE = "KEY_TYPE"
    CLIPBOARD_SET = "CLIPBOARD_SET"
    CLIPBOARD_GET = "CLIPBOARD_GET"
    WINDOW_FOCUS = "WINDOW_FOCUS"
    WINDOW_MINIMIZE = "WINDOW_MINIMIZE"
    WINDOW_MAXIMIZE = "WINDOW_MAXIMIZE"
    WINDOW_CLOSE = "WINDOW_CLOSE"
    SCREEN_CAPTURE = "SCREEN_CAPTURE"
    WINDOW_DETECT = "WINDOW_DETECT"
    OCR_TEXT_EXTRACT = "OCR_TEXT_EXTRACT"


class WindowInfo(BaseModel):
    """Information payload for a desktop window."""
    hwnd: int = Field(..., description="Window handle ID")
    title: str = Field(..., description="Window title bar string")
    process_name: str = Field(default="unknown")
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0
    is_active: bool = False


class ScreenCaptureResult(BaseModel):
    """Result payload for screen capture operation."""
    image_base64: str = Field(..., description="PNG image encoded as Base64 string")
    width: int
    height: int
    format: str = "PNG"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class OCRBoundingBox(BaseModel):
    """OCR detected text bounding box."""
    text: str
    x: int
    y: int
    width: int
    height: int
    confidence: float = 0.95


class OCRResult(BaseModel):
    """OCR text extraction result payload."""
    extracted_text: str
    boxes: List[OCRBoundingBox] = Field(default_factory=list)


class AutomationRequest(BaseModel):
    """Request payload for desktop automation action."""
    action_type: AutomationActionType
    parameters: Dict[str, Any] = Field(default_factory=dict)
    require_confirmation: bool = Field(default=False)
    reason: Optional[str] = Field(default=None, description="Explanation for action audit log")


class AutomationResponse(BaseModel):
    """Response payload for desktop automation action."""
    model_config = ConfigDict(from_attributes=True)

    action_id: str = Field(default_factory=lambda: f"act-{uuid.uuid4().hex[:8]}")
    action_type: AutomationActionType
    status: str = "SUCCESS"  # SUCCESS, FAILED, EMERGENCY_STOPPED, CANCELLED
    result: Optional[Any] = None
    error_message: Optional[str] = None
    is_reversible: bool = False
    undo_action_id: Optional[str] = None
    executed_at: datetime = Field(default_factory=datetime.utcnow)


class EmergencyStopStatus(BaseModel):
    """Emergency stop safety status payload."""
    is_emergency_stopped: bool
    triggered_at: Optional[datetime] = None
    reason: Optional[str] = None
