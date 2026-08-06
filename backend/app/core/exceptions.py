"""
Unified Exception Hierarchy for Enterprise AI Operating System (Sprint 7.5).
Categorizes system exceptions into Recoverable, Fatal, Security, Validation, Infrastructure, Tool, Planner, Browser, Desktop, and Memory exceptions.
"""

from typing import Any, Dict, Optional


class JARVISBaseException(Exception):
    """Base exception class for all JARVIS AI OS errors."""

    def __init__(
        self,
        message: str,
        error_code: str = "JARVIS_ERROR",
        details: Optional[Dict[str, Any]] = None,
        is_recoverable: bool = False
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.is_recoverable = is_recoverable

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
            "is_recoverable": self.is_recoverable
        }


class RecoverableJARVISException(JARVISBaseException):
    """Base exception for recoverable system errors (triggers retry or recovery ladder)."""

    def __init__(self, message: str, error_code: str = "RECOVERABLE_ERROR", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, error_code=error_code, details=details, is_recoverable=True)


class FatalJARVISException(JARVISBaseException):
    """Base exception for non-recoverable fatal system errors."""

    def __init__(self, message: str, error_code: str = "FATAL_ERROR", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, error_code=error_code, details=details, is_recoverable=False)


# Security Exceptions
class SecurityException(FatalJARVISException):
    """Raised on security policy violations, unauthorized access, or sandbox breaches."""
    def __init__(self, message: str, error_code: str = "SECURITY_VIOLATION", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, error_code=error_code, details=details)


# Validation Exceptions
class ValidationException(JARVISBaseException):
    """Raised on input schema validation or constraint failure."""
    def __init__(self, message: str, error_code: str = "VALIDATION_FAILED", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, error_code=error_code, details=details, is_recoverable=False)


# Infrastructure Exceptions
class InfrastructureException(JARVISBaseException):
    """Raised on database, networking, or service connectivity failure."""
    def __init__(self, message: str, error_code: str = "INFRASTRUCTURE_FAILURE", details: Optional[Dict[str, Any]] = None, is_recoverable: bool = True) -> None:
        super().__init__(message, error_code=error_code, details=details, is_recoverable=is_recoverable)


# Subsystem Exceptions
class SubsystemException(JARVISBaseException):
    """Base class for domain-specific subsystem failures."""
    pass


class ToolExecutionException(SubsystemException):
    """Raised when an Enterprise Tool Framework tool fails during execution."""
    def __init__(self, message: str, tool_name: str, details: Optional[Dict[str, Any]] = None, is_recoverable: bool = True) -> None:
        merged_details = details or {}
        merged_details["tool_name"] = tool_name
        super().__init__(message, error_code="TOOL_EXECUTION_FAILED", details=merged_details, is_recoverable=is_recoverable)


class PlannerException(SubsystemException):
    """Raised when Task Planner encounters planning or step execution failure."""
    def __init__(self, message: str, plan_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None, is_recoverable: bool = True) -> None:
        merged_details = details or {}
        if plan_id:
            merged_details["plan_id"] = plan_id
        super().__init__(message, error_code="PLANNER_FAILURE", details=merged_details, is_recoverable=is_recoverable)


class BrowserException(SubsystemException):
    """Raised on Playwright browser automation or navigation failure."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, is_recoverable: bool = True) -> None:
        super().__init__(message, error_code="BROWSER_AUTOMATION_FAILED", details=details, is_recoverable=is_recoverable)


class DesktopException(SubsystemException):
    """Raised on desktop window, OS input, or process management failure."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, is_recoverable: bool = True) -> None:
        super().__init__(message, error_code="DESKTOP_AUTOMATION_FAILED", details=details, is_recoverable=is_recoverable)


class MemoryException(SubsystemException):
    """Raised on vector store or memory engine query/persistence failure."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, is_recoverable: bool = True) -> None:
        super().__init__(message, error_code="MEMORY_ENGINE_FAILED", details=details, is_recoverable=is_recoverable)
