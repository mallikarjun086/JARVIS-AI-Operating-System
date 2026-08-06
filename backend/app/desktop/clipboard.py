"""
Clipboard Manager — Manages OS clipboard read/write and history.
"""

from typing import List, Optional
import structlog
from app.desktop.platform.windows import windows_adapter

logger = structlog.get_logger(__name__)


class ClipboardManager:
    """Manages system clipboard operations and history."""

    def __init__(self) -> None:
        self._history: List[str] = []

    def get_text(self) -> str:
        """Reads current clipboard text content."""
        return windows_adapter.get_clipboard_text()

    def set_text(self, text: str) -> None:
        """Writes text content to clipboard."""
        windows_adapter.set_clipboard_text(text)
        self._history.append(text)
        if len(self._history) > 50:
            self._history.pop(0)

    def clear(self) -> None:
        """Clears clipboard."""
        windows_adapter.set_clipboard_text("")

    def get_history(self) -> List[str]:
        """Returns clipboard text history."""
        return list(self._history)


clipboard_manager = ClipboardManager()
