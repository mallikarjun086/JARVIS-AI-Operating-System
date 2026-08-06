"""
Unit Tests for JARVIS Domain Entities and Value Objects.
"""

import pytest
from jarvis.domain.entities import AgentProcess, TaskContext, ToolDefinition
from jarvis.domain.value_objects import MemoryType, ProcessStatus, TaskPriority, ToolPermission


def test_task_context_creation():
    """Verifies TaskContext initialization and step logging."""
    ctx = TaskContext(goal="Create automated unit tests", priority=TaskPriority.HIGH)
    assert ctx.goal == "Create automated unit tests"
    assert ctx.priority == TaskPriority.HIGH
    assert ctx.status == ProcessStatus.CREATED
    assert ctx.current_step == 0
    assert len(ctx.history) == 0

    ctx.add_step_log(1, "Tool Exec", {"output": "ok"})
    assert ctx.current_step == 1
    assert len(ctx.history) == 1
    assert ctx.history[0]["step"] == 1


def test_agent_process_status_transitions():
    """Verifies AgentProcess state machine transitions."""
    ctx = TaskContext(goal="Deploy service")
    proc = AgentProcess(agent_name="DeployAgent", task_context=ctx)

    assert proc.status == ProcessStatus.CREATED
    assert proc.completed_at is None

    proc.update_status(ProcessStatus.RUNNING)
    assert proc.status == ProcessStatus.RUNNING

    proc.update_status(ProcessStatus.COMPLETED)
    assert proc.status == ProcessStatus.COMPLETED
    assert proc.completed_at is not None


def test_tool_definition_immutability():
    """Verifies ToolDefinition model validation."""
    tool = ToolDefinition(
        name="test_tool",
        description="A test tool definition",
        permission_required=ToolPermission.FILE_WRITE
    )
    assert tool.name == "test_tool"
    assert tool.permission_required == ToolPermission.FILE_WRITE
