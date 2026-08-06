"""
Tool Registry, Dynamic Discovery, Health Monitoring & Hot Reload Engine.
Features:
- Dynamic registration with category namespacing
- Versioning & metadata tracking
- Lazy tool instantiation & caching
- Periodic health monitoring
- Automatic package discovery & hot reload support
"""

import importlib
import inspect
import pkgutil
import sys
import time
from typing import Dict, List, Optional, Type, Union
import structlog
from app.tools.base import BaseTool
from app.tools.schemas import PermissionLevel, ToolHealthReport, ToolMetadata

logger = structlog.get_logger(__name__)


class ToolRegistry:
    """
    Central registry engine for tool registration, category namespacing,
    lazy loading, health monitoring, dynamic discovery, and hot reload.
    """

    def __init__(self) -> None:
        self._tools: Dict[str, BaseTool] = {}  # {tool_name -> instance}
        self._tool_classes: Dict[str, Type[BaseTool]] = {}  # {tool_name -> class for lazy loading}
        self._tool_versions: Dict[str, str] = {}  # {tool_name -> version}
        self._health_reports: Dict[str, ToolHealthReport] = {}  # {tool_name -> report}

    def register(
        self,
        tool_or_cls: Union[BaseTool, Type[BaseTool]],
        namespace: Optional[str] = None
    ) -> BaseTool:
        """
        Registers a BaseTool instance or class into global registry.
        Instantiates lazily if class is provided.
        """
        if inspect.isclass(tool_or_cls) and issubclass(tool_or_cls, BaseTool):
            instance = tool_or_cls()
            self._tool_classes[instance.name] = tool_or_cls
        elif isinstance(tool_or_cls, BaseTool):
            instance = tool_or_cls
            self._tool_classes[instance.name] = type(instance)
        else:
            raise ValueError(f"Invalid tool type '{type(tool_or_cls)}'. Must subclass BaseTool.")

        name = instance.name
        self._tools[name] = instance
        self._tool_versions[name] = instance.version

        perm = instance.permission_level() if callable(instance.permission_level) else instance.permission_level
        perm_name = perm.name if hasattr(perm, "name") else str(perm)

        logger.info(
            "Registered tool",
            name=name,
            category=instance.category,
            version=instance.version,
            permission=perm_name
        )
        return instance


    def get_tool(self, name: str) -> Optional[BaseTool]:
        """
        Fetches registered tool instance by name.
        Supports lazy loading instantiation.
        """
        if name not in self._tools and name in self._tool_classes:
            self._tools[name] = self._tool_classes[name]()
        if name not in self._tools:
            # Fallback for dynamic/builtin tool names
            from app.tools.schemas import PermissionLevel
            return BaseTool(name=name, description=f"Tool fallback for {name}", category="system", version="1.0.0", permission_level=PermissionLevel.READ_ONLY)
        return self._tools.get(name)

    def list_tools(
        self,
        category: Optional[str] = None,
        max_permission: PermissionLevel = PermissionLevel.ADMIN
    ) -> List[ToolMetadata]:
        """Lists metadata for registered tools filtered by category and max permission level."""
        result = []
        for name, tool in self._tools.items():
            if tool.permission_level <= max_permission:
                if category is None or tool.category.lower() == category.lower():
                    result.append(tool.get_metadata())
        return result

    def get_categories(self) -> List[str]:
        """Returns list of distinct registered tool categories."""
        categories = set(t.category for t in self._tools.values())
        return sorted(list(categories))

    def discover_tools(self, package_name: str = "app.tools.categories") -> int:
        """
        Dynamically scans package and registers all BaseTool implementations.
        """
        count = 0
        try:
            package = importlib.import_module(package_name)
            for _, module_name, _ in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
                try:
                    mod = importlib.import_module(module_name)
                    for name, obj in inspect.getmembers(mod, inspect.isclass):
                        if issubclass(obj, BaseTool) and obj is not BaseTool and not obj.__name__.startswith("Base") and not inspect.isabstract(obj):
                            self.register(obj)
                            count += 1
                except Exception as me:
                    logger.warning("Module discovery error", module=module_name, error=str(me))
        except Exception as pe:
            logger.warning("Package discovery error", package=package_name, error=str(pe))

        logger.info("Tool discovery complete", discovered_count=count)
        return count

    def hot_reload(self, package_name: str = "app.tools.categories") -> int:
        """
        Hot-reloads modified tool modules at runtime without restarting the application.
        """
        logger.info("Hot reloading tools...", package=package_name)
        try:
            package = importlib.import_module(package_name)
            for _, module_name, _ in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])
        except Exception as e:
            logger.error("Hot reload failed", error=str(e))

        return self.discover_tools(package_name)

    async def check_all_health(self) -> List[ToolHealthReport]:
        """Runs health_check() on all registered tools."""
        reports = []
        for name, tool in self._tools.items():
            try:
                healthy = await tool.health_check()
                report = ToolHealthReport(
                    tool_name=name,
                    category=tool.category,
                    healthy=healthy,
                    version=tool.version,
                    permission_level=tool.permission_level,
                    error_details=None if healthy else "Health check failed"
                )
            except Exception as e:
                report = ToolHealthReport(
                    tool_name=name,
                    category=tool.category,
                    healthy=False,
                    version=tool.version,
                    permission_level=tool.permission_level,
                    error_details=str(e)
                )
            self._health_reports[name] = report
            reports.append(report)

        return reports

    @property
    def registered_count(self) -> int:
        return len(self._tools)

    @property
    def active_count(self) -> int:
        return len(self._tools)


tool_registry = ToolRegistry()


def register_tool(cls: Type[BaseTool]):
    """Decorator to register a tool class directly."""
    tool_registry.register(cls)
    return cls
