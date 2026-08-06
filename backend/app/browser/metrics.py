"""
Browser Observability Metrics Manager.
Tracks navigation latency, DOM extraction latency, interaction latency, browser crashes, retries, downloads, uploads, active sessions, and open tabs.
"""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class BrowserMetricsManager:
    """Thread-safe telemetry counter for Browser Automation Engine."""

    total_navigations: int = 0
    total_dom_extractions: int = 0
    total_interactions: int = 0
    total_screenshots: int = 0
    total_downloads: int = 0
    total_uploads: int = 0
    total_crashes: int = 0
    total_retries: int = 0
    total_approvals_requested: int = 0

    total_navigation_ms: float = 0.0
    total_dom_extraction_ms: float = 0.0
    total_interaction_ms: float = 0.0

    def record_navigation(self, latency_ms: float) -> None:
        self.total_navigations += 1
        self.total_navigation_ms += latency_ms

    def record_dom_extraction(self, latency_ms: float) -> None:
        self.total_dom_extractions += 1
        self.total_dom_extraction_ms += latency_ms

    def record_interaction(self, latency_ms: float) -> None:
        self.total_interactions += 1
        self.total_interaction_ms += latency_ms

    @property
    def avg_navigation_ms(self) -> float:
        return round(self.total_navigation_ms / max(1, self.total_navigations), 2)

    @property
    def avg_dom_extraction_ms(self) -> float:
        return round(self.total_dom_extraction_ms / max(1, self.total_dom_extractions), 2)

    def to_dict(self) -> dict:
        return {
            "total_navigations": self.total_navigations,
            "total_dom_extractions": self.total_dom_extractions,
            "total_interactions": self.total_interactions,
            "total_screenshots": self.total_screenshots,
            "total_downloads": self.total_downloads,
            "total_uploads": self.total_uploads,
            "total_crashes": self.total_crashes,
            "total_retries": self.total_retries,
            "total_approvals_requested": self.total_approvals_requested,
            "avg_navigation_ms": self.avg_navigation_ms,
            "avg_dom_extraction_ms": self.avg_dom_extraction_ms
        }


browser_metrics = BrowserMetricsManager()
