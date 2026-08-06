"""
Safety Emergency Stop, Permission Confirmation Guard, and Reversibility Undo Engine.
"""

from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from app.automation.schemas import EmergencyStopStatus


class SafetyEngine:
    """Manages emergency stop switch, confirmation guard, and reversibility undo log."""

    def __init__(self) -> None:
        self._emergency_stopped: bool = False
        self._emergency_stopped_at: Optional[datetime] = None
        self._emergency_reason: Optional[str] = None
        self._reversibility_log: Dict[str, Dict[str, Any]] = {}

    def is_emergency_stopped(self) -> bool:
        """Checks if emergency stop switch is active."""
        return self._emergency_stopped

    def get_emergency_status(self) -> EmergencyStopStatus:
        """Returns current emergency stop status."""
        return EmergencyStopStatus(
            is_emergency_stopped=self._emergency_stopped,
            triggered_at=self._emergency_stopped_at,
            reason=self._emergency_reason
        )

    def trigger_emergency_stop(self, reason: str = "User panic button triggered.") -> None:
        """Activates emergency stop kill switch immediately."""
        self._emergency_stopped = True
        self._emergency_stopped_at = datetime.utcnow()
        self._emergency_reason = reason

    def resume_operation(self) -> None:
        """Resumes automation operation after emergency stop."""
        self._emergency_stopped = False
        self._emergency_stopped_at = None
        self._emergency_reason = None

    def register_reversible_action(
        self,
        action_id: str,
        action_type: str,
        pre_state: Dict[str, Any],
        undo_handler: Callable[..., Any]
    ) -> None:
        """Registers pre-action snapshot state and undo handler function."""
        self._reversibility_log[action_id] = {
            "action_type": action_type,
            "pre_state": pre_state,
            "undo_handler": undo_handler,
            "timestamp": datetime.utcnow()
        }

    async def execute_undo(self, action_id: str) -> bool:
        """Executes rollback for a registered action ID."""
        if self._emergency_stopped:
            raise RuntimeError("Cannot execute undo while system is emergency stopped.")

        entry = self._reversibility_log.get(action_id)
        if not entry:
            return False

        undo_handler = entry["undo_handler"]
        pre_state = entry["pre_state"]

        if callable(undo_handler):
            res = undo_handler(pre_state)
            if hasattr(res, "__await__"):
                await res
            del self._reversibility_log[action_id]
            return True

        return False


safety_engine = SafetyEngine()
