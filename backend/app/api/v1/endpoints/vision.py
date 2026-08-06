"""
FastAPI Endpoints for Computer Vision Subsystem.
"""

from typing import List
from fastapi import APIRouter, Depends, Query, status
from app.api.deps import get_current_user
from app.models.user import User
from app.vision.detector import ui_detector
from app.vision.manager import vision_manager
from app.vision.memory import vision_memory_engine
from app.vision.reasoning import vision_reasoner
from app.vision.schemas import (
    DetectedUIElement,
    ScreenSegment,
    VisionAnalysisRequest,
    VisionAnalysisResponse,
    VisionMemoryRecord,
    VisionReasoningResult,
)
from app.vision.segmentation import screen_segmenter

router = APIRouter()


@router.post("/analyze", response_model=VisionAnalysisResponse, summary="Execute Comprehensive Computer Vision Analysis")
async def analyze_vision_screenshot(
    req: VisionAnalysisRequest,
    current_user: User = Depends(get_current_user)
) -> VisionAnalysisResponse:
    """Performs screenshot understanding, OCR text extraction, UI element detection, bounding boxes, screen segmentation, and reasoning."""
    return await vision_manager.analyze_screenshot(req)


@router.post("/detect-elements", response_model=List[DetectedUIElement], summary="Detect UI Elements & Buttons")
async def detect_ui_elements(
    current_user: User = Depends(get_current_user)
) -> List[DetectedUIElement]:
    """Scans screenshot buffer and returns detected UI elements and button bounding boxes."""
    return ui_detector.detect_elements()


@router.post("/segment", response_model=List[ScreenSegment], summary="Perform Screen Layout Segmentation")
async def segment_screen_layout(
    current_user: User = Depends(get_current_user)
) -> List[ScreenSegment]:
    """Divides desktop layout into functional regions (Header, Sidebar, Main Canvas, Footer)."""
    return screen_segmenter.segment_screen()


@router.post("/reason", response_model=VisionReasoningResult, summary="Perform Visual Scene Reasoning")
async def reason_visual_scene(
    goal: str = Query("Analyze UI layout", description="Target action goal prompt"),
    current_user: User = Depends(get_current_user)
) -> VisionReasoningResult:
    """Performs multi-modal visual scene reasoning and returns recommended click/action coordinates."""
    return await vision_reasoner.reason_scene(task_goal=goal)


@router.get("/memory", response_model=List[VisionMemoryRecord], summary="Get Vision Memory Records")
async def list_vision_memory_records(
    current_user: User = Depends(get_current_user)
) -> List[VisionMemoryRecord]:
    """Retrieves cached vision scene snapshots and hash records."""
    return vision_memory_engine.list_records()
