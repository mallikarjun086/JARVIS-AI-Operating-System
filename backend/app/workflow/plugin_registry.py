"""
Dynamic Plugin Step System for Extensible Workflow Nodes (Sprint 10).
Workflow nodes are non-hardcoded plugins inheriting from BaseStepPlugin.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import structlog

from app.workflow.execution_backend import ExecutionBackend, local_execution_backend

logger = structlog.get_logger(__name__)


class BaseStepPlugin(ABC):
    """Abstract base class for extensible workflow step plugins."""

    def __init__(self, plugin_name: str, capability_required: str) -> None:
        self.plugin_name = plugin_name
        self.capability_required = capability_required

    @abstractmethod
    async def execute_step(
        self,
        step_name: str,
        parameters: Dict[str, Any],
        backend: ExecutionBackend
    ) -> Dict[str, Any]:
        """Executes plugin step using ExecutionBackend."""
        pass


class GenericPluginStep(BaseStepPlugin):
    """Generic plugin step forwarding goal to ExecutionBackend."""

    async def execute_step(
        self,
        step_name: str,
        parameters: Dict[str, Any],
        backend: ExecutionBackend
    ) -> Dict[str, Any]:
        goal = parameters.get("goal") or f"Execute plugin step '{step_name}' ({self.plugin_name})"
        return await backend.dispatch_step_task(goal=goal, capability=self.capability_required, parameters=parameters)


class PluginStepRegistry:
    """Dynamic registry managing workflow step plugins."""

    def __init__(self) -> None:
        self._plugins: Dict[str, BaseStepPlugin] = {}
        self._register_default_plugins()

    def _register_default_plugins(self) -> None:
        """Registers default 10 enterprise plugins."""
        self.register_plugin(GenericPluginStep("ApprovalNode", "quality_verification"))
        self.register_plugin(GenericPluginStep("BrowserNode", "browser_automation"))
        self.register_plugin(GenericPluginStep("DesktopNode", "desktop_automation"))
        self.register_plugin(GenericPluginStep("GitNode", "code_refactoring"))
        self.register_plugin(GenericPluginStep("DockerNode", "general_processing"))
        self.register_plugin(GenericPluginStep("SlackNode", "general_processing"))
        self.register_plugin(GenericPluginStep("EmailNode", "general_processing"))
        self.register_plugin(GenericPluginStep("VisionNode", "ocr_text_extraction"))
        self.register_plugin(GenericPluginStep("VoiceNode", "speech_recognition"))
        self.register_plugin(GenericPluginStep("SWENode", "code_refactoring"))

    def register_plugin(self, plugin: BaseStepPlugin) -> None:
        """Registers custom step plugin dynamically."""
        self._plugins[plugin.plugin_name.lower()] = plugin
        logger.info("Registered workflow step plugin", plugin_name=plugin.plugin_name)

    def get_plugin(self, plugin_name: str) -> Optional[BaseStepPlugin]:
        """Retrieves plugin instance by name."""
        return self._plugins.get(plugin_name.lower())

    def list_plugins(self) -> List[str]:
        """Lists names of all registered plugins."""
        return list(self._plugins.keys())


plugin_step_registry = PluginStepRegistry()
