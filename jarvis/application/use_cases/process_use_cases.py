"""
Application Use Cases for Agent Process Management.
"""

from typing import List, Optional
from jarvis.application.dto import CreateProcessRequest, ProcessResponse
from jarvis.domain.entities import AgentProcess, TaskContext
from jarvis.domain.exceptions import ProcessNotFoundError
from jarvis.domain.ports import ProcessSchedulerPort, TaskRepositoryPort
from jarvis.domain.value_objects import ProcessStatus


class CreateAgentProcessUseCase:
    """Use case to create and schedule a new agent process."""

    def __init__(
        self,
        scheduler: ProcessSchedulerPort,
        repository: Optional[TaskRepositoryPort] = None
    ) -> None:
        self.scheduler = scheduler
        self.repository = repository

    async def execute(self, request: CreateProcessRequest) -> ProcessResponse:
        task_ctx = TaskContext(
            goal=request.goal,
            priority=request.priority,
            max_steps=request.max_steps
        )
        process = AgentProcess(
            agent_name=request.agent_name,
            role=request.role,
            status=ProcessStatus.CREATED,
            task_context=task_ctx,
            permissions=request.permissions
        )

        process_id = await self.scheduler.submit_process(process)

        if self.repository:
            await self.repository.save_process(process)

        return ProcessResponse(
            process_id=process_id,
            agent_name=process.agent_name,
            role=process.role,
            status=process.status,
            goal=process.task_context.goal,
            priority=process.task_context.priority,
            current_step=process.task_context.current_step,
            max_steps=process.task_context.max_steps,
            history=process.task_context.history,
            result=process.task_context.result,
            created_at=process.created_at,
            completed_at=process.completed_at
        )


class GetAgentProcessUseCase:
    """Use case to retrieve process state."""

    def __init__(
        self,
        scheduler: ProcessSchedulerPort,
        repository: Optional[TaskRepositoryPort] = None
    ) -> None:
        self.scheduler = scheduler
        self.repository = repository

    async def execute(self, process_id: str) -> ProcessResponse:
        process = await self.scheduler.get_process(process_id)
        if not process and self.repository:
            process = await self.repository.get_process(process_id)

        if not process:
            raise ProcessNotFoundError(process_id)

        return ProcessResponse(
            process_id=process.process_id,
            agent_name=process.agent_name,
            role=process.role,
            status=process.status,
            goal=process.task_context.goal,
            priority=process.task_context.priority,
            current_step=process.task_context.current_step,
            max_steps=process.task_context.max_steps,
            history=process.task_context.history,
            result=process.task_context.result,
            created_at=process.created_at,
            completed_at=process.completed_at
        )


class ListAgentProcessesUseCase:
    """Use case to list all registered processes."""

    def __init__(self, scheduler: ProcessSchedulerPort) -> None:
        self.scheduler = scheduler

    async def execute(self) -> List[ProcessResponse]:
        processes = await self.scheduler.list_processes()
        return [
            ProcessResponse(
                process_id=proc.process_id,
                agent_name=proc.agent_name,
                role=proc.role,
                status=proc.status,
                goal=proc.task_context.goal,
                priority=proc.task_context.priority,
                current_step=proc.task_context.current_step,
                max_steps=proc.task_context.max_steps,
                history=proc.task_context.history,
                result=proc.task_context.result,
                created_at=proc.created_at,
                completed_at=proc.completed_at
            )
            for proc in processes
        ]


class CancelAgentProcessUseCase:
    """Use case to terminate an active process."""

    def __init__(self, scheduler: ProcessSchedulerPort) -> None:
        self.scheduler = scheduler

    async def execute(self, process_id: str) -> bool:
        cancelled = await self.scheduler.cancel_process(process_id)
        if not cancelled:
            raise ProcessNotFoundError(process_id)
        return True
