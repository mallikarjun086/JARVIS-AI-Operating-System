"""
Desktop Automation Manager Engine.
Orchestrates OS perception, control actions, emergency stop fail-safe, and reversibility undo logging.
"""

from typing import Any, Dict
from app.automation.controller import controller_engine
from app.automation.perception import perception_engine
from app.automation.safety import safety_engine
from app.automation.schemas import AutomationActionType, AutomationRequest, AutomationResponse


class DesktopAutomationManager:
    """Central manager for executing desktop automation actions with safety checks."""

    @classmethod
    async def execute_action(cls, req: AutomationRequest) -> AutomationResponse:
        """
        Executes desktop automation action enforcing safety emergency stop switch,
        confirmation guards, and registering pre-action state for reversibility undo.
        """
        # 1. Emergency Stop Check
        if safety_engine.is_emergency_stopped():
            return AutomationResponse(
                action_type=req.action_type,
                status="EMERGENCY_STOPPED",
                error_message="System is emergency stopped. Action aborted."
            )

        # 2. Confirmation Guard Check for Destructive Actions
        if req.action_type == AutomationActionType.WINDOW_CLOSE and req.require_confirmation:
            return AutomationResponse(
                action_type=req.action_type,
                status="CANCELLED",
                error_message="Action required explicit user confirmation before closing active window."
            )

        resp = AutomationResponse(action_type=req.action_type, status="SUCCESS")

        # 3. Action Execution & Reversibility Registration
        params = req.parameters

        if req.action_type == AutomationActionType.MOUSE_MOVE:
            x, y = params.get("x", 0), params.get("y", 0)
            old_pos, new_pos = controller_engine.move_mouse(x, y)
            resp.result = {"position": new_pos}

            # Register reversible undo step (move cursor back to old_pos)
            resp.is_reversible = True
            resp.undo_action_id = resp.action_id
            safety_engine.register_reversible_action(
                resp.action_id,
                "MOUSE_MOVE",
                {"x": old_pos[0], "y": old_pos[1]},
                lambda pre: controller_engine.move_mouse(pre["x"], pre["y"])
            )

        elif req.action_type == AutomationActionType.MOUSE_CLICK:
            resp.result = controller_engine.click_mouse(
                button=params.get("button", "left"),
                double=params.get("double", False)
            )

        elif req.action_type == AutomationActionType.KEY_TYPE:
            resp.result = controller_engine.type_text(params.get("text", ""))

        elif req.action_type == AutomationActionType.KEY_PRESS:
            resp.result = controller_engine.press_key(params.get("key", "Enter"))

        elif req.action_type == AutomationActionType.CLIPBOARD_SET:
            old_text, new_text = controller_engine.set_clipboard(params.get("text", ""))
            resp.result = {"clipboard": new_text}

            # Register reversible undo step (restore old clipboard text)
            resp.is_reversible = True
            resp.undo_action_id = resp.action_id
            safety_engine.register_reversible_action(
                resp.action_id,
                "CLIPBOARD_SET",
                {"text": old_text},
                lambda pre: controller_engine.set_clipboard(pre["text"])
            )

        elif req.action_type == AutomationActionType.CLIPBOARD_GET:
            resp.result = {"text": controller_engine.get_clipboard()}

        elif req.action_type == AutomationActionType.WINDOW_FOCUS:
            hwnd = params.get("hwnd", 1001)
            focused = controller_engine.focus_window(hwnd)
            resp.result = focused.model_dump() if focused else {}

        elif req.action_type == AutomationActionType.WINDOW_MINIMIZE:
            hwnd = params.get("hwnd", 1001)
            resp.result = controller_engine.set_window_state(hwnd, "MINIMIZE")
            resp.is_reversible = True
            resp.undo_action_id = resp.action_id
            safety_engine.register_reversible_action(
                resp.action_id,
                "WINDOW_MINIMIZE",
                {"hwnd": hwnd},
                lambda pre: controller_engine.set_window_state(pre["hwnd"], "RESTORE")
            )

        elif req.action_type == AutomationActionType.WINDOW_MAXIMIZE:
            hwnd = params.get("hwnd", 1001)
            resp.result = controller_engine.set_window_state(hwnd, "MAXIMIZE")

        elif req.action_type == AutomationActionType.WINDOW_CLOSE:
            hwnd = params.get("hwnd", 1001)
            resp.result = controller_engine.set_window_state(hwnd, "CLOSE")

        elif req.action_type == AutomationActionType.SCREEN_CAPTURE:
            cap = perception_engine.capture_screen()
            resp.result = cap.model_dump()

        elif req.action_type == AutomationActionType.WINDOW_DETECT:
            wins = perception_engine.detect_open_windows()
            resp.result = [w.model_dump() for w in wins]

        elif req.action_type == AutomationActionType.OCR_TEXT_EXTRACT:
            ocr = perception_engine.extract_ocr_text()
            resp.result = ocr.model_dump()

        return resp


automation_manager = DesktopAutomationManager()
