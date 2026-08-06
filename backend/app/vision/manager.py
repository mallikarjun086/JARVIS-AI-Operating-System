"""
Computer Vision Manager Engine.
Orchestrates UI element detection, OCR, screen segmentation, vision reasoning, and vision memory sync.
"""

from app.automation.perception import perception_engine
from app.vision.detector import ui_detector
from app.vision.memory import vision_memory_engine
from app.vision.reasoning import vision_reasoner
from app.vision.schemas import VisionAnalysisRequest, VisionAnalysisResponse
from app.vision.segmentation import screen_segmenter


class ComputerVisionManager:
    """Central orchestrator for computer vision perception pipelines."""

    @classmethod
    async def analyze_screenshot(cls, req: VisionAnalysisRequest) -> VisionAnalysisResponse:
        """
        Executes comprehensive vision pipeline:
        1. Captures/loads screenshot buffer.
        2. Performs OCR text extraction.
        3. Detects UI elements, buttons, and bounding boxes.
        4. Segments screen layout into functional regions.
        5. Executes multi-modal visual reasoning.
        6. Registers snapshot in Vision Memory.
        """
        image_b64 = req.image_base64
        if not image_b64:
            cap = perception_engine.capture_screen()
            image_b64 = cap.image_base64

        # OCR Text
        ocr_res = perception_engine.extract_ocr_text(image_b64)

        # UI Element & Button Detection
        elements = ui_detector.detect_elements(image_b64)

        # Screen Layout Segmentation
        segments = screen_segmenter.segment_screen(image_b64)

        # Vision Reasoning
        reasoning = await vision_reasoner.reason_scene(image_b64, req.task_goal)

        # Vision Memory Snapshot
        vision_memory_engine.record_scene(
            image_b64=image_b64,
            scene_summary=reasoning.scene_description,
            ocr_text=ocr_res.extracted_text,
            element_count=len(elements)
        )

        return VisionAnalysisResponse(
            screenshot_width=1920,
            screenshot_height=1080,
            ocr_text=ocr_res.extracted_text,
            elements=elements,
            segments=segments,
            reasoning=reasoning
        )


vision_manager = ComputerVisionManager()
