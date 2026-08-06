"""
Application Use Cases for Tool Execution and Registration.
"""

from typing import List
from jarvis.application.dto import ExecuteToolRequest
from jarvis.domain.entities import ToolDefinition, ToolResult
from jarvis.domain.ports import ToolRegistryPort
from jarvis.domain.value_objects import ToolPermission


class ListToolsUseCase:
    """Use case to list registered executable capabilities."""

    def __init__(self, tool_registry: ToolRegistryPort) -> None:
        self.tool_registry = tool_registry

    def execute(self) -> List[ToolDefinition]:
        return self.tool_registry.list_tools()


class ExecuteToolUseCase:
    """Use case to execute a system tool directly with privilege checking."""

    def __init__(self, tool_registry: ToolRegistryPort) -> None:
        self.tool_registry = tool_registry

    async def execute(
        self,
        request: ExecuteToolRequest,
        permissions: List[ToolPermission] | None = None
    ) -> ToolResult:
        user_permissions = permissions or [
            ToolPermission.READ_ONLY,
            ToolPermission.FILE_WRITE,
            ToolPermission.SYSTEM_EXECUTE,
            ToolPermission.NETWORK_ACCESS
        ]
        return await self.tool_registry.execute_tool(
            name=request.tool_name,
            params=request.parameters,
            caller_permissions=user_permissions
        )
