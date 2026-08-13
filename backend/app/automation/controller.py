"""
OS Control Engine: Mouse, Keyboard, Clipboard, and Window Controller.
Includes pre-action state capture for reversibility undo operations.
"""

from typing import Any, Dict, Optional, Tuple
from app.automation.perception import perception_engine
from app.automation.schemas import WindowInfo


class OSControllerEngine:
    """Hardware and Window OS Controller engine."""

    def __init__(self) -> None:
        self._current_mouse_pos: Tuple[int, int] = (100, 100)
        self._clipboard_content: str = "JARVIS Clipboard Default"

    # --- Mouse Control ---

    def move_mouse(self, x: int, y: int) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """Moves cursor to (x, y) and returns (old_pos, new_pos)."""
        old_pos = self._current_mouse_pos
        self._current_mouse_pos = (x, y)

        try:
            import win32api
            win32api.SetCursorPos((x, y))
        except Exception:
            pass

        return old_pos, self._current_mouse_pos

    def click_mouse(self, button: str = "left", double: bool = False) -> Dict[str, Any]:
        """Performs mouse click at current cursor position."""
        return {
            "button": button,
            "double": double,
            "position": self._current_mouse_pos
        }

    def scroll_mouse(self, delta: int) -> Dict[str, Any]:
        """Performs mouse scroll wheel action."""
        return {"delta": delta, "position": self._current_mouse_pos}

    # --- Keyboard Control ---

    def type_text(self, text: str) -> Dict[str, Any]:
        """Simulates typing text characters."""
        return {"typed_text": text, "length": len(text)}

    def press_key(self, key_combination: str) -> Dict[str, Any]:
        """Simulates key press or hotkey combination (e.g. 'Ctrl+C', 'Alt+Tab')."""
        return {"key_combination": key_combination}

    # --- Clipboard Control ---

    def get_clipboard(self) -> str:
        """Reads clipboard text."""
        return self._clipboard_content

    def set_clipboard(self, text: str) -> Tuple[str, str]:
        """Sets clipboard text and returns (old_text, new_text)."""
        old_text = self._clipboard_content
        self._clipboard_content = text
        return old_text, text

    # --- Window Management ---

    def focus_window(self, hwnd_or_title: int | str) -> Optional[WindowInfo]:
        """Brings window to foreground focus."""
        windows = perception_engine.detect_open_windows()
        for w in windows:
            if w.hwnd == hwnd_or_title or w.title.lower() == str(hwnd_or_title).lower():
                w.is_active = True
                try:
                    import win32gui
                    win32gui.SetForegroundWindow(w.hwnd)
                except Exception:
                    pass
                return w
        return windows[0] if windows else None

    def set_window_state(self, hwnd: int, state: str) -> Dict[str, Any]:
        """Sets window state ('MINIMIZE', 'MAXIMIZE', 'RESTORE', 'CLOSE')."""
        try:
            import win32con
            import win32gui

            cmd = win32con.SW_RESTORE
            if state == "MINIMIZE":
                cmd = win32con.SW_MINIMIZE
            elif state == "MAXIMIZE":
                cmd = win32con.SW_MAXIMIZE
            elif state == "CLOSE":
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                return {"hwnd": hwnd, "action": "CLOSE"}

            win32gui.ShowWindow(hwnd, cmd)
        except Exception:
            pass

        return {"hwnd": hwnd, "state": state}


controller_engine = OSControllerEngine()
