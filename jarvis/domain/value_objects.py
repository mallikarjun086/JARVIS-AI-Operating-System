"""
Domain Value Objects and Enums for JARVIS AI OS.
"""

from enum import Enum, IntEnum


class ProcessStatus(str, Enum):
    """Execution status lifecycle of an agent process."""
    CREATED = "CREATED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class TaskPriority(IntEnum):
    """
    Priority levels for agent task scheduling.
    Numerical values are ordered such that lower numbers indicate higher priority
    in PriorityQueue ordering.
    """
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


class ToolPermission(str, Enum):
    """Permission boundaries required for tool execution."""
    READ_ONLY = "READ_ONLY"
    FILE_WRITE = "FILE_WRITE"
    SYSTEM_EXECUTE = "SYSTEM_EXECUTE"
    NETWORK_ACCESS = "NETWORK_ACCESS"


class MemoryType(str, Enum):
    """Classification of memory entries in the AI OS storage subsystem."""
    WORKING = "WORKING"
    EPISODIC = "EPISODIC"
    SEMANTIC = "SEMANTIC"
    SYSTEM_PROMPT = "SYSTEM_PROMPT"
