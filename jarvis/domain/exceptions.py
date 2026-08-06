"""
Domain-Specific Exception Hierarchy for JARVIS AI Operating System.
Provides clean error semantics across all layers.
"""

class JARVISError(Exception):
    """Base exception class for all JARVIS system errors."""
    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ProcessNotFoundError(JARVISError):
    """Raised when an agent process ID is not found in kernel registry or DB."""
    def __init__(self, process_id: str) -> None:
        super().__init__(f"Agent process '{process_id}' was not found in kernel registry.", {"process_id": process_id})


class TaskExecutionError(JARVISError):
    """Raised when a task fails during execution phase."""
    def __init__(self, task_id: str, reason: str) -> None:
        super().__init__(f"Execution failed for task '{task_id}': {reason}", {"task_id": task_id, "reason": reason})


class SecurityViolationError(JARVISError):
    """Raised when an action violates security sandbox or path boundaries."""
    def __init__(self, operation: str, path_or_command: str) -> None:
        super().__init__(
            f"Security violation during '{operation}': Operation on '{path_or_command}' denied by security policy.",
            {"operation": operation, "target": path_or_command}
        )


class LLMProviderError(JARVISError):
    """Raised when external LLM gateway or provider encounters unrecoverable failure."""
    def __init__(self, provider: str, error_msg: str) -> None:
        super().__init__(f"LLM Provider '{provider}' error: {error_msg}", {"provider": provider, "error": error_msg})


class VectorStoreError(JARVISError):
    """Raised when vector embedding or similarity search operations fail."""
    def __init__(self, message: str) -> None:
        super().__init__(f"Vector memory store error: {message}")


class ToolExecutionError(JARVISError):
    """Raised when a registered system tool fails execution."""
    def __init__(self, tool_name: str, error_msg: str) -> None:
        super().__init__(f"Tool '{tool_name}' execution error: {error_msg}", {"tool_name": tool_name, "error": error_msg})


class QuotaExceededError(JARVISError):
    """Raised when resource limits (tokens, concurrent processes, execution timeout) are exceeded."""
    def __init__(self, resource: str, limit: int | float, current: int | float) -> None:
        super().__init__(
            f"Resource quota exceeded for '{resource}': limit={limit}, current={current}",
            {"resource": resource, "limit": limit, "current": current}
        )
