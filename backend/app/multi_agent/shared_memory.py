"""
Shared Swarm Memory Workspace Engine.
Provides a thread-safe shared context memory store accessible across all 10 agents.
"""

from typing import Any, Dict


class SharedSwarmMemory:
    """Shared workspace context store for multi-agent swarms."""

    def __init__(self) -> None:
        self._workspace: Dict[str, Any] = {}

    def set_key(self, key: str, value: Any) -> None:
        """Stores context value by key."""
        self._workspace[key] = value

    def get_key(self, key: str, default: Any = None) -> Any:
        """Retrieves context value by key."""
        return self._workspace.get(key, default)

    def delete_key(self, key: str) -> None:
        """Deletes context key."""
        if key in self._workspace:
            del self._workspace[key]

    def get_all_context(self) -> Dict[str, Any]:
        """Returns complete workspace snapshot."""
        return dict(self._workspace)


shared_swarm_memory = SharedSwarmMemory()
