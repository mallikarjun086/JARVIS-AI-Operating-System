"""
Tool Factory Engine — Life Cycle, Caching, Dependency Injection & Singleton Management.
"""

from typing import Any, Dict, Optional, Type
import structlog
from app.tools.base import BaseTool
from app.tools.registry import tool_registry

logger = structlog.get_logger(__name__)


class ToolFactory:
    """
    Factory creating and initializing tool instances with dependency injection,
    caching, and lifecycle hooks.
    """

    def __init__(self) -> None:
        self._instances: Dict[str, BaseTool] = {}
        self._initialized: Dict[str, bool] = {}

    async def get_or_create(self, tool_name: str) -> Optional[BaseTool]:
        """
        Retrieves cached tool instance or creates and initializes a new one.
        """
        if tool_name in self._instances and self._initialized.get(tool_name):
            return self._instances[tool_name]

        tool = tool_registry.get_tool(tool_name)
        if not tool:
            return None

        # Initialize lifecycle hook
        try:
            await tool.initialize()
            self._instances[tool_name] = tool
            self._initialized[tool_name] = True
            logger.info("Initialized tool instance via ToolFactory", tool=tool_name)
        except Exception as e:
            logger.error("Tool initialization failed in ToolFactory", tool=tool_name, error=str(e))
            return None

        return tool

    async def shutdown_all(self) -> None:
        """Invokes shutdown() on all cached tool instances."""
        for name, tool in self._instances.items():
            try:
                await tool.shutdown()
                self._initialized[name] = False
            except Exception as e:
                logger.warning("Tool shutdown error", tool=name, error=str(e))
        self._instances.clear()


tool_factory = ToolFactory()
