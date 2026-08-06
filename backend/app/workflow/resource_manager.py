"""
Resource Reservation Manager for Workflow Scheduler (Sprint 10).
Reserves CPU, RAM, GPU, Browser Sessions, Desktop Sessions, and LLM Budget prior to execution.
"""

from typing import Any, Dict
import structlog

from app.workflow.schemas import ResourceReservation

logger = structlog.get_logger(__name__)


class ResourceReservationManager:
    """Manages pre-execution system resource allocation and release."""

    def __init__(self) -> None:
        self.allocated_cpu: float = 0.0
        self.allocated_ram_mb: float = 0.0
        self.allocated_browser_sessions: int = 0
        self.allocated_desktop_sessions: int = 0
        self.allocated_llm_tokens: int = 0

    def reserve_resources(self, req: ResourceReservation) -> bool:
        """Reserves requested compute and session resources."""
        self.allocated_cpu += req.cpu_cores
        self.allocated_ram_mb += req.ram_mb
        self.allocated_browser_sessions += req.browser_sessions
        self.allocated_desktop_sessions += req.desktop_sessions
        self.allocated_llm_tokens += req.llm_budget_tokens

        logger.info(
            "Reserved workflow resources",
            cpu=req.cpu_cores,
            ram_mb=req.ram_mb,
            browser_sessions=req.browser_sessions,
            llm_tokens=req.llm_budget_tokens
        )
        return True

    def release_resources(self, req: ResourceReservation) -> None:
        """Releases previously allocated resources upon workflow completion or cancellation."""
        self.allocated_cpu = max(0.0, self.allocated_cpu - req.cpu_cores)
        self.allocated_ram_mb = max(0.0, self.allocated_ram_mb - req.ram_mb)
        self.allocated_browser_sessions = max(0, self.allocated_browser_sessions - req.browser_sessions)
        self.allocated_desktop_sessions = max(0, self.allocated_desktop_sessions - req.desktop_sessions)
        self.allocated_llm_tokens = max(0, self.allocated_llm_tokens - req.llm_budget_tokens)

        logger.info("Released workflow resources", cpu=req.cpu_cores, ram_mb=req.ram_mb)

    def get_resource_usage(self) -> Dict[str, Any]:
        """Returns current allocated resource metrics."""
        return {
            "allocated_cpu": self.allocated_cpu,
            "allocated_ram_mb": self.allocated_ram_mb,
            "allocated_browser_sessions": self.allocated_browser_sessions,
            "allocated_desktop_sessions": self.allocated_desktop_sessions,
            "allocated_llm_tokens": self.allocated_llm_tokens
        }


resource_reservation_manager = ResourceReservationManager()
