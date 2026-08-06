"""
Domain Ports (Abstract Interfaces and Protocols) for JARVIS AI Operating System.
Ensures Hexagonal Architecture decoupling of domain logic from infrastructure implementations.
"""

from typing import Any, Callable, Dict, List, Optional, Protocol, runtime_checkable
from jarvis.domain.entities import AgentProcess, KernelMetrics, MemoryRecord, ToolDefinition, ToolResult
from jarvis.domain.value_objects import ToolPermission


@runtime_checkable
class LLMProviderPort(Protocol):
    """Abstract port for multi-provider LLM gateways."""

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        tools: Optional[List[ToolDefinition]] = None,
        temperature: float = 0.2
    ) -> Dict[str, Any]:
        """Generates text or tool-call response from LLM."""
        ...

    async def generate_embedding(self, text: str) -> List[float]:
        """Generates vector embedding for input text."""
        ...


@runtime_checkable
class VectorStorePort(Protocol):
    """Abstract port for vector memory indexing and retrieval."""

    async def add_memory(self, record: MemoryRecord) -> None:
        """Stores a memory record with vector index."""
        ...

    async def search_memory(
        self,
        query: str,
        top_k: int = 5,
        min_similarity: float = 0.5
    ) -> List[MemoryRecord]:
        """Retrieves top-k relevant memory records by semantic vector similarity."""
        ...

    async def delete_memory(self, memory_id: str) -> bool:
        """Deletes memory record by ID."""
        ...


@runtime_checkable
class ProcessSchedulerPort(Protocol):
    """Abstract port for process scheduling kernel."""

    async def submit_process(self, process: AgentProcess) -> str:
        """Submits an agent process into priority queue for execution."""
        ...

    async def get_process(self, process_id: str) -> Optional[AgentProcess]:
        """Retrieves process state by process ID."""
        ...

    async def cancel_process(self, process_id: str) -> bool:
        """Cancels a pending or running process."""
        ...

    async def list_processes(self) -> List[AgentProcess]:
        """Lists all registered agent processes."""
        ...

    async def get_metrics(self) -> KernelMetrics:
        """Returns real-time kernel execution metrics."""
        ...


@runtime_checkable
class ToolRegistryPort(Protocol):
    """Abstract port for tool discovery and execution engine."""

    def register_tool(
        self,
        definition: ToolDefinition,
        executor: Callable[..., Any]
    ) -> None:
        """Registers a executable tool function with permission metadata."""
        ...

    def list_tools(self) -> List[ToolDefinition]:
        """Lists all registered tool definitions."""
        ...

    async def execute_tool(
        self,
        name: str,
        params: Dict[str, Any],
        caller_permissions: List[ToolPermission]
    ) -> ToolResult:
        """Executes tool after validating parameter schemas and permissions."""
        ...


@runtime_checkable
class SecuritySandboxPort(Protocol):
    """Abstract port for security isolation sandbox."""

    def validate_path(self, target_path: str) -> bool:
        """Validates that path resides within safe workspace root."""
        ...

    def validate_command(self, command: str) -> bool:
        """Validates that shell command is whitelisted and non-destructive."""
        ...


@runtime_checkable
class TaskRepositoryPort(Protocol):
    """Abstract port for persistent process database storage."""

    async def save_process(self, process: AgentProcess) -> None:
        """Persists agent process record to database."""
        ...

    async def get_process(self, process_id: str) -> Optional[AgentProcess]:
        """Fetches agent process record from database."""
        ...

    async def list_processes(self) -> List[AgentProcess]:
        """Lists all stored process records."""
        ...
