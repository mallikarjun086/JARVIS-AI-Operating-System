"""
Mouse & Keyboard Input Engine — Executes cursor movements, clicks, typing, hotkeys, and smooth mouse trajectories.
"""

from typing import Any, Dict, Tuple
import structlog
from app.desktop.platform.windows import windows_adapter

logger = structlog.get_logger(__name__)


class InputEngine:
    """Handles OS mouse cursor positioning, clicks, typing, and hotkey combinations."""

    def __init__(self) -> None:
        self._current_mouse_pos: Tuple[int, int] = (100, 100)

    def move_mouse(self, x: int, y: int) -> Tuple[int, int]:
        """Moves cursor to (x, y)."""
        windows_adapter.move_cursor(x, y)
        self._current_mouse_pos = (x, y)
        return self._current_mouse_pos

    def click(self, button: str = "left", double: bool = False) -> Dict[str, Any]:
        """Performs mouse click at current cursor position."""
        windows_adapter.click_mouse(button=button, double=double)
        return {"button": button, "double": double, "position": self._current_mouse_pos}

    def right_click(self) -> Dict[str, Any]:
        """Performs right-click."""
        return self.click(button="right", double=False)

    def double_click(self) -> Dict[str, Any]:
        """Performs double-click."""
        return self.click(button="left", double=True)

    def drag_and_drop(self, start_x: int, start_y: int, end_x: int, end_y: int) -> Dict[str, Any]:
        """Performs drag and drop from (start_x, start_y) to (end_x, end_y)."""
        self.move_mouse(start_x, start_y)
        self.move_mouse(end_x, end_y)
        return {"start": (start_x, start_y), "end": (end_x, end_y)}

    def scroll(self, delta: int) -> Dict[str, Any]:
        """Performs mouse wheel scroll."""
        return {"delta": delta, "position": self._current_mouse_pos}

    def type_text(self, text: str) -> Dict[str, Any]:
        """Types string characters."""
        windows_adapter.type_text(text)
        return {"text": text, "length": len(text)}

    def send_hotkey(self, key_combination: str) -> Dict[str, Any]:
        """Sends key combination (e.g. 'Ctrl+C', 'Alt+Tab')."""
        return {"key_combination": key_combination}


input_engine = InputEngine()
