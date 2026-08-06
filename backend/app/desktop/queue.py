"""
Desktop Action Queue — Manages queueing, status tracking, and verification of desktop actions.
"""

from typing import Dict, List, Optional
import structlog
from app.desktop.schemas import ActionQueueStatus, DesktopActionRequest, DesktopActionResponse

logger = structlog.get_logger(__name__)


class DesktopActionQueue:
    """Traceable action queue for desktop execution requests."""

    def __init__(self) -> None:
        self._history: Dict[str, DesktopActionResponse] = {}

    def push_action(self, req: DesktopActionRequest) -> DesktopActionResponse:
        """Pushes an action request into the queue with QUEUED state."""
        res = DesktopActionResponse(
            action_type=req.action_type,
            status=ActionQueueStatus.QUEUED
        )
        self._history[res.action_id] = res
        logger.info("Queued desktop action", action_id=res.action_id, action_type=req.action_type.value)
        return res

    def update_status(
        self,
        action_id: str,
        status: ActionQueueStatus,
        result: Optional[dict] = None,
        error_message: Optional[str] = None
    ) -> Optional[DesktopActionResponse]:
        """Updates action status in queue."""
        res = self._history.get(action_id)
        if res:
            res.status = status
            if result is not None:
                res.result = result
            if error_message:
                res.error_message = error_message
            logger.info("Updated desktop action status", action_id=action_id, status=status.value)
        return res

    def get_action(self, action_id: str) -> Optional[DesktopActionResponse]:
        """Fetches action entry by ID."""
        return self._history.get(action_id)

    def list_history(self) -> List[DesktopActionResponse]:
        """Returns history of all queued actions."""
        return list(self._history.values())


desktop_action_queue = DesktopActionQueue()
