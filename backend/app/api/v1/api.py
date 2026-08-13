"""
Primary v1 API Router Assembly.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    ai,
    auth,
    automation,
    browser,
    desktop,
    health,
    jarvis,
    memory,
    metrics,
    multi_agent,
    planner,
    security,
    swe_agent,
    tools,
    users,
    vision,
    voice,
    workflow,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router, tags=["System Health"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["Observability"])
api_router.include_router(jarvis.router, prefix="/jarvis", tags=["JARVIS Multimodal Orchestration"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["User Management"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI Core Kernel"])
api_router.include_router(memory.router, prefix="/memory", tags=["Long-Term Memory Subsystem"])
api_router.include_router(planner.router, prefix="/planner", tags=["Intelligent Task Planner"])
api_router.include_router(tools.router, prefix="/tools", tags=["Tool System Framework"])
api_router.include_router(automation.router, prefix="/automation", tags=["Windows Desktop Automation"])
api_router.include_router(browser.router, prefix="/browser", tags=["Playwright Browser Automation"])
api_router.include_router(desktop.router, prefix="/desktop", tags=["Enterprise Desktop Automation"])
api_router.include_router(swe_agent.router, prefix="/swe-agent", tags=["Software Engineering Agent"])
api_router.include_router(multi_agent.router, prefix="/multi-agent", tags=["Multi-Agent Swarm Orchestration"])
api_router.include_router(vision.router, prefix="/vision", tags=["Computer Vision Subsystem"])
api_router.include_router(voice.router, prefix="/voice", tags=["Voice Assistant Subsystem"])
api_router.include_router(workflow.router, prefix="/workflow", tags=["Workflow Automation Subsystem"])
api_router.include_router(workflow.router, prefix="/workflows", tags=["Workflow Automation Subsystem"])
api_router.include_router(security.router, prefix="/security", tags=["Enterprise Security & Hardening"])
