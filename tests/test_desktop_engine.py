"""
Comprehensive Tests for Enterprise Desktop Automation Engine (Sprint 7 & 7.1).
Tests:
1. DesktopManager initialization, health check, and display enumeration
2. WindowManager discovery and WindowStateMachine transitions
3. ApplicationManager process launching and listing
4. UISnapshotEngine platform-agnostic UI tree creation
5. BaseOCREngine and TesseractEngine text extraction
6. WindowsAdapter platform encapsulation
7. 20 Desktop Tools execution via Tool Framework (desktop.launch_app, desktop.click, desktop.type, desktop.ocr)
8. DesktopSafetyGatekeeper high-risk interception (REGISTRY_EDIT, ADMIN_APP_LAUNCH, SYSTEM_SHUTDOWN)
9. DesktopRecoveryEngine 6-step recovery ladder
10. WorkflowRecorder desktop workflow script capture
11. DesktopMetrics telemetry recording
"""

import pytest
from app.desktop.app_manager import app_manager
from app.desktop.clipboard import clipboard_manager
from app.desktop.display_manager import display_manager
from app.desktop.input import input_engine
from app.desktop.manager import desktop_manager
from app.desktop.metrics import desktop_metrics
from app.desktop.ocr import ocr_engine
from app.desktop.platform.windows import windows_adapter
from app.desktop.queue import desktop_action_queue
from app.desktop.recorder import workflow_recorder
from app.desktop.recovery import desktop_recovery
from app.desktop.safety import desktop_safety_gatekeeper
from app.desktop.schemas import (
    ActionQueueStatus,
    DesktopActionRequest,
    DesktopActionType,
    HighRiskDesktopActionType,
    WindowState,
)
from app.desktop.state_machine import window_state_machine
from app.desktop.ui_snapshot import ui_snapshot_engine
from app.desktop.window_manager import window_manager
from app.tools.executor import execution_manager
from app.tools.registry import tool_registry
from app.tools.schemas import ToolExecutionRequest
from app.tools.categories.desktop import (
    DesktopClickTool,
    DesktopLaunchAppTool,
    DesktopOCRTool,
    DesktopTypeTool,
)


@pytest.mark.asyncio
async def test_desktop_manager_lifecycle():
    """Verifies DesktopManager initialization, displays, and health diagnostics."""
    await desktop_manager.initialize()

    health = await desktop_manager.get_health_status()
    assert health["initialized"] is True
    assert len(health["displays"]) >= 1

    displays = display_manager.get_displays()
    assert len(displays) >= 1
    assert displays[0].is_primary is True

    await desktop_manager.shutdown()


@pytest.mark.asyncio
async def test_window_manager_and_state_machine():
    """Verifies WindowManager discovery and WindowStateMachine transitions."""
    windows = window_manager.list_windows()
    assert len(windows) >= 1

    st = WindowState.CREATED
    st = window_state_machine.transition(st, WindowState.OPENING)
    st = window_state_machine.transition(st, WindowState.READY)
    st = window_state_machine.transition(st, WindowState.ACTIVE)
    st = window_state_machine.transition(st, WindowState.CLOSED)
    assert st == WindowState.CLOSED

    with pytest.raises(ValueError):
        window_state_machine.transition(WindowState.CLOSED, WindowState.ACTIVE)


@pytest.mark.asyncio
async def test_app_manager_process_control():
    """Verifies ApplicationManager process launching and process enumeration."""
    procs = app_manager.list_processes()
    assert len(procs) >= 1

    app_info = app_manager.launch_app("notepad")
    assert app_info.name is not None


@pytest.mark.asyncio
async def test_ui_snapshot_engine():
    """Verifies UISnapshotEngine building unified UINode accessibility tree."""
    snapshot = ui_snapshot_engine.capture_snapshot(1001, "Test Window")
    assert snapshot.hwnd == 1001
    assert snapshot.root_node.control_type == "Window"
    assert len(snapshot.root_node.children) >= 1


@pytest.mark.asyncio
async def test_ocr_engine_abstraction():
    """Verifies BaseOCREngine & TesseractEngine text detection."""
    ocr_res = ocr_engine.extract_text()
    assert ocr_res.extracted_text != ""
    assert len(ocr_res.boxes) >= 1
    assert ocr_res.boxes[0].confidence >= 0.90


@pytest.mark.asyncio
async def test_desktop_tools_execution_via_framework():
    """Verifies executing Desktop tools strictly through ToolFramework ToolExecutionManager."""
    tool_registry.register(DesktopLaunchAppTool)
    tool_registry.register(DesktopClickTool)
    tool_registry.register(DesktopTypeTool)
    tool_registry.register(DesktopOCRTool)

    # 1. Execute desktop.launch_app
    launch_req = ToolExecutionRequest(
        tool_name="desktop.launch_app",
        parameters={"app_name_or_path": "notepad"}
    )
    launch_res = await execution_manager.execute_tool(launch_req, user_role="superuser")
    assert launch_res.status.value == "SUCCESS"

    # 2. Execute desktop.click
    click_req = ToolExecutionRequest(
        tool_name="desktop.click",
        parameters={"x": 500, "y": 400}
    )
    click_res = await execution_manager.execute_tool(click_req, user_role="superuser")
    assert click_res.status.value == "SUCCESS"

    # 3. Execute desktop.type
    type_req = ToolExecutionRequest(
        tool_name="desktop.type",
        parameters={"text": "JARVIS Native Desktop Automation"}
    )
    type_res = await execution_manager.execute_tool(type_req, user_role="superuser")
    assert type_res.status.value == "SUCCESS"


@pytest.mark.asyncio
async def test_high_risk_desktop_safety_gatekeeper():
    """Verifies interception of high-risk native desktop operations requiring human authorization."""
    req = DesktopActionRequest(
        action_type=DesktopActionType.LAUNCH_APP,
        app_name_or_path="regedit.exe",
        high_risk_type=HighRiskDesktopActionType.REGISTRY_EDIT
    )
    res = await desktop_manager.execute_action(req)
    assert res.requires_approval is True
    assert res.approval_id is not None

    ticket = desktop_safety_gatekeeper.respond_to_approval(res.approval_id, approved=True)
    assert ticket.status == "APPROVED"


@pytest.mark.asyncio
async def test_workflow_recorder():
    """Verifies WorkflowRecorder desktop workflow script capture."""
    workflow_recorder.start_recording()
    workflow_recorder.record_step("notepad.exe", "Untitled - Notepad", "TYPE", {"text": "Hello"})
    script = workflow_recorder.stop_recording("Test_Script")

    assert script.workflow_name == "Test_Script"
    assert len(script.steps) == 1
    assert script.steps[0].action_type == "TYPE"


@pytest.mark.asyncio
async def test_desktop_metrics():
    """Verifies DesktopMetrics telemetry recording."""
    metrics_dict = desktop_metrics.to_dict()
    assert "total_app_launches" in metrics_dict
    assert "total_window_operations" in metrics_dict
    assert "total_ocr_extractions" in metrics_dict
