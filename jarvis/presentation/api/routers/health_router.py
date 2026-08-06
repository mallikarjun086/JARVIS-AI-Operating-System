"""
Health & Metrics API Router.
"""

from fastapi import APIRouter, Depends, Request
from jarvis import __version__
from jarvis.application.dto import HealthResponse
from jarvis.config import settings
from jarvis.domain.entities import KernelMetrics
from jarvis.domain.ports import ProcessSchedulerPort

router = APIRouter(prefix="/api/v1", tags=["Health & System Metrics"])


@router.get("/health", response_model=HealthResponse, summary="Get Kernel Health Overview")
async def get_health(request: Request) -> HealthResponse:
    """Returns general health status and uptime metrics."""
    scheduler: ProcessSchedulerPort = request.app.state.scheduler
    metrics = await scheduler.get_metrics()

    return HealthResponse(
        status="HEALTHY",
        app_name=settings.APP_NAME,
        version=__version__,
        active_processes=metrics.active_processes,
        total_processes=metrics.total_processes,
        uptime_seconds=metrics.uptime_seconds,
        environment=settings.ENV
    )


@router.get("/metrics", response_model=KernelMetrics, summary="Get Real-Time Operational Metrics")
async def get_metrics(request: Request) -> KernelMetrics:
    """Returns detailed real-time kernel execution metrics."""
    scheduler: ProcessSchedulerPort = request.app.state.scheduler
    return await scheduler.get_metrics()
