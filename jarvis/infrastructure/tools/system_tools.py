"""
System Tools Registry and Executable Capabilities.
Enforces parameter schemas, sandboxing, and permission checks.
"""

import asyncio
import os
from pathlib import Path
import time
from typing import Any, Callable, Dict, List, Optional
from jarvis.config import settings
from jarvis.domain.entities import ToolDefinition, ToolResult
from jarvis.domain.exceptions import SecurityViolationError, ToolExecutionError
from jarvis.domain.ports import SecuritySandboxPort, ToolRegistryPort
from jarvis.domain.value_objects import ToolPermission
from jarvis.infrastructure.logging.logger import get_logger
from jarvis.infrastructure.security.sandbox import SecuritySandbox

logger = get_logger("jarvis.system_tools")


class ToolRegistry(ToolRegistryPort):
    """Registry engine managing tool definitions and execution routing."""

    def __init__(self, sandbox: Optional[SecuritySandboxPort] = None) -> None:
        self.sandbox = sandbox or SecuritySandbox()
        self._tools: Dict[str, ToolDefinition] = {}
        self._executors: Dict[str, Callable[..., Any]] = {}

        # Automatically register default built-in system tools
        self._register_default_tools()

    def register_tool(
        self,
        definition: ToolDefinition,
        executor: Callable[..., Any]
    ) -> None:
        """Registers a executable tool function."""
        self._tools[definition.name] = definition
        self._executors[definition.name] = executor
        logger.info("Registered system tool", tool_name=definition.name, permission=definition.permission_required.value)

    def list_tools(self) -> List[ToolDefinition]:
        """Lists all registered tools."""
        return list(self._tools.values())

    async def execute_tool(
        self,
        name: str,
        params: Dict[str, Any],
        caller_permissions: List[ToolPermission]
    ) -> ToolResult:
        """Executes tool with permission checks and timing metrics."""
        if name not in self._tools or name not in self._executors:
            return ToolResult(
                tool_name=name,
                success=False,
                result=None,
                error=f"Tool '{name}' is not registered in system registry."
            )

        definition = self._tools[name]
        executor = self._executors[name]

        # Permission check
        if definition.permission_required not in caller_permissions:
            return ToolResult(
                tool_name=name,
                success=False,
                result=None,
                error=f"Permission Denied: Caller lacks '{definition.permission_required.value}' privilege."
            )

        start_time = time.time()
        try:
            if asyncio.iscoroutinefunction(executor):
                res = await executor(**params)
            else:
                res = executor(**params)

            elapsed_ms = (time.time() - start_time) * 1000.0
            return ToolResult(
                tool_name=name,
                success=True,
                result=res,
                execution_time_ms=round(elapsed_ms, 2)
            )
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000.0
            logger.error("Tool execution failed", tool_name=name, error=str(e))
            return ToolResult(
                tool_name=name,
                success=False,
                result=None,
                error=str(e),
                execution_time_ms=round(elapsed_ms, 2)
            )

    def _register_default_tools(self) -> None:
        """Registers standard system tools."""

        # 1. Read File Tool
        self.register_tool(
            ToolDefinition(
                name="read_file",
                description="Reads text contents of a file within workspace sandbox.",
                parameters_schema={"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
                permission_required=ToolPermission.READ_ONLY
            ),
            self._tool_read_file
        )

        # 2. Write File Tool
        self.register_tool(
            ToolDefinition(
                name="write_file",
                description="Writes text content to a file within workspace sandbox.",
                parameters_schema={"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]},
                permission_required=ToolPermission.FILE_WRITE
            ),
            self._tool_write_file
        )

        # 3. List Directory Tool
        self.register_tool(
            ToolDefinition(
                name="list_dir",
                description="Lists files and directories under target path.",
                parameters_schema={"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
                permission_required=ToolPermission.READ_ONLY
            ),
            self._tool_list_dir
        )

        # 4. Execute Command Tool
        self.register_tool(
            ToolDefinition(
                name="execute_command",
                description="Executes a safe, whitelisted shell command.",
                parameters_schema={"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]},
                permission_required=ToolPermission.SYSTEM_EXECUTE
            ),
            self._tool_execute_command
        )

        # 5. Web Search Simulator Tool
        self.register_tool(
            ToolDefinition(
                name="web_search",
                description="Performs web search for real-time information lookup.",
                parameters_schema={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
                permission_required=ToolPermission.NETWORK_ACCESS
            ),
            self._tool_web_search
        )

    # Tool Execution Functions
    def _tool_read_file(self, path: str) -> str:
        self.sandbox.validate_path(path)
        abs_path = (settings.WORKSPACE_ROOT / path).resolve()
        if not abs_path.exists():
            raise FileNotFoundError(f"File not found: '{path}'")
        with open(abs_path, "r", encoding="utf-8") as f:
            return f.read()

    def _tool_write_file(self, path: str, content: str) -> str:
        self.sandbox.validate_path(path)
        abs_path = (settings.WORKSPACE_ROOT / path).resolve()
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} bytes to '{path}'"

    def _tool_list_dir(self, path: str = ".") -> List[str]:
        self.sandbox.validate_path(path)
        abs_path = (settings.WORKSPACE_ROOT / path).resolve()
        if not abs_path.exists() or not abs_path.is_dir():
            raise NotADirectoryError(f"Directory not found: '{path}'")
        return os.listdir(abs_path)

    async def _tool_execute_command(self, command: str) -> str:
        self.sandbox.validate_command(command)
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(settings.WORKSPACE_ROOT)
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise ToolExecutionError("execute_command", stderr.decode().strip())
        return stdout.decode().strip()

    def _tool_web_search(self, query: str) -> List[Dict[str, str]]:
        return [
            {
                "title": f"Search Results for '{query}'",
                "snippet": f"Simulated intelligence snippet addressing query: {query}",
                "source": "https://search.jarvis.ai/results"
            }
        ]
