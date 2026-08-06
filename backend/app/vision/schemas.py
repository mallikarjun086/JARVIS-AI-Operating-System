"""
Pydantic Schemas for Computer Vision Subsystem.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field, ConfigDict


class UIElementType(str, Enum):
    BUTTON = "BUTTON"
    INPUT_FIELD = "INPUT_FIELD"
    TEXT_LABEL = "TEXT_LABEL"
    CHECKBOX = "CHECKBOX"
    IMAGE = "IMAGE"
    CONTAINER = "CONTAINER"
    MENU = "MENU"
    ICON = "ICON"


class BoundingBox(BaseModel):
    """Bounding Box geometry coordinates."""
    x_min: int = Field(..., description="Top-left X coordinate")
    y_min: int = Field(..., description="Top-left Y coordinate")
    x_max: int = Field(..., description="Bottom-right X coordinate")
    y_max: int = Field(..., description="Bottom-right Y coordinate")
    width: int
    height: int


class DetectedUIElement(BaseModel):
    """Detected UI Element container with clickability score and layout hierarchy."""
    element_id: str = Field(default_factory=lambda: f"elem-{uuid.uuid4().hex[:8]}")
    element_type: UIElementType
    label: str
    bounding_box: BoundingBox
    confidence: float = Field(default=0.95, ge=0.0, le=1.0)
    is_clickable: bool = True
    clickability_score: float = Field(default=0.92, ge=0.0, le=1.0, description="Heuristic clickability score")
    visual_hierarchy_path: str = Field(default="root/canvas/element", description="DOM/visual layout hierarchy path")


class ScreenSegment(BaseModel):
    """Screen layout semantic region segment."""
    segment_id: str = Field(default_factory=lambda: f"seg-{uuid.uuid4().hex[:8]}")
    region_type: str  # HEADER, SIDEBAR, MAIN_CANVAS, FOOTER, POPUP_MODAL
    bounds: BoundingBox
    element_count: int = 0


class VisionReasoningResult(BaseModel):
    """Multi-modal visual scene reasoning output."""
    scene_description: str
    active_window_title: str = "JARVIS Desktop"
    recommended_actions: List[Dict[str, Any]] = Field(default_factory=list)
    confidence: float = 0.98


class VisionMemoryRecord(BaseModel):
    """Vision memory snapshot log."""
    record_id: str = Field(default_factory=lambda: f"vmem-{uuid.uuid4().hex[:8]}")
    image_hash: str
    scene_summary: str
    extracted_text: str
    element_count: int
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))



class VisionAnalysisRequest(BaseModel):
    """Request payload for vision analysis."""
    image_base64: Optional[str] = Field(default=None, description="Base64 PNG screenshot string")
    task_goal: Optional[str] = Field(default=None, description="Target action goal prompt")


class VisionAnalysisResponse(BaseModel):
    """Response payload for computer vision analysis."""
    model_config = ConfigDict(from_attributes=True)

    action_id: str = Field(default_factory=lambda: f"vis-{uuid.uuid4().hex[:8]}")
    screenshot_width: int = 1920
    screenshot_height: int = 1080
    ocr_text: str = ""
    elements: List[DetectedUIElement] = Field(default_factory=list)
    segments: List[ScreenSegment] = Field(default_factory=list)
    reasoning: Optional[VisionReasoningResult] = None
    executed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

