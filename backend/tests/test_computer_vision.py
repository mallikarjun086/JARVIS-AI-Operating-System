"""
Pytest Test Suite for Computer Vision Subsystem.
Tests screenshot understanding, OCR, object detection, button recognition, bounding boxes, screen segmentation, vision reasoning, and vision memory.
"""

from httpx import AsyncClient
import pytest
from app.vision.detector import ui_detector
from app.vision.manager import vision_manager
from app.vision.memory import vision_memory_engine
from app.vision.reasoning import vision_reasoner
from app.vision.schemas import UIElementType, VisionAnalysisRequest
from app.vision.segmentation import screen_segmenter


@pytest.mark.asyncio
async def test_ui_element_detection_and_button_recognition():
    """Tests UI element detection, button classifier, and bounding box coordinates."""
    elements = ui_detector.detect_elements()
    assert len(elements) >= 3

    # Verify bounding box geometry
    btn = next(e for e in elements if e.element_type == UIElementType.BUTTON)
    assert btn.bounding_box.width > 0
    assert btn.bounding_box.x_max > btn.bounding_box.x_min

    # Button Recognizer
    buttons = ui_detector.recognize_buttons()
    assert len(buttons) >= 1
    assert buttons[0].is_clickable is True


@pytest.mark.asyncio
async def test_screen_segmentation():
    """Tests screen layout segmentation into functional regions."""
    segments = screen_segmenter.segment_screen()
    assert len(segments) >= 3
    region_types = [s.region_type for s in segments]
    assert "HEADER" in region_types
    assert "MAIN_CANVAS" in region_types


@pytest.mark.asyncio
async def test_multi_modal_vision_reasoning_and_memory():
    """Tests visual scene reasoning and vision memory cache."""
    reasoning = await vision_reasoner.reason_scene(task_goal="Click submit button")
    assert "scene_description" in reasoning.model_dump()
    assert len(reasoning.recommended_actions) >= 1

    # Record Vision Memory
    rec = vision_memory_engine.record_scene(
        image_b64=None,
        scene_summary="Test Vision Memory Scene",
        ocr_text="JARVIS OCR Text",
        element_count=4
    )
    assert rec.image_hash is not None

    recs = vision_memory_engine.list_records()
    assert any(r.record_id == rec.record_id for r in recs)


@pytest.mark.asyncio
async def test_vision_pipeline_manager():
    """Tests comprehensive vision manager pipeline execution."""
    req = VisionAnalysisRequest(task_goal="Find Submit Button")
    resp = await vision_manager.analyze_screenshot(req)

    assert resp.screenshot_width == 1920
    assert len(resp.elements) >= 3
    assert len(resp.segments) >= 3
    assert resp.reasoning is not None


@pytest.mark.asyncio
async def test_vision_api_endpoints(client: AsyncClient):
    """Tests FastAPI REST endpoints for Computer Vision."""
    # Register & login
    await client.post("/api/v1/auth/register", json={"email": "vision@jarvis.ai", "password": "Password123!", "full_name": "Vision User"})
    login_resp = await client.post("/api/v1/auth/login", data={"username": "vision@jarvis.ai", "password": "Password123!"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Analyze Screenshot Endpoint
    an_resp = await client.post("/api/v1/vision/analyze", json={"task_goal": "Inspect UI"}, headers=headers)
    assert an_resp.status_code == 200
    assert "elements" in an_resp.json()

    # Detect Elements Endpoint
    det_resp = await client.post("/api/v1/vision/detect-elements", headers=headers)
    assert det_resp.status_code == 200
    assert len(det_resp.json()) >= 1

    # Segment Layout Endpoint
    seg_resp = await client.post("/api/v1/vision/segment", headers=headers)
    assert seg_resp.status_code == 200
    assert len(seg_resp.json()) >= 1

    # Reason Endpoint
    reas_resp = await client.post("/api/v1/vision/reason?goal=Test", headers=headers)
    assert reas_resp.status_code == 200
    assert "scene_description" in reas_resp.json()

    # Vision Memory Endpoint
    mem_resp = await client.get("/api/v1/vision/memory", headers=headers)
    assert mem_resp.status_code == 200
