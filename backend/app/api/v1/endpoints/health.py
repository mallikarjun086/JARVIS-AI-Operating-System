"""
Health and Database Readiness Endpoint Handlers.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.config import settings

from app.core.health_manager import global_health_manager

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK, summary="Global Subsystem Health Summary")
async def health_check():
    """Summary health check returning aggregate system status."""
    return await global_health_manager.get_summary_health()


@router.get("/health/full", status_code=status.HTTP_200_OK, summary="Full System Diagnostic Health Report")
async def full_health_check():
    """Detailed health report inspecting latencies, versions, and dependencies of all 7 core subsystems."""
    return await global_health_manager.get_full_health()


@router.get("/health/readiness", status_code=status.HTTP_200_OK, summary="Database Readiness Check")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Verifies backend database connection pool readiness."""
    try:
        await db.execute(text("SELECT 1"))
        return {
            "status": "READY",
            "database": "CONNECTED",
            "app_name": settings.APP_NAME
        }
    except Exception as e:
        return {
            "status": "UNREADY",
            "database": "DISCONNECTED",
            "error": str(e)
        }
