"""
Central Desktop Automation Manager Orchestrator.
Orchestrates DisplayManager, WindowManager, ApplicationManager, DesktopSessionManager, Safety Gatekeeper, and Action Queue.
"""

import time
from typing import Any, Dict, Optional
import structlog

from app.desktop.app_manager import app_manager
from app.desktop.clipboard import clipboard_manager
from app.desktop.display_manager import display_manager
from app.desktop.input import input_engine
from app.desktop.metrics import desktop_metrics
from app.desktop.ocr import ocr_engine
from app.desktop.perception import perception_engine
from app.desktop.queue import desktop_action_queue
from app.desktop.recorder import workflow_recorder
from app.desktop.recovery import desktop_recovery
from app.desktop.safety import desktop_safety_gatekeeper
from app.desktop.schemas import (
    ActionQueueStatus,
    DesktopActionRequest,
    DesktopActionResponse,
    DesktopActionType,
    HighRiskDesktopActionType,
)
from app.desktop.session_manager import desktop_session_manager
from app.desktop.ui_snapshot import ui_snapshot_engine
from app.desktop.window_manager import window_manager

logger = structlog.get_logger(__name__)


class DesktopManager:
    """Central Orchestrator for Enterprise Desktop Automation Engine."""

    def __init__(self) -> None:
        self._is_initialized: bool = False

    async def initialize(self) -> None:
        """Initializes DisplayManager High-DPI scaling and desktop session."""
        display_manager.initialize_dpi_awareness()
        self._is_initialized = True
        logger.info("DesktopManager initialized successfully")

    async def shutdown(self) -> None:
        """Gracefully shuts down DesktopManager."""
        self._is_initialized = False
        logger.info("DesktopManager shutdown completed")

    async def get_health_status(self) -> Dict[str, Any]:
        """Returns desktop health diagnostics."""
        return {
            "initialized": True,

            "displays": [d.model_dump() for d in display_manager.get_displays()],
            "active_windows_count": len(window_manager.list_windows()),
            "running_processes_count": len(app_manager.list_processes()),
            "session_id": desktop_session_manager.get_current_session().session_id
        }

    async def execute_action(self, req: DesktopActionRequest) -> DesktopActionResponse:
        """
        Executes desktop action with Action Queue tracking, Safety Gatekeeper interception, and Telemetry.
        """
        if not self._is_initialized:
            await self.initialize()

        # 1. High-Risk Safety Gatekeeper Interception
        risk_type = req.high_risk_type or desktop_safety_gatekeeper.evaluate_action_risk(
            action_type=req.action_type.value,
            app_name_or_path=req.app_name_or_path,
            parameters=req.parameters
        )
        if risk_type is not None:
            desktop_metrics.total_approvals_requested += 1
            ticket = desktop_safety_gatekeeper.create_approval_request(
                high_risk_type=risk_type,
                target_details={"action_type": req.action_type.value, "app": req.app_name_or_path, "parameters": req.parameters}
            )
            return DesktopActionResponse(
                action_type=req.action_type,
                status=ActionQueueStatus.QUEUED,
                requires_approval=True,
                approval_id=ticket.approval_id,
                error_message=f"High-risk action '{risk_type.value}' requires human approval before proceeding."
            )

        # 2. Action Queue Tracking
        q_item = desktop_action_queue.push_action(req)
        desktop_action_queue.update_status(q_item.action_id, ActionQueueStatus.RUNNING)

        resp = DesktopActionResponse(
            action_id=q_item.action_id,
            action_type=req.action_type,
            status=ActionQueueStatus.COMPLETED
        )
        start_time = time.time()

        try:
            # Record step if workflow recording is active
            workflow_recorder.record_step(
                app_name=req.app_name_or_path or "desktop",
                window_title=str(req.window_title_or_hwnd or ""),
                action_type=req.action_type.value,
                parameters=req.parameters
            )

            # 3. Action Dispatcher
            if req.action_type == DesktopActionType.LAUNCH_APP:
                app_info = app_manager.launch_app(req.app_name_or_path or "notepad")
                resp.result = app_info.model_dump()
                desktop_metrics.total_app_launches += 1

            elif req.action_type == DesktopActionType.CLOSE_APP:
                closed = app_manager.close_app(req.app_name_or_path or 0)
                resp.result = {"closed": closed}

            elif req.action_type == DesktopActionType.FIND_WINDOW or req.action_type == DesktopActionType.LIST_WINDOWS:
                if req.window_title_or_hwnd:
                    win = window_manager.find_window(req.window_title_or_hwnd)
                    resp.result = win.model_dump() if win else None
                else:
                    wins = window_manager.list_windows()
                    resp.result = [w.model_dump() for w in wins]
                desktop_metrics.record_window_discovery((time.time() - start_time) * 1000.0)

            elif req.action_type == DesktopActionType.FOCUS_WINDOW or req.action_type == DesktopActionType.ACTIVATE_WINDOW:
                win = window_manager.focus_window(req.window_title_or_hwnd or 1001)
                resp.result = win.model_dump() if win else None
                desktop_metrics.record_window_discovery((time.time() - start_time) * 1000.0)

            elif req.action_type == DesktopActionType.CLICK:
                if req.x is not None and req.y is not None:
                    input_engine.move_mouse(req.x, req.y)
                resp.result = input_engine.click(button=req.button or "left")
                desktop_metrics.record_input_event("mouse", (time.time() - start_time) * 1000.0)

            elif req.action_type == DesktopActionType.DOUBLE_CLICK:
                if req.x is not None and req.y is not None:
                    input_engine.move_mouse(req.x, req.y)
                resp.result = input_engine.double_click()
                desktop_metrics.record_input_event("mouse", (time.time() - start_time) * 1000.0)

            elif req.action_type == DesktopActionType.RIGHT_CLICK:
                if req.x is not None and req.y is not None:
                    input_engine.move_mouse(req.x, req.y)
                resp.result = input_engine.right_click()
                desktop_metrics.record_input_event("mouse", (time.time() - start_time) * 1000.0)

            elif req.action_type == DesktopActionType.DRAG:
                sx, sy = req.parameters.get("start_x", 0), req.parameters.get("start_y", 0)
                ex, ey = req.parameters.get("end_x", 100), req.parameters.get("end_y", 100)
                resp.result = input_engine.drag_and_drop(sx, sy, ex, ey)
                desktop_metrics.record_input_event("mouse", (time.time() - start_time) * 1000.0)

            elif req.action_type == DesktopActionType.SCROLL:
                delta = req.parameters.get("delta", 100)
                resp.result = input_engine.scroll(delta)
                desktop_metrics.record_input_event("mouse", (time.time() - start_time) * 1000.0)

            elif req.action_type == DesktopActionType.TYPE:
                text = req.text_content or req.parameters.get("text", "")
                resp.result = input_engine.type_text(text)
                desktop_metrics.record_input_event("keyboard", (time.time() - start_time) * 1000.0)

            elif req.action_type == DesktopActionType.HOTKEY:
                hk = req.hotkey_combination or req.parameters.get("hotkey", "Enter")
                resp.result = input_engine.send_hotkey(hk)
                desktop_metrics.record_input_event("keyboard", (time.time() - start_time) * 1000.0)

            elif req.action_type == DesktopActionType.CLIPBOARD_COPY or req.action_type == DesktopActionType.CLIPBOARD_PASTE:
                text = req.text_content or req.parameters.get("text")
                if text:
                    clipboard_manager.set_text(text)
                resp.result = {"text": clipboard_manager.get_text()}
                desktop_metrics.total_clipboard_events += 1

            elif req.action_type == DesktopActionType.SCREENSHOT:
                b64 = perception_engine.capture_screen(
                    x=req.x or 0, y=req.y or 0,
                    width=req.width or 1920, height=req.height or 1080
                )
                resp.result = {"image_base64": b64}

            elif req.action_type == DesktopActionType.OCR:
                ocr_res = ocr_engine.extract_text()
                resp.result = ocr_res.model_dump()
                desktop_metrics.record_ocr_extraction((time.time() - start_time) * 1000.0)

            elif req.action_type == DesktopActionType.LIST_PROCESSES:
                procs = app_manager.list_processes()
                resp.result = [p.model_dump() for p in procs]

            desktop_action_queue.update_status(resp.action_id, ActionQueueStatus.COMPLETED, result=resp.result)

        except Exception as e:
            logger.error("Desktop action execution error", action_type=req.action_type.value, error=str(e))
            resp.status = ActionQueueStatus.FAILED
            resp.error_message = str(e)
            desktop_action_queue.update_status(resp.action_id, ActionQueueStatus.FAILED, error_message=str(e))
            desktop_metrics.total_failures += 1

        return resp


desktop_manager = DesktopManager()
