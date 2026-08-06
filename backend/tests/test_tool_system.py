"""
Pytest Test Suite for Tool System Framework.
Tests every framework feature: BaseTool contract, ToolRegistry, permissions, validation, timeouts, retries, and parallel execution.
"""

import asyncio
from typing import Any, Dict, Type
from httpx import AsyncClient
import pytest
from pydantic import BaseModel, Field
from app.tools.base import BaseTool
from app.tools.executor import execution_manager
from app.tools.registry import register_tool, tool_registry
from app.tools.schemas import ExecutionStatus, PermissionLevel, ToolExecutionRequest

# --- Test Mock Tool Implementations ---


class EchoInputSchema(BaseModel):
    message: str = Field(..., description="Message to echo back")


class EchoOutputSchema(BaseModel):
    echo: str = Field(...)


class EchoTestTool(BaseTool):
    @property
    def name(self) -> str:
        return "test_echo_tool"

    @property
    def description(self) -> str:
        return "Test echo tool for schema validation testing."

    @property
    def permission_level(self) -> PermissionLevel:
        return PermissionLevel.USER_READ

    @property
    def input_schema(self) -> Type[BaseModel]:
        return EchoInputSchema

    @property
    def output_schema(self) -> Type[BaseModel]:
        return EchoOutputSchema

    async def execute_async(self, params: Dict[str, Any], context: Dict[str, Any]) -> Any:
        return {"echo": f"Echo: {params['message']}"}


class TimeoutTestTool(BaseTool):
    @property
    def name(self) -> str:
        return "test_timeout_tool"

    @property
    def description(self) -> str:
        return "Tool that sleeps to trigger timeout."

    @property
    def permission_level(self) -> PermissionLevel:
        return PermissionLevel.USER_READ

    @property
    def input_schema(self) -> Type[BaseModel]:
        return EchoInputSchema

    @property
    def output_schema(self) -> Type[BaseModel]:
        return EchoOutputSchema

    @property
    def timeout_seconds(self) -> float:
        return 0.1

    @property
    def max_retries(self) -> int:
        return 1

    async def execute_async(self, params: Dict[str, Any], context: Dict[str, Any]) -> Any:
        await asyncio.sleep(0.5)  # Triggers timeout!
        return {"echo": "Done"}


class CriticalAdminTool(BaseTool):
    @property
    def name(self) -> str:
        return "test_critical_admin_tool"

    @property
    def description(self) -> str:
        return "Critical administrative tool."

    @property
    def permission_level(self) -> PermissionLevel:
        return PermissionLevel.CRITICAL_SYSTEM

    @property
    def input_schema(self) -> Type[BaseModel]:
        return EchoInputSchema

    @property
    def output_schema(self) -> Type[BaseModel]:
        return EchoOutputSchema

    async def execute_async(self, params: Dict[str, Any], context: Dict[str, Any]) -> Any:
        return {"echo": "Admin Success"}


# --- Pytest Tests ---


@pytest.fixture(autouse=True)
def setup_test_tools():
    """Registers test tools into tool_registry."""
    tool_registry.register(EchoTestTool())
    tool_registry.register(TimeoutTestTool())
    tool_registry.register(CriticalAdminTool())


@pytest.mark.asyncio
async def test_tool_registry_and_metadata():
    """Verifies tool registry lookup and metadata generation."""
    tool = tool_registry.get_tool("test_echo_tool")
    assert tool is not None
    meta = tool.get_metadata()
    assert meta.name == "test_echo_tool"
    assert meta.permission_level == PermissionLevel.USER_READ
    assert "properties" in meta.input_schema_json


@pytest.mark.asyncio
async def test_tool_execution_success():
    """Verifies successful tool execution and input/output validation."""
    req = ToolExecutionRequest(tool_name="test_echo_tool", parameters={"message": "JARVIS Framework"})
    res = await execution_manager.execute_tool(req, user_role="user")

    assert res.status == ExecutionStatus.SUCCESS
    assert res.output["echo"] == "Echo: JARVIS Framework"
    assert res.execution_time_seconds > 0.0


@pytest.mark.asyncio
async def test_permission_denied_enforcement():
    """Verifies permission guard blocks user role from CRITICAL_SYSTEM tools."""
    req = ToolExecutionRequest(tool_name="test_critical_admin_tool", parameters={"message": "System test"})
    res = await execution_manager.execute_tool(req, user_role="user")

    assert res.status == ExecutionStatus.PERMISSION_DENIED
    assert "Access denied" in res.error_message


@pytest.mark.asyncio
async def test_timeout_and_retry_handling():
    """Verifies execution timeout enforcement and retries."""
    req = ToolExecutionRequest(tool_name="test_timeout_tool", parameters={"message": "Slow request"}, timeout_seconds=0.1, max_retries=1)
    res = await execution_manager.execute_tool(req, user_role="user")

    assert res.status == ExecutionStatus.TIMEOUT
    assert res.retry_count == 1
    assert "timed out" in res.error_message


@pytest.mark.asyncio
async def test_parallel_tool_execution():
    """Verifies concurrent parallel execution of multiple tools using asyncio.gather."""
    req1 = ToolExecutionRequest(tool_name="test_echo_tool", parameters={"message": "Parallel Task 1"})
    req2 = ToolExecutionRequest(tool_name="test_echo_tool", parameters={"message": "Parallel Task 2"})

    results = await execution_manager.execute_parallel([req1, req2], user_role="user")

    assert len(results) == 2
    assert results[0].status == ExecutionStatus.SUCCESS
    assert results[1].status == ExecutionStatus.SUCCESS
    assert results[0].output["echo"] == "Echo: Parallel Task 1"
    assert results[1].output["echo"] == "Echo: Parallel Task 2"


@pytest.mark.asyncio
async def test_tools_api_endpoints(client: AsyncClient):
    """Tests FastAPI REST endpoints for tool discovery and execution."""
    # Register & login
    await client.post("/api/v1/auth/register", json={"email": "tooluser@jarvis.ai", "password": "Password123!", "full_name": "Tool User"})
    login_resp = await client.post("/api/v1/auth/login", data={"username": "tooluser@jarvis.ai", "password": "Password123!"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # List Tools
    list_resp = await client.get("/api/v1/tools", headers=headers)
    assert list_resp.status_code == 200
    tools = list_resp.json()
    assert len(tools) >= 3

    # Execute Tool via API
    exec_payload = {"tool_name": "test_echo_tool", "parameters": {"message": "API Test"}}
    exec_resp = await client.post("/api/v1/tools/execute", json=exec_payload, headers=headers)
    assert exec_resp.status_code == 200
    res_data = exec_resp.json()
    assert res_data["status"] == "SUCCESS"
    assert res_data["output"]["echo"] == "Echo: API Test"
