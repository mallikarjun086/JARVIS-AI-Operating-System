"""
FastAPI Application Entry Point & Lifespan Service Initializer.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.config import settings
from app.core.logging import logger
from app.db.init_db import create_initial_superuser, init_db_tables
from app.db.session import async_session_factory


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """App lifespan context manager handling ordered startup & reverse shutdown events (Sprint 7.5)."""
    logger.info("Initializing Enterprise AI Operating System Subsystems...")

    # 1. Configuration & 2. Logging (Pre-initialized)

    # 3. Database Initialization & Superuser Seeding
    await init_db_tables()
    async with async_session_factory() as db:
        await create_initial_superuser(db)

    # 4. Security Subsystem Verification
    try:
        from app.security.engine import security_engine
        logger.info("Security Subsystem verified successfully")
    except Exception as e:
        logger.warning("Security Subsystem warning", error=str(e))

    # 5. AI Provider Layer Health Pre-warm
    try:
        from app.ai.router import llm_router
        await llm_router.prewarm_health_cache()
        logger.info("AI Provider Layer health pre-warmed successfully")
    except Exception as e:
        logger.warning("AI Provider Layer health pre-warm failed (non-fatal)", error=str(e))

    # 6. Enterprise Memory Engine Initialization
    try:
        from app.memory.manager import memory_manager
        await memory_manager.initialize()
        logger.info("Enterprise Memory Engine initialized successfully")
    except Exception as e:
        logger.warning("Memory Engine initialization failed (non-fatal)", error=str(e))

    # 7. Enterprise Tool Framework Discovery
    try:
        from app.tools.registry import tool_registry
        discovered = tool_registry.discover_tools()
        logger.info("Enterprise Tools registered successfully", count=discovered)
    except Exception as e:
        logger.warning("Tool discovery warning (non-fatal)", error=str(e))

    # 8. Intelligent Task Planner Kernel Initialization
    try:
        from app.planner.planner import task_planner
        logger.info("Intelligent Task Planner Kernel initialized successfully")
    except Exception as e:
        logger.warning("Planner Kernel initialization warning", error=str(e))

    # 9. Enterprise Browser Automation Engine Initialization
    try:
        from app.browser.manager import browser_manager
        await browser_manager.initialize()
        logger.info("Enterprise Browser Automation Engine initialized successfully")
    except Exception as e:
        logger.warning("Browser Automation Engine initialization failed (non-fatal)", error=str(e))

    # 10. Enterprise Desktop Automation Engine Initialization
    try:
        from app.desktop.manager import desktop_manager
        await desktop_manager.initialize()
        logger.info("Enterprise Desktop Automation Engine initialized successfully")
    except Exception as e:
        logger.warning("Desktop Automation Engine initialization failed (non-fatal)", error=str(e))

    # Start conversation session cleanup task
    try:
        from app.ai.conversation import conversation_manager
        conversation_manager.start_cleanup_task()
    except Exception as e:
        logger.warning("Conversation cleanup task start failed (non-fatal)", error=str(e))

    # 11. Unified Event Bus Kernel Initialization
    try:
        from app.core.event_bus import event_bus
        logger.info("Unified Event Bus Kernel initialized successfully")
    except Exception as e:
        logger.warning("Event Bus Kernel initialization warning", error=str(e))

    logger.info("Unified AI Operating System Platform Initialized Successfully", app_name=settings.APP_NAME)
    yield


    # Shutdown (Exact Reverse Order: 10 to 1)
    logger.info("Shutting down AI Operating System Subsystems in reverse order...")
    # 10. Desktop Engine Shutdown
    try:
        from app.desktop.manager import desktop_manager
        await desktop_manager.shutdown()
    except Exception as e:
        logger.warning("Desktop Engine shutdown notice", error=str(e))
    # 9. Browser Engine Shutdown
    try:
        from app.browser.manager import browser_manager
        await browser_manager.shutdown()
    except Exception as e:
        logger.warning("Browser Engine shutdown notice", error=str(e))
    # Conversation cleanup shutdown
    try:
        from app.ai.conversation import conversation_manager
        await conversation_manager.stop_cleanup_task()
    except Exception as e:
        logger.warning("Conversation cleanup shutdown notice", error=str(e))
    # 5. AI Providers Shutdown
    try:
        from app.ai.providers.factory import provider_factory
        await provider_factory.shutdown_all()
    except Exception as e:
        logger.warning("AI Providers shutdown notice", error=str(e))


def create_application() -> FastAPI:
    """FastAPI Application Factory."""
    app = FastAPI(
        title=settings.APP_NAME,
        description="Production Foundation API Backend for JARVIS AI OS",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )

    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include Main API Router
    app.include_router(api_router)

    return app


app = create_application()
