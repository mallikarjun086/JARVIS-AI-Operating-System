"""
SQLAlchemy Persistent Repositories for Agent Processes and Tasks.
Implements TaskRepositoryPort using async SQLAlchemy queries.
"""

from datetime import datetime
import json
from typing import List, Optional
from sqlalchemy import Column, DateTime, String, Text, select
from sqlalchemy.ext.asyncio import AsyncSession
from jarvis.domain.entities import AgentProcess, TaskContext
from jarvis.domain.ports import TaskRepositoryPort
from jarvis.domain.value_objects import ProcessStatus, TaskPriority, ToolPermission
from jarvis.infrastructure.persistence.database import Base


class ProcessRecordModel(Base):
    """SQLAlchemy ORM Entity for persistent agent process table."""
    __tablename__ = "agent_processes"

    process_id = Column(String, primary_key=True)
    agent_name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    status = Column(String, nullable=False)
    goal = Column(Text, nullable=False)
    priority = Column(String, nullable=False)
    max_steps = Column(String, nullable=False)
    current_step = Column(String, nullable=False)
    history_json = Column(Text, nullable=False, default="[]")
    result = Column(Text, nullable=True)
    permissions_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class SQLAlchemyTaskRepository(TaskRepositoryPort):
    """Async database repository implementing TaskRepositoryPort."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save_process(self, process: AgentProcess) -> None:
        """Saves or updates process state in database."""
        model = await self.session.get(ProcessRecordModel, process.process_id)
        if not model:
            model = ProcessRecordModel(process_id=process.process_id)
            self.session.add(model)

        model.agent_name = process.agent_name
        model.role = process.role
        model.status = process.status.value
        model.goal = process.task_context.goal
        model.priority = str(int(process.task_context.priority))
        model.max_steps = str(process.task_context.max_steps)
        model.current_step = str(process.task_context.current_step)
        model.history_json = json.dumps(process.task_context.history)
        model.result = process.task_context.result
        model.permissions_json = json.dumps([p.value for p in process.permissions])
        model.created_at = process.created_at
        model.completed_at = process.completed_at

        await self.session.commit()

    async def get_process(self, process_id: str) -> Optional[AgentProcess]:
        """Retrieves process by process ID."""
        model = await self.session.get(ProcessRecordModel, process_id)
        if not model:
            return None
        return self._to_entity(model)

    async def list_processes(self) -> List[AgentProcess]:
        """Lists all stored processes."""
        stmt = select(ProcessRecordModel)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    def _to_entity(self, model: ProcessRecordModel) -> AgentProcess:
        """Converts database ORM model to domain AgentProcess entity."""
        history = json.loads(model.history_json) if model.history_json else []
        permissions_raw = json.loads(model.permissions_json) if model.permissions_json else []

        task_ctx = TaskContext(
            goal=model.goal,
            priority=TaskPriority(int(model.priority)),
            status=ProcessStatus(model.status),
            max_steps=int(model.max_steps),
            current_step=int(model.current_step),
            history=history,
            result=model.result
        )

        return AgentProcess(
            process_id=model.process_id,
            agent_name=model.agent_name,
            role=model.role,
            status=ProcessStatus(model.status),
            task_context=task_ctx,
            permissions=[ToolPermission(p) for p in permissions_raw],
            created_at=model.created_at,
            completed_at=model.completed_at
        )
