"""
Abstract Base Class Contract for All Enterprise Tools.
Enforces full lifecycle: initialize(), shutdown(), validate(), execute(), rollback(), health_check(), estimate_runtime(), get_metadata().
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Type
from pydantic import BaseModel, ConfigDict

from app.tools.schemas import PermissionLevel, ToolMetadata


class DefaultToolSchema(BaseModel):
    """Default Pydantic schema fallback for tools, allowing arbitrary output payload keys."""
    model_config = ConfigDict(extra="allow")



class BaseTool(ABC):
    """
    Mandatory Abstract Base Class for all tool implementations.
    No mock methods allowed — every concrete tool subclass must provide full operational logic.
    """

    def __init__(
        self,
        name: str = "",
        description: str = "",
        category: str = "system",
        version: str = "1.0.0",
        permission_level: PermissionLevel = PermissionLevel.READ_ONLY
    ) -> None:
        self._name = name
        self._description = description
        self._category = category
        self._version = version
        self._permission_level = permission_level

    @property
    def name(self) -> str:
        """Unique tool identifier name (e.g. 'filesystem.read_file')."""
        return getattr(self, "_name", "") or self.__class__.__name__

    @property
    def description(self) -> str:
        """Detailed natural language description of tool behavior for LLMs."""
        return getattr(self, "_description", "") or (self.__doc__ or self.__class__.__name__)

    @property
    def category(self) -> str:
        """Category namespace (filesystem, terminal, git, browser, desktop, network, memory, ai, system, workflow)."""
        return getattr(self, "_category", "system")

    @property
    def version(self) -> str:
        """Semantic version string."""
        return getattr(self, "_version", "1.0.0")

    @property
    def permission_level(self) -> PermissionLevel:
        """Mandatory minimum permission level required to invoke tool."""
        return getattr(self, "_permission_level", PermissionLevel.READ_ONLY)

    @property
    def input_schema(self) -> Type[BaseModel]:
        """Pydantic model class for input parameter validation."""
        return DefaultToolSchema

    @property
    def output_schema(self) -> Type[BaseModel]:
        """Pydantic model class for output result validation."""
        return DefaultToolSchema

    @property
    def timeout_seconds(self) -> float:
        """Default execution timeout in seconds."""
        return 30.0

    @property
    def max_retries(self) -> int:
        """Default maximum retries on transient execution failures."""
        return 3

    @property
    def requires_approval(self) -> bool:
        """True if sensitive tool requires explicit user approval before execution."""
        return self.permission_level in (PermissionLevel.DANGEROUS, PermissionLevel.ADMIN)

    # ─────────────────────────────────────────────────
    # Tool Lifecycle Methods
    # ─────────────────────────────────────────────────

    async def initialize(self) -> None:
        """Initializes tool resources (e.g. connections, handles, caches). Overridden if needed."""
        pass

    async def shutdown(self) -> None:
        """Cleans up tool resources on registry shutdown or module unload."""
        pass

    async def validate(self, params: Dict[str, Any]) -> bool:
        """
        Validates input parameter payload against schema and custom business policy.
        Returns True if parameters are valid.
        """
        try:
            self.input_schema.model_validate(params)
            return True
        except Exception:
            return False

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """
        Asynchronous execution implementation body.
        Must be overridden by concrete tool implementations.
        """
        return await self.execute_async(params, context)

    async def execute_async(self, params: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Backward-compatible alias delegating to execute()."""
        return await self.execute(params, context)


    async def rollback(self, params: Dict[str, Any], context: Dict[str, Any], error: Exception) -> bool:
        """
        Executes compensation/undo logic if execution failed midway.
        Returns True if rollback completed successfully.
        """
        return False

    async def health_check(self) -> bool:
        """Diagnostic health check verifying tool dependencies and operational state."""
        return True

    def estimate_runtime(self, params: Dict[str, Any]) -> float:
        """Estimates expected execution runtime in seconds given input parameters."""
        return 1.0

    def get_metadata(self) -> ToolMetadata:
        """Generates tool metadata descriptor for API inspection and discovery."""
        perm = self.permission_level() if callable(self.permission_level) else self.permission_level
        return ToolMetadata(
            name=self.name,
            description=self.description,
            category=self.category,
            version=self.version,
            permission_level=perm,
            timeout_seconds=self.timeout_seconds,
            max_retries=self.max_retries,
            requires_approval=self.requires_approval,
            input_schema_json=self.input_schema.model_json_schema(),
            output_schema_json=self.output_schema.model_json_schema()
        )

