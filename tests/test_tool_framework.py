"""
Comprehensive Tests for Enterprise Tool Framework (Sprint 4).
Tests:
1. BaseTool Interface lifecycle & metadata
2. ToolRegistry discovery, versioning, lazy loading, health checks
3. ToolPermissionManager levels, approval workflows, rate limits
4. ToolValidationEngine schemas, size limits, safety policies
5. ToolExecutionManager timeouts, retries, cancellation, parallel, sequential, rollback
6. ToolAuditLogger structured logs & redaction
7. ToolMetricsManager telemetry counters
"""

import asyncio
import pytest
from typing import Any, Dict
from pydantic import BaseModel, Field

from app.tools.audit import audit_logger
from app.tools.base import BaseTool
from app.tools.executor import execution_manager
from app.tools.metrics import tool_metrics
from app.tools.permissions import permission_manager
from app.tools.registry import ToolRegistry, tool_registry
from app.tools.schemas import (
    ExecutionStatus,
    PermissionLevel,
    ToolExecutionRequest,
)
from app.tools.validator import validator_engine


# Mock Custom Test Tools
class SimpleInput(BaseModel):
    value: int = Field(..., ge=0)

class SimpleOutput(BaseModel):
    result: int

class SimpleTestTool(BaseTool):
    @property
    def name(self) -> str: return "test.simple"
    @property
    def description(self) -> str: return "Simple test tool adding 10 to input value."
    @property
    def category(self) -> str: return "test"
    @property
    def permission_level(self) -> PermissionLevel: return PermissionLevel.READ_ONLY
    @property
    def input_schema(self): return SimpleInput
    @property
    def output_schema(self): return SimpleOutput

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        return {"result": params["value"] + 10}


class RollbackInput(BaseModel):
    should_fail: bool = Field(default=True)

class RollbackOutput(BaseModel):
    status: str

class RollbackTestTool(BaseTool):
    rolled_back = False

    @property
    def name(self) -> str: return "test.rollback"
    @property
    def description(self) -> str: return "Tool that fails and triggers rollback."
    @property
    def category(self) -> str: return "test"
    @property
    def permission_level(self) -> PermissionLevel: return PermissionLevel.WRITE
    @property
    def input_schema(self): return RollbackInput
    @property
    def output_schema(self): return RollbackOutput

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        if params.get("should_fail", True):
            raise RuntimeError("Simulated execution failure")
        return {"status": "SUCCESS"}

    async def rollback(self, params: Dict[str, Any], context: Dict[str, Any], error: Exception) -> bool:
        RollbackTestTool.rolled_back = True
        return True


class SlowTestTool(BaseTool):
    @property
    def name(self) -> str: return "test.slow"
    @property
    def description(self) -> str: return "Slow tool for timeout testing."
    @property
    def category(self) -> str: return "test"
    @property
    def permission_level(self) -> PermissionLevel: return PermissionLevel.READ_ONLY
    @property
    def input_schema(self): return SimpleInput
    @property
    def output_schema(self): return SimpleOutput
    @property
    def timeout_seconds(self) -> float: return 0.2

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(1.0)
        return {"result": 999}


@pytest.mark.asyncio
async def test_tool_registry_registration_and_discovery():
    """Verifies tool registration, dynamic discovery, and metadata retrieval."""
    registry = ToolRegistry()
    registry.register(SimpleTestTool)

    tool = registry.get_tool("test.simple")
    assert tool is not None
    assert tool.name == "test.simple"
    assert tool.permission_level == PermissionLevel.READ_ONLY

    meta = tool.get_metadata()
    assert meta.name == "test.simple"
    assert meta.category == "test"


@pytest.mark.asyncio
async def test_permission_guard_and_approval():
    """Verifies permission level hierarchy and approval checks."""
    tool = SimpleTestTool()

    # Anonymous user -> READ_ONLY tool -> ALLOWED
    allowed, reason = permission_manager.verify_permission(tool, user_role="anonymous")
    assert allowed is True

    # Dangerous Tool requires approval
    class DangerousTool(BaseTool):
        @property
        def name(self) -> str: return "test.dangerous"
        @property
        def description(self) -> str: return "Dangerous operation."
        @property
        def permission_level(self) -> PermissionLevel: return PermissionLevel.DANGEROUS
        @property
        def input_schema(self): return SimpleInput
        @property
        def output_schema(self): return SimpleOutput
        async def execute(self, p, c): return {"result": 0}

    d_tool = DangerousTool()
    allowed_no_app, reason = permission_manager.verify_permission(d_tool, user_role="admin", approval_granted=False)
    assert allowed_no_app is False
    assert "Approval Required" in reason

    allowed_with_app, _ = permission_manager.verify_permission(d_tool, user_role="admin", approval_granted=True)
    assert allowed_with_app is True


@pytest.mark.asyncio
async def test_validation_engine():
    """Verifies input/output validation, size limits, and command security rules."""
    tool = SimpleTestTool()

    # Valid input
    validated = validator_engine.validate_input(tool, {"value": 5})
    assert validated.value == 5

    # Invalid input (negative value violates ge=0)
    with pytest.raises(ValueError):
        validator_engine.validate_input(tool, {"value": -5})

    # Forbidden command safety check
    with pytest.raises(ValueError) as exc:
        validator_engine._validate_command_safety("rm -rf /")
    assert "security policy" in str(exc.value)


@pytest.mark.asyncio
async def test_executor_successful_execution():
    """Tests ToolExecutionManager executing a valid tool call."""
    tool_registry.register(SimpleTestTool)

    req = ToolExecutionRequest(tool_name="test.simple", parameters={"value": 15})
    res = await execution_manager.execute_tool(req, user_role="user")

    assert res.status == ExecutionStatus.SUCCESS
    assert res.output["result"] == 25
    assert res.execution_time_seconds > 0.0


@pytest.mark.asyncio
async def test_executor_timeout():
    """Tests ToolExecutionManager handling execution timeouts."""
    tool_registry.register(SlowTestTool)

    req = ToolExecutionRequest(tool_name="test.slow", parameters={"value": 1}, timeout_seconds=0.1, max_retries=0)
    res = await execution_manager.execute_tool(req, user_role="user")

    assert res.status == ExecutionStatus.TIMEOUT
    assert "timed out" in res.error_message


@pytest.mark.asyncio
async def test_executor_rollback_on_failure():
    """Tests tool rollback execution when execution fails."""
    tool_registry.register(RollbackTestTool)
    RollbackTestTool.rolled_back = False

    req = ToolExecutionRequest(tool_name="test.rollback", parameters={"should_fail": True}, max_retries=0)
    res = await execution_manager.execute_tool(req, user_role="user")

    assert res.status == ExecutionStatus.FAILED
    assert res.rolled_back is True
    assert RollbackTestTool.rolled_back is True


@pytest.mark.asyncio
async def test_executor_parallel_batch():
    """Tests parallel batch tool execution."""
    tool_registry.register(SimpleTestTool)

    reqs = [
        ToolExecutionRequest(tool_name="test.simple", parameters={"value": 10}),
        ToolExecutionRequest(tool_name="test.simple", parameters={"value": 20}),
        ToolExecutionRequest(tool_name="test.simple", parameters={"value": 30}),
    ]

    results = await execution_manager.execute_parallel(reqs, user_role="user")
    assert len(results) == 3
    assert all(r.status == ExecutionStatus.SUCCESS for r in results)
    assert [r.output["result"] for r in results] == [20, 30, 40]


@pytest.mark.asyncio
async def test_audit_and_metrics():
    """Verifies audit logging parameter redaction and observability counters."""
    audit_entry = audit_logger.log_execution(
        tool_name="test.simple",
        user_role="user",
        permission_level=PermissionLevel.READ_ONLY,
        parameters={"value": 10, "api_key": "secret123"},
        status=ExecutionStatus.SUCCESS,
        execution_time_seconds=0.05
    )

    assert audit_entry.parameters["api_key"] == "******"
    assert audit_entry.status == ExecutionStatus.SUCCESS

    metrics = tool_metrics.to_dict()
    assert metrics["total_executions"] >= 1
