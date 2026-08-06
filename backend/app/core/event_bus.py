"""
Unified Asynchronous Event Bus Kernel (Sprint 15).
Connects Planner, Multi-Agent Swarm, Tool Framework, Memory Engine, Vision, Voice, and Security into a decoupled Event-Driven Architecture.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Coroutine, Dict, List, Set
import uuid
from pydantic import BaseModel, Field


class SystemEventType(str, Enum):
    PLANNER_TASK_STARTED = "PLANNER_TASK_STARTED"
    PLANNER_TASK_COMPLETED = "PLANNER_TASK_COMPLETED"
    AGENT_STATE_CHANGED = "AGENT_STATE_CHANGED"
    TOOL_EXECUTION_COMPLETED = "TOOL_EXECUTION_COMPLETED"
    MEMORY_STORED = "MEMORY_STORED"
    VISION_ANALYSIS_COMPLETED = "VISION_ANALYSIS_COMPLETED"
    SECURITY_ALERT_TRIGGERED = "SECURITY_ALERT_TRIGGERED"
    SYSTEM_HEALTH_CHECK = "SYSTEM_HEALTH_CHECK"


class SystemEvent(BaseModel):
    """Decoupled System Event Payload."""
    event_id: str = Field(default_factory=lambda: f"evt-{uuid.uuid4().hex[:8]}")
    event_type: SystemEventType | str
    source_subsystem: str = "system"
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, key, value)




EventHandler = Callable[[SystemEvent], Coroutine[Any, Any, None]]


class UnifiedEventBus:
    """Asynchronous Pub/Sub Event Bus for cross-subsystem messaging and event-driven orchestration."""

    def __init__(self) -> None:
        self._subscribers: Dict[SystemEventType, List[EventHandler]] = {}
        self._global_subscribers: List[EventHandler] = []
        self._event_history: List[SystemEvent] = []
        self._max_history: int = 500

    def subscribe(self, event_type: SystemEventType, handler: EventHandler) -> None:
        """Registers handler for specific event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    def subscribe_all(self, handler: EventHandler) -> None:
        """Registers global listener for all published system events."""
        self._global_subscribers.append(handler)

    async def publish(self, event: SystemEvent) -> None:
        """Publishes event to all registered listeners asynchronously."""
        # History logging
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)

        tasks = []
        # Type-specific handlers
        if event.event_type in self._subscribers:
            for handler in self._subscribers[event.event_type]:
                tasks.append(handler(event))

        # Global handlers
        for handler in self._global_subscribers:
            tasks.append(handler(event))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def get_event_history(self, limit: int = 50) -> List[SystemEvent]:
        """Returns recent event history."""
        return self._event_history[-limit:]

    def clear_history(self) -> None:
        """Clears event history log."""
        self._event_history.clear()


event_bus = UnifiedEventBus()
