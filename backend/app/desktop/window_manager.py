"""
Window Manager Engine — Handles window discovery, handle management (HWND), state machine transitions, focus, and bounds.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.desktop.platform.windows import windows_adapter
from app.desktop.schemas import WindowInfo, WindowState
from app.desktop.state_machine import window_state_machine

logger = structlog.get_logger(__name__)


class WindowManager:
    """Manages OS window handles, discovery, state transitions, and focus."""

    def list_windows(self) -> List[WindowInfo]:
        """Lists active visible windows."""
        return windows_adapter.list_windows()

    def find_window(self, title_or_hwnd: Any) -> Optional[WindowInfo]:
        """Finds window by HWND or title substring."""
        return windows_adapter.find_window(title_or_hwnd)

    def focus_window(self, title_or_hwnd: Any) -> Optional[WindowInfo]:
        """Brings window to foreground focus and transitions state to ACTIVE."""
        win = self.find_window(title_or_hwnd)
        if win:
            windows_adapter.focus_window(win.hwnd)
            win.is_active = True
            try:
                win.state = window_state_machine.transition(win.state, WindowState.ACTIVE)
            except ValueError:
                pass
            logger.info("Focused desktop window", title=win.title, hwnd=win.hwnd)
        return win

    def set_window_state(self, hwnd: int, state: WindowState) -> bool:
        """Transitions window state and applies OS window state change."""
        success = windows_adapter.set_window_state(hwnd, state.value)
        win = self.find_window(hwnd)
        if win and success:
            try:
                win.state = window_state_machine.transition(win.state, state)
            except ValueError:
                pass
        return success


window_manager = WindowManager()
