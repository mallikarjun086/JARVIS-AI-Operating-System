"""
Base Abstract Desktop Platform Adapter.
Encapsulates platform-specific OS calls behind a unified interface.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from app.desktop.schemas import WindowInfo


class DesktopPlatformAdapter(ABC):
    """Abstract Base Class for OS Platform Adapters (Windows, Linux, macOS)."""

    @abstractmethod
    def list_windows(self) -> List[WindowInfo]:
        """Lists active desktop windows."""
        pass

    @abstractmethod
    def find_window(self, title_or_hwnd: Any) -> Optional[WindowInfo]:
        """Finds window by title substring or HWND handle."""
        pass

    @abstractmethod
    def focus_window(self, hwnd: int) -> bool:
        """Brings window to foreground focus."""
        pass

    @abstractmethod
    def set_window_state(self, hwnd: int, state: str) -> bool:
        """Sets window state (MINIMIZE, MAXIMIZE, RESTORE, CLOSE)."""
        pass

    @abstractmethod
    def move_cursor(self, x: int, y: int) -> bool:
        """Moves OS mouse cursor to (x, y)."""
        pass

    @abstractmethod
    def click_mouse(self, button: str = "left", double: bool = False) -> bool:
        """Clicks mouse button."""
        pass

    @abstractmethod
    def type_text(self, text: str) -> bool:
        """Types string into focused input."""
        pass

    @abstractmethod
    def get_clipboard_text(self) -> str:
        """Reads clipboard text."""
        pass

    @abstractmethod
    def set_clipboard_text(self, text: str) -> bool:
        """Writes clipboard text."""
        pass
