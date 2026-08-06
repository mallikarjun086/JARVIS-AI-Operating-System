"""
Async Priority Queue Process Scheduler Kernel for JARVIS AI OS.
Manages process scheduling, concurrent worker pools, and system metrics.
"""

import asyncio
from datetime import datetime
import time
from typing import Dict, List, Optional
from jarvis.config import settings
from jarvis.domain.entities import AgentProcess, KernelMetrics
from jarvis.domain.exceptions import ProcessNotFoundError
from jarvis.domain.ports import ProcessSchedulerPort
from jarvis.domain.value_objects import ProcessStatus
from jarvis.infrastructure.logging.logger import get_logger

logger = get_logger("jarvis.process_scheduler")


class ProcessScheduler(ProcessSchedulerPort):
    """
    Non-blocking Async Process Scheduler supporting priority queues
    and concurrent task execution.
    """

    def __init__(
        self,
        task_executor_func=None,
        concurrency: Optional[int] = None
    ) -> None:
        self.concurrency = concurrency or settings.SCHEDULER_CONCURRENCY
        self.task_executor_func = task_executor_func
        self._processes: Dict[str, AgentProcess] = {}
        self._queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self._workers: List[asyncio.Task] = []
        self._start_time = time.time()
        self._is_running = False
        self._completed_count = 0
        self._failed_count = 0
        self._lock = asyncio.Lock()

    async def start(self) -> None:
        """Starts worker pool loop tasks."""
        if self._is_running:
            return
        self._is_running = True
        for i in range(self.concurrency):
            worker = asyncio.create_task(self._worker_loop(i))
            self._workers.append(worker)
        logger.info("Process scheduler kernel started", concurrency=self.concurrency)

    async def stop(self) -> None:
        """Gracefully shuts down worker tasks."""
        self._is_running = False
        for worker in self._workers:
            worker.cancel()
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()
        logger.info("Process scheduler kernel stopped")

    async def submit_process(self, process: AgentProcess) -> str:
        """Submits an agent process into priority queue."""
        async with self._lock:
            self._processes[process.process_id] = process
            process.update_status(ProcessStatus.QUEUED)

        # Numerical priority value (0 is highest)
        priority_val = int(process.task_context.priority)
        await self._queue.put((priority_val, time.time(), process.process_id))

        logger.info("Process submitted to queue", process_id=process.process_id, priority=priority_val)
        return process.process_id

    async def get_process(self, process_id: str) -> Optional[AgentProcess]:
        """Retrieves process state."""
        return self._processes.get(process_id)

    async def cancel_process(self, process_id: str) -> bool:
        """Cancels a pending or running process."""
        proc = self._processes.get(process_id)
        if not proc:
            return False

        proc.update_status(ProcessStatus.CANCELLED)
        logger.info("Process cancelled", process_id=process_id)
        return True

    async def list_processes(self) -> List[AgentProcess]:
        """Returns all registered agent processes."""
        return list(self._processes.values())

    async def get_metrics(self) -> KernelMetrics:
        """Returns real-time kernel metrics."""
        total = len(self._processes)
        active = sum(1 for p in self._processes.values() if p.status in (ProcessStatus.QUEUED, ProcessStatus.RUNNING))

        return KernelMetrics(
            total_processes=total,
            active_processes=active,
            completed_tasks=self._completed_count,
            failed_tasks=self._failed_count,
            uptime_seconds=round(time.time() - self._start_time, 2)
        )

    async def _worker_loop(self, worker_id: int) -> None:
        """Background queue consumer loop."""
        while self._is_running:
            try:
                priority, ts, process_id = await self._queue.get()
                proc = self._processes.get(process_id)

                if not proc or proc.status == ProcessStatus.CANCELLED:
                    self._queue.task_done()
                    continue

                proc.update_status(ProcessStatus.RUNNING)
                logger.info("Worker started executing process", worker_id=worker_id, process_id=process_id)

                if self.task_executor_func:
                    try:
                        await self.task_executor_func(proc)
                        self._completed_count += 1
                    except Exception as e:
                        logger.error("Process execution error", process_id=process_id, error=str(e))
                        proc.update_status(ProcessStatus.FAILED)
                        self._failed_count += 1
                else:
                    # Default execution simulation when executor not set directly
                    await asyncio.sleep(0.1)
                    proc.task_context.result = "Completed default execution."
                    proc.update_status(ProcessStatus.COMPLETED)
                    self._completed_count += 1

                self._queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Worker loop exception", worker_id=worker_id, error=str(e))
                await asyncio.sleep(0.5)
