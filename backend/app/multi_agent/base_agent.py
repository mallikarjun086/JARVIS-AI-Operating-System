"""
Abstract BaseAgent Framework for Enterprise Multi-Agent Platform (Sprint 9 Step 2).
Every specialized agent must inherit from BaseAgent and implement all standard lifecycle and capability methods.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import structlog

from app.multi_agent.schemas import AgentMetadata, AgentRole, SharedContextPayload, SubTaskSpec

logger = structlog.get_logger(__name__)


class BaseAgent(ABC):
    """Abstract Base Class for all specialized agents in the JARVIS AI OS platform."""

    def __init__(self, metadata: AgentMetadata) -> None:
        self.metadata = metadata
        self.completed_count: int = 0
        self.failed_count: int = 0
        self.total_latency_ms: float = 0.0
        self._is_initialized: bool = False

    @abstractmethod
    async def initialize(self) -> None:
        """Initializes agent resources and tools."""
        self._is_initialized = True
        logger.info("Agent initialized", agent_id=self.metadata.agent_id, role=self.metadata.role.value)

    @abstractmethod
    async def shutdown(self) -> None:
        """Gracefully releases agent resources."""
        self._is_initialized = False
        logger.info("Agent shutdown completed", agent_id=self.metadata.agent_id)

    @abstractmethod
    async def plan(self, goal: str, context: SharedContextPayload) -> List[SubTaskSpec]:
        """Decomposes goal into specialized subtasks."""
        pass

    @abstractmethod
    async def execute(self, subtask: SubTaskSpec, context: SharedContextPayload) -> SubTaskSpec:
        """Executes assigned subtask strictly through Tool Framework."""
        pass

    async def execute_task(self, subtask: SubTaskSpec, context: Optional[SharedContextPayload] = None) -> SubTaskSpec:
        """Helper alias executing assigned subtask with context."""
        from app.multi_agent.context import shared_context_builder
        ctx = context or shared_context_builder.build_context()
        res = await self.execute(subtask, ctx)
        return res or subtask


    @abstractmethod
    async def verify(self, subtask: SubTaskSpec) -> bool:
        """Verifies subtask execution result against acceptance criteria."""
        pass

    @abstractmethod
    async def rollback(self, subtask: SubTaskSpec) -> bool:
        """Rolls back subtask execution state if verification fails."""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Returns live agent diagnostic health state."""
        return {
            "agent_id": self.metadata.agent_id,
            "role": self.metadata.role.value,
            "status": self.metadata.status.value,
            "initialized": self._is_initialized,
            "completed_count": self.completed_count,
            "failed_count": self.failed_count
        }

    def get_capabilities(self) -> List[str]:
        """Returns list of capabilities exposed by agent."""
        return self.metadata.capabilities

    def estimate_cost(self, subtask: SubTaskSpec) -> float:
        """Estimates financial cost ($) for subtask execution."""
        return self.metadata.estimated_cost_per_task

    def estimate_runtime(self, subtask: SubTaskSpec) -> float:
        """Estimates latency (ms) for subtask execution."""
        return self.metadata.estimated_latency_ms

    def supported_tools(self) -> List[str]:
        """Returns list of supported tool names."""
        return self.metadata.supported_tools

    def supported_languages(self) -> List[str]:
        """Returns supported programming languages."""
        return self.metadata.supported_languages

    def supported_frameworks(self) -> List[str]:
        """Returns supported frameworks."""
        return self.metadata.supported_frameworks
