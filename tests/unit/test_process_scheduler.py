"""
Unit Tests for Process Scheduler Engine.
"""

import pytest
from jarvis.domain.entities import AgentProcess, TaskContext
from jarvis.domain.value_objects import ProcessStatus, TaskPriority
from jarvis.infrastructure.scheduler.process_scheduler import ProcessScheduler


@pytest.mark.asyncio
async def test_scheduler_process_submission_and_metrics():
    """Tests submitting processes and verifying scheduler metrics."""
    scheduler = ProcessScheduler()
    await scheduler.start()

    ctx = TaskContext(goal="Run benchmark test", priority=TaskPriority.HIGH)
    proc = AgentProcess(agent_name="BenchmarkAgent", task_context=ctx)

    proc_id = await scheduler.submit_process(proc)
    assert proc_id == proc.process_id

    fetched = await scheduler.get_process(proc_id)
    assert fetched is not None
    assert fetched.agent_name == "BenchmarkAgent"

    metrics = await scheduler.get_metrics()
    assert metrics.total_processes == 1

    await scheduler.stop()


@pytest.mark.asyncio
async def test_scheduler_process_cancellation():
    """Tests cancelling a queued process."""
    scheduler = ProcessScheduler()
    await scheduler.start()

    ctx = TaskContext(goal="Long running task", priority=TaskPriority.LOW)
    proc = AgentProcess(agent_name="CancelAgent", task_context=ctx)

    proc_id = await scheduler.submit_process(proc)
    cancelled = await scheduler.cancel_process(proc_id)
    assert cancelled is True

    fetched = await scheduler.get_process(proc_id)
    assert fetched.status == ProcessStatus.CANCELLED

    await scheduler.stop()
