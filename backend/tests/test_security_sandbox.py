"""
Unit tests for Enterprise Process Execution Engine & Sandbox.
"""

import pytest
from app.security.command_guard import command_guard
from app.security.schemas import ProcessExecutionRequest, ProcessExecutionStatus
from app.security.sandbox import LocalProcessExecutor, ProcessSandboxEngine


@pytest.mark.asyncio
async def test_async_process_execution_success():
    executor = LocalProcessExecutor()
    req = ProcessExecutionRequest(command="echo 'Process Engine Verified'", timeout_seconds=5)
    res = await executor.execute(req)

    assert res.status == ProcessExecutionStatus.COMPLETED
    assert res.exit_code == 0
    assert "Process Engine Verified" in res.stdout
    assert res.sandboxed is True
    assert res.blocked is False


@pytest.mark.asyncio
async def test_command_injection_blocked():
    executor = LocalProcessExecutor()
    req = ProcessExecutionRequest(command="echo hello; rm -rf /", timeout_seconds=5)
    res = await executor.execute(req)

    assert res.status == ProcessExecutionStatus.BLOCKED_SECURITY
    assert res.blocked is True
    assert "Blocked by Command Injection Guard" in res.stderr


@pytest.mark.asyncio
async def test_human_approval_gatekeeper():
    executor = LocalProcessExecutor()
    req = ProcessExecutionRequest(command="format C:", timeout_seconds=5)
    res = await executor.execute(req)

    assert res.status == ProcessExecutionStatus.REQUIRES_HUMAN_APPROVAL
    assert res.requires_approval is True
    assert "Human Approval" in res.stderr


@pytest.mark.asyncio
async def test_environment_sanitization():
    executor = LocalProcessExecutor()
    res_env = executor._sanitize_environment({"CUSTOM_VAR": "SAFE_VALUE"})
    assert "SECRET_KEY" not in res_env
    assert "POSTGRES_PASSWORD" not in res_env
    assert res_env.get("CUSTOM_VAR") == "SAFE_VALUE"


@pytest.mark.asyncio
async def test_process_timeout_handling():
    executor = LocalProcessExecutor()
    req = ProcessExecutionRequest(command="ping 127.0.0.1 -n 10", timeout_seconds=1)
    res = await executor.execute(req)

    assert res.status == ProcessExecutionStatus.TIMED_OUT
    assert res.blocked is True
    assert "timed out" in res.stderr.lower()




@pytest.mark.asyncio
async def test_command_tokenization_and_allowlist():
    tokens = command_guard.tokenize_command("python -c \"print('Hello')\"")
    assert tokens[0] == "python"
    assert "python" in command_guard.ALLOWED_EXECUTABLES


@pytest.mark.asyncio
async def test_health_and_metrics_telemetry():
    executor = LocalProcessExecutor()
    req = ProcessExecutionRequest(command="echo 'Telemetry'", timeout_seconds=5)
    await executor.execute(req)

    health = executor.get_health_status()
    metrics = executor.get_metrics()

    assert health["status"] == "HEALTHY"
    assert metrics["total_executions"] >= 1
    assert metrics["successful_executions"] >= 1


@pytest.mark.asyncio
async def test_sandbox_engine_facade():
    engine = ProcessSandboxEngine()
    res = await engine.execute_in_sandbox_async("echo 'Facade Test'", timeout_seconds=5)
    assert res.status == ProcessExecutionStatus.COMPLETED
    assert "Facade Test" in res.stdout

    sync_res = engine.execute_in_sandbox("echo 'Sync Facade Test'", timeout_seconds=5)
    assert sync_res["exit_code"] == 0
    assert "Sync Facade Test" in sync_res["stdout"]
