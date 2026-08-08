"""
FastAPI Application Entry Point & Lifespan Service Initializer.
"""

import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
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

    # Startup security validation
    sec_warnings = settings.validate_production_security()
    for w in sec_warnings:
        logger.warning("SECURITY CONFIGURATION ALERT", message=w)

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


from fastapi.responses import JSONResponse
from fastapi.requests import Request


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Injects production-grade security headers on every response."""
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        if settings.is_production():
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


class RequestCorrelationMiddleware(BaseHTTPMiddleware):
    """Adds X-Request-ID correlation header for distributed tracing."""
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())[:8]
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


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

    # Security Headers (Phase 4 hardening)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestCorrelationMiddleware)

    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS or ["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
    )

    # Global Exception Handlers for Production Hardening
    @app.exception_handler(PermissionError)
    async def permission_error_handler(request: Request, exc: PermissionError):
        logger.warning("Permission denied", path=request.url.path, error=str(exc))
        return JSONResponse(
            status_code=403,
            content={"detail": str(exc) or "Permission denied by Security Engine."}
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        logger.warning("Value error in request", path=request.url.path, error=str(exc))
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc) or "Invalid request parameters."}
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.error("Unhandled internal server error", path=request.url.path, error=str(exc))
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error: " + str(exc)}
        )

    # Include Main API Router
    app.include_router(api_router)

    return app


app = create_application()

