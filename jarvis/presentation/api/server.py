"""
FastAPI Server Application Factory and Lifespan Initialization.
Wires together Domain, Application, and Infrastructure layers.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from jarvis import __version__
from jarvis.application.use_cases.task_use_cases import ExecuteTaskUseCase
from jarvis.config import settings
from jarvis.domain.exceptions import JARVISError, ProcessNotFoundError, SecurityViolationError
from jarvis.infrastructure.llm.llm_gateway import LLMGateway
from jarvis.infrastructure.logging.logger import get_logger
from jarvis.infrastructure.memory.vector_store import VectorMemoryStore
from jarvis.infrastructure.persistence.database import init_db
from jarvis.infrastructure.scheduler.process_scheduler import ProcessScheduler
from jarvis.infrastructure.tools.system_tools import ToolRegistry
from jarvis.presentation.api.routers import health_router, memory_router, process_router, task_router
from jarvis.presentation.api.websocket import router as websocket_router

logger = get_logger("jarvis.server")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan setup and teardown manager."""
    logger.info("Initializing JARVIS AI Operating System Kernel Services...")

    # 1. Initialize DB tables
    await init_db()

    # 2. Instantiate infrastructure singletons
    llm_provider = LLMGateway()
    vector_store = VectorMemoryStore(llm_provider=llm_provider)
    tool_registry = ToolRegistry()

    # 3. Create Task Execution UseCase handler
    execute_task_use_case = ExecuteTaskUseCase(
        llm_provider=llm_provider,
        tool_registry=tool_registry,
        vector_store=vector_store
    )

    # 4. Instantiate and start Process Scheduler Kernel
    scheduler = ProcessScheduler(task_executor_func=execute_task_use_case.execute)
    await scheduler.start()

    # 5. Attach services to app.state
    app.state.llm_provider = llm_provider
    app.state.vector_store = vector_store
    app.state.tool_registry = tool_registry
    app.state.scheduler = scheduler

    logger.info("JARVIS AI OS Kernel initialized successfully", version=__version__)
    yield

    # Shutdown teardown
    logger.info("Shutting down JARVIS AI Operating System Kernel...")
    await scheduler.stop()
    logger.info("Kernel shutdown complete.")


def create_app() -> FastAPI:
    """FastAPI Application Factory."""
    app = FastAPI(
        title=settings.APP_NAME,
        description="Enterprise Autonomous Multi-Agent AI Operating System Kernel",
        version=__version__,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )

    # Add CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include Routers
    app.include_router(health_router.router)
    app.include_router(process_router.router)
    app.include_router(task_router.router)
    app.include_router(memory_router.router)
    app.include_router(websocket_router)

    # Global Exception Handlers
    @app.exception_handler(JARVISError)
    async def jarvis_error_handler(request: Request, exc: JARVISError) -> JSONResponse:
        logger.error("Domain Error", error=exc.message, details=exc.details)
        status_code = status.HTTP_400_BAD_REQUEST
        if isinstance(exc, ProcessNotFoundError):
            status_code = status.HTTP_404_NOT_FOUND
        elif isinstance(exc, SecurityViolationError):
            status_code = status.HTTP_403_FORBIDDEN

        return JSONResponse(
            status_code=status_code,
            content={"error": exc.message, "details": exc.details}
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error("Unhandled System Exception", error=str(exc))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Internal System Error", "details": str(exc)}
        )

    return app


# Default ASGI App Instance
app = create_app()
