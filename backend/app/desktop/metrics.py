"""
Desktop Telemetry Metrics Manager.
Tracks window discovery latency, UI lookup latency, OCR latency, input latency, launch latency, recoveries, and event counts.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class DesktopMetricsManager:
    """Thread-safe telemetry counter for Desktop Automation Engine."""

    total_app_launches: int = 0
    total_window_operations: int = 0
    total_mouse_events: int = 0
    total_keyboard_events: int = 0
    total_ocr_extractions: int = 0
    total_clipboard_events: int = 0
    total_recoveries: int = 0
    total_failures: int = 0
    total_approvals_requested: int = 0

    total_window_discovery_ms: float = 0.0
    total_ui_lookup_ms: float = 0.0
    total_ocr_latency_ms: float = 0.0
    total_input_latency_ms: float = 0.0
    total_launch_latency_ms: float = 0.0

    def record_window_discovery(self, latency_ms: float) -> None:
        self.total_window_operations += 1
        self.total_window_discovery_ms += latency_ms

    def record_ocr_extraction(self, latency_ms: float) -> None:
        self.total_ocr_extractions += 1
        self.total_ocr_latency_ms += latency_ms

    def record_input_event(self, event_type: str, latency_ms: float) -> None:
        if event_type == "mouse":
            self.total_mouse_events += 1
        elif event_type == "keyboard":
            self.total_keyboard_events += 1
        self.total_input_latency_ms += latency_ms

    def record_launch(self, latency_ms: float) -> None:
        self.total_app_launches += 1
        self.total_launch_latency_ms += latency_ms

    def record_recovery(self) -> None:
        self.total_recoveries += 1

    @property
    def avg_window_discovery_ms(self) -> float:
        return round(self.total_window_discovery_ms / max(1, self.total_window_operations), 2)

    @property
    def avg_ocr_latency_ms(self) -> float:
        return round(self.total_ocr_latency_ms / max(1, self.total_ocr_extractions), 2)

    @property
    def avg_input_latency_ms(self) -> float:
        total_input = self.total_mouse_events + self.total_keyboard_events
        return round(self.total_input_latency_ms / max(1, total_input), 2)

    @property
    def avg_launch_latency_ms(self) -> float:
        return round(self.total_launch_latency_ms / max(1, self.total_app_launches), 2)

    @property
    def automation_success_rate(self) -> float:
        total_ops = self.total_window_operations + self.total_mouse_events + self.total_keyboard_events
        if total_ops == 0:
            return 100.0
        successes = max(0, total_ops - self.total_failures)
        return round((successes / total_ops) * 100.0, 2)

    def to_dict(self) -> dict:
        return {
            "total_app_launches": self.total_app_launches,
            "total_window_operations": self.total_window_operations,
            "total_mouse_events": self.total_mouse_events,
            "total_keyboard_events": self.total_keyboard_events,
            "total_ocr_extractions": self.total_ocr_extractions,
            "total_clipboard_events": self.total_clipboard_events,
            "total_recoveries": self.total_recoveries,
            "total_failures": self.total_failures,
            "total_approvals_requested": self.total_approvals_requested,
            "avg_window_discovery_ms": self.avg_window_discovery_ms,
            "avg_ocr_latency_ms": self.avg_ocr_latency_ms,
            "avg_input_latency_ms": self.avg_input_latency_ms,
            "avg_launch_latency_ms": self.avg_launch_latency_ms,
            "automation_success_rate": self.automation_success_rate,
        }


desktop_metrics = DesktopMetricsManager()
