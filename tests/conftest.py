"""
Pytest Async Fixtures for Unit and Integration Testing.
"""

from typing import AsyncGenerator
from httpx import ASGITransport, AsyncClient
import pytest
from jarvis.infrastructure.llm.llm_gateway import LLMGateway
from jarvis.infrastructure.memory.vector_store import VectorMemoryStore
from jarvis.infrastructure.scheduler.process_scheduler import ProcessScheduler
from jarvis.infrastructure.security.sandbox import SecuritySandbox
from jarvis.infrastructure.tools.system_tools import ToolRegistry
from jarvis.presentation.api.server import create_app


@pytest.fixture
def mock_llm_gateway() -> LLMGateway:
    """Fixture providing an offline LLMGateway instance."""
    return LLMGateway(fallback_mode=True)


@pytest.fixture
def vector_store(mock_llm_gateway: LLMGateway) -> VectorMemoryStore:
    """Fixture providing a VectorMemoryStore instance."""
    return VectorMemoryStore(llm_provider=mock_llm_gateway, storage_path=None)


@pytest.fixture
def tool_registry() -> ToolRegistry:
    """Fixture providing a ToolRegistry instance with default tools."""
    return ToolRegistry()


@pytest.fixture
def sandbox() -> SecuritySandbox:
    """Fixture providing SecuritySandbox instance."""
    return SecuritySandbox()


@pytest.fixture
async def scheduler() -> AsyncGenerator[ProcessScheduler, None]:
    """Async fixture providing running ProcessScheduler."""
    sched = ProcessScheduler()
    await sched.start()
    yield sched
    await sched.stop()


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP Client fixture for testing API endpoints."""
    app = create_app()
    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client
