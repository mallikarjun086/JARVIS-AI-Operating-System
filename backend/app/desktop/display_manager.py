"""
Display Manager — Handles multi-monitor display enumeration and High-DPI scaling awareness.
"""

import sys
from typing import List
import structlog
from app.desktop.schemas import DisplayInfo

logger = structlog.get_logger(__name__)


class DisplayManager:
    """Manages display monitors and OS High-DPI scaling configuration."""

    def __init__(self) -> None:
        self.initialize_dpi_awareness()

    def initialize_dpi_awareness(self) -> None:
        """Configures High-DPI process awareness on Windows OS."""
        if sys.platform == "win32":
            try:
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-monitor DPI aware
                logger.info("Initialized High-DPI process awareness (Per-Monitor v2)")
            except Exception as e:
                logger.warning("Could not set High-DPI awareness", error=str(e))

    def get_displays(self) -> List[DisplayInfo]:
        """Enumerates active display monitors."""
        displays: List[DisplayInfo] = []
        if sys.platform == "win32":
            try:
                import win32api
                import win32con

                monitors = win32api.EnumDisplayMonitors()
                for idx, (hmon, hdc, rect) in enumerate(monitors):
                    info = win32api.GetMonitorInfo(hmon)
                    w = rect[2] - rect[0]
                    h = rect[3] - rect[1]
                    is_primary = (info.get("Flags", 0) & win32con.MONITORINFOF_PRIMARY) != 0

                    displays.append(
                        DisplayInfo(
                            display_index=idx,
                            name=f"Monitor {idx + 1}",
                            width=w,
                            height=h,
                            dpi_scaling=1.0,
                            is_primary=is_primary
                        )
                    )
                if displays:
                    return displays
            except Exception as e:
                logger.warning("Failed EnumDisplayMonitors, returning fallback primary display", error=str(e))

        # Fallback primary display
        return [
            DisplayInfo(
                display_index=0,
                name="Primary Monitor",
                width=1920,
                height=1080,
                dpi_scaling=1.0,
                is_primary=True
            )
        ]


display_manager = DisplayManager()
