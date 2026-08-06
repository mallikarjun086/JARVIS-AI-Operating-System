"""
Desktop Session Manager — Manages active desktop automation sessions and context restoration.
"""

from datetime import datetime
from typing import Dict, Optional
import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)


class DesktopSession(BaseModel):
    """Desktop automation session descriptor."""
    session_id: str
    active_hwnd: Optional[int] = None
    active_app: Optional[str] = None
    user_id: Optional[str] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class DesktopSessionManager:
    """Manages active desktop sessions for user automation tasks."""

    def __init__(self) -> None:
        self._current_session: DesktopSession = DesktopSession(session_id="default_desktop_session")

    def get_current_session(self) -> DesktopSession:
        """Returns active desktop automation session."""
        return self._current_session

    def update_session(self, hwnd: Optional[int] = None, app_name: Optional[str] = None) -> DesktopSession:
        """Updates active session focus."""
        if hwnd is not None:
            self._current_session.active_hwnd = hwnd
        if app_name is not None:
            self._current_session.active_app = app_name
        return self._current_session


desktop_session_manager = DesktopSessionManager()
