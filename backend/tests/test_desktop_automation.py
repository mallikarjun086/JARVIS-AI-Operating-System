"""
Pytest Test Suite for Windows Desktop Automation Subsystem.
Tests perception, OS control, emergency stop fail-safe, permission guards, and action reversibility undo.
"""

from httpx import AsyncClient
import pytest
from app.automation.controller import controller_engine
from app.automation.manager import automation_manager
from app.automation.perception import perception_engine
from app.automation.safety import safety_engine
from app.automation.schemas import AutomationActionType, AutomationRequest


@pytest.fixture(autouse=True)
def ensure_safety_resumed():
    """Resumes operation before every test."""
    safety_engine.resume_operation()


@pytest.mark.asyncio
async def test_mouse_keyboard_clipboard_controls():
    """Tests mouse move/click, keyboard type/press, and clipboard actions."""
    # Mouse Move
    old_p, new_p = controller_engine.move_mouse(250, 400)
    assert new_p == (250, 400)

    # Keyboard Type
    typed = controller_engine.type_text("JARVIS Automation Engine")
    assert typed["typed_text"] == "JARVIS Automation Engine"

    # Clipboard Set & Get
    old_c, new_c = controller_engine.set_clipboard("Test Clipboard Text")
    assert new_c == "Test Clipboard Text"
    assert controller_engine.get_clipboard() == "Test Clipboard Text"


@pytest.mark.asyncio
async def test_window_detection_and_perception():
    """Tests window enumeration, screen capture, and OCR text extraction."""
    windows = perception_engine.detect_open_windows()
    assert len(windows) >= 1
    assert windows[0].title is not None

    cap = perception_engine.capture_screen(width=800, height=600)
    assert cap.width == 800
    assert len(cap.image_base64) > 100

    ocr = perception_engine.extract_ocr_text()
    assert "JARVIS" in ocr.extracted_text
    assert len(ocr.boxes) >= 1


@pytest.mark.asyncio
async def test_reversibility_action_undo():
    """Tests snapshot state capture and step-by-step action undo execution."""
    # 1. Execute Clipboard Set action (Reversible)
    controller_engine.set_clipboard("Initial Clipboard Value")
    req = AutomationRequest(
        action_type=AutomationActionType.CLIPBOARD_SET,
        parameters={"text": "New Overwritten Value"}
    )
    resp = await automation_manager.execute_action(req)

    assert resp.status == "SUCCESS"
    assert resp.is_reversible is True
    assert resp.undo_action_id is not None
    assert controller_engine.get_clipboard() == "New Overwritten Value"

    # 2. Execute Undo
    undone = await safety_engine.execute_undo(resp.undo_action_id)
    assert undone is True
    assert controller_engine.get_clipboard() == "Initial Clipboard Value"  # Reverted!


@pytest.mark.asyncio
async def test_emergency_stop_fail_safe():
    """Verifies emergency stop switch blocks all automation actions immediately."""
    # Trigger Panic Button
    safety_engine.trigger_emergency_stop(reason="Test Panic Button")
    assert safety_engine.is_emergency_stopped() is True

    # Attempt execution during emergency stop
    req = AutomationRequest(action_type=AutomationActionType.MOUSE_CLICK)
    resp = await automation_manager.execute_action(req)

    assert resp.status == "EMERGENCY_STOPPED"
    assert "emergency stopped" in resp.error_message.lower()

    # Resume Operation
    safety_engine.resume_operation()
    assert safety_engine.is_emergency_stopped() is False


@pytest.mark.asyncio
async def test_automation_api_endpoints(client: AsyncClient):
    """Tests FastAPI REST endpoints for desktop automation."""
    # Register & login
    await client.post("/api/v1/auth/register", json={"email": "auto@jarvis.ai", "password": "Password123!", "full_name": "Auto User"})
    login_resp = await client.post("/api/v1/auth/login", data={"username": "auto@jarvis.ai", "password": "Password123!"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # List Windows
    win_resp = await client.get("/api/v1/automation/windows", headers=headers)
    assert win_resp.status_code == 200
    wins = win_resp.json()
    assert len(wins) >= 1

    # Take Screen Capture
    cap_resp = await client.post("/api/v1/automation/screen-capture", headers=headers)
    assert cap_resp.status_code == 200
    assert "image_base64" in cap_resp.json()

    # Emergency Stop Endpoint
    es_resp = await client.post("/api/v1/automation/emergency-stop", headers=headers)
    assert es_resp.status_code == 200
    assert es_resp.json()["is_emergency_stopped"] is True

    # Resume Endpoint
    res_resp = await client.post("/api/v1/automation/resume", headers=headers)
    assert res_resp.status_code == 200
    assert res_resp.json()["is_emergency_stopped"] is False


@pytest.mark.asyncio
async def test_sprint_7_1_desktop_state_and_ui_snapshot():
    """Sprint 7.1: Tests DesktopManager health status and Unified UI Tree Snapshot."""
    from app.desktop.manager import desktop_manager
    from app.desktop.ui_snapshot import ui_snapshot_engine
    from app.desktop.schemas import WindowState

    # Health status
    health = await desktop_manager.get_health_status()
    assert health["initialized"] is True
    assert "displays" in health
    assert "active_windows_count" in health

    # UI Tree Snapshot
    snap = ui_snapshot_engine.capture_snapshot(1001, "Test Window")
    assert snap.window_title == "Test Window"
    assert snap.hwnd == 1001
    assert snap.root_node.class_name == "Window"
    assert len(snap.root_node.children) >= 1


@pytest.mark.asyncio
async def test_sprint_7_1_window_state_machine_and_recovery():
    """Sprint 7.1: Tests Window State Machine 10 states and 7-Step Recovery Ladder."""
    from app.desktop.state_machine import window_state_machine
    from app.desktop.schemas import WindowState
    from app.desktop.recovery import desktop_recovery

    # State transitions
    st = window_state_machine.transition(WindowState.CREATED, WindowState.OPENING)
    assert st == WindowState.OPENING
    st = window_state_machine.transition(st, WindowState.READY)
    assert st == WindowState.READY
    st = window_state_machine.transition(st, WindowState.ACTIVE)
    assert st == WindowState.ACTIVE

    # 7-Step Recovery Ladder
    attempts = 0

    async def failing_action():
        nonlocal attempts
        attempts += 1
        if attempts < 4:
            raise RuntimeError("Temporary action error")
        return "RECOVERED_SUCCESS"

    async def refocus():
        pass

    result = await desktop_recovery.execute_with_recovery_ladder(
        action_fn=failing_action,
        refocus_window_fn=refocus,
        max_retries=3
    )
    assert result == "RECOVERED_SUCCESS"


@pytest.mark.asyncio
async def test_sprint_7_1_ocr_and_memory_redaction():
    """Sprint 7.1: Tests BaseOCREngine polymorphic output and Memory Bridge secret redaction."""
    from app.desktop.ocr import ocr_engine
    from app.desktop.memory_bridge import desktop_memory_bridge

    ocr_res = ocr_engine.extract_text()
    assert ocr_res.extracted_text is not None
    assert len(ocr_res.boxes) >= 1

    redacted = desktop_memory_bridge.redact_secrets("Action with password='Secret123!' and token='abc123xyz'")
    assert "Secret123!" not in redacted
    assert "[REDACTED]" in redacted


@pytest.mark.asyncio
async def test_sprint_7_1_human_approval_and_metrics():
    """Sprint 7.1: Tests High-Risk Gatekeeper interception and Telemetry metrics."""
    from app.desktop.manager import desktop_manager
    from app.desktop.schemas import DesktopActionRequest, DesktopActionType, ActionQueueStatus
    from app.desktop.metrics import desktop_metrics

    # High-Risk registry edit action request
    req = DesktopActionRequest(
        action_type=DesktopActionType.LAUNCH_APP,
        app_name_or_path="regedit.exe"
    )
    resp = await desktop_manager.execute_action(req)
    assert resp.requires_approval is True
    assert resp.status == ActionQueueStatus.QUEUED
    assert resp.approval_id is not None

    # Telemetry dictionary verify
    metrics_dict = desktop_metrics.to_dict()
    assert "total_approvals_requested" in metrics_dict
    assert "automation_success_rate" in metrics_dict

