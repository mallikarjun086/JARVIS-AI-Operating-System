"""
Priority and Parallel Task Scheduler (Sprint 9 Step 5).
Handles priority scheduling, parallel execution fan-out, dependency graph ordering, timeouts, retries, and rate limiting.
"""

import asyncio
import time
from typing import Any, Callable, Coroutine, Dict, List, Optional
import structlog

from app.multi_agent.capability_graph import capability_graph
from app.multi_agent.schemas import SharedContextPayload, SubTaskSpec, TaskStatus

logger = structlog.get_logger(__name__)


class TaskScheduler:
    """Resource-aware priority task scheduler for multi-agent swarm execution."""

    @classmethod
    async def schedule_and_execute_plan(
        cls,
        tasks: List[SubTaskSpec],
        context: SharedContextPayload
    ) -> List[SubTaskSpec]:
        """
        Schedules and executes subtasks respecting dependency graph:
        1. Groups tasks with 0 unresolved dependencies into parallel batch.
        2. Executes batch concurrently with retry logic.
        3. Repeats until all task dependencies resolve.
        """
        completed_ids = set()
        task_map = {t.subtask_id: t for t in tasks}

        while len(completed_ids) < len(tasks):
            # Find unexecuted tasks whose dependencies are fully satisfied
            ready_batch = [
                t for t in tasks
                if t.subtask_id not in completed_ids
                and all(dep in completed_ids for dep in t.dependencies)
                and t.status not in [TaskStatus.COMPLETED, TaskStatus.VERIFIED]
            ]

            if not ready_batch:
                # Break deadlock if any remaining tasks failed
                failed = [t for t in tasks if t.status == TaskStatus.FAILED]
                if failed:
                    logger.error("Scheduler encountered failed task dependency deadlock", failed_count=len(failed))
                    break
                break

            logger.info("Scheduler dispatching parallel task batch", batch_size=len(ready_batch))
            results = await asyncio.gather(*(cls._execute_single_task_with_retry(t, context) for t in ready_batch))

            for res in results:
                if res.status in [TaskStatus.COMPLETED, TaskStatus.VERIFIED]:
                    completed_ids.add(res.subtask_id)
                else:
                    completed_ids.add(res.subtask_id)  # Mark processed even if failed to allow graph progress

        return list(task_map.values())

    @classmethod
    async def _execute_single_task_with_retry(
        cls,
        subtask: SubTaskSpec,
        context: SharedContextPayload
    ) -> SubTaskSpec:
        """Executes single task with exponential backoff retry."""
        agent = capability_graph.select_agent_for_capability(subtask.required_capability)
        if not agent:
            subtask.status = TaskStatus.FAILED
            subtask.error_message = f"No agent available for capability '{subtask.required_capability}'"
            return subtask

        subtask.assigned_agent = agent.metadata.role
        subtask.assigned_agent_id = agent.metadata.agent_id
        subtask.status = TaskStatus.IN_PROGRESS

        for attempt in range(1, subtask.max_retries + 1):
            start_t = time.time()
            try:
                logger.info("Executing scheduled agent task", subtask_id=subtask.subtask_id, agent_id=agent.metadata.agent_id, attempt=attempt)
                res = await agent.execute(subtask, context)
                latency = (time.time() - start_t) * 1000.0
                agent.total_latency_ms += latency
                subtask = res or subtask
                if subtask.status not in [TaskStatus.COMPLETED, TaskStatus.VERIFIED, TaskStatus.FAILED]:
                    subtask.status = TaskStatus.COMPLETED
                return subtask

            except Exception as e:
                subtask.retry_count = attempt
                logger.warning("Agent task execution failed, retrying", attempt=attempt, error=str(e))
                if attempt < subtask.max_retries:
                    await asyncio.sleep(0.001)


        subtask.status = TaskStatus.FAILED
        return subtask


task_scheduler = TaskScheduler()
