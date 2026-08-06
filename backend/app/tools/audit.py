"""
Enterprise Audit Logger for Tool Framework.
Logs every tool execution attempt with request ID, workflow ID, user, arguments, status, timing, rollback status, and approval source.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import structlog
from app.config import settings
from app.tools.schemas import AuditLogEntry, ExecutionStatus, PermissionLevel

logger = structlog.get_logger(__name__)


class ToolAuditLogger:
    """
    Structured audit logger storing execution records in an in-memory ring buffer
    and appending to disk for immutable security audit trails.
    """

    def __init__(self, buffer_capacity: int = 1000, log_file_path: Optional[str] = None) -> None:
        self._buffer: List[AuditLogEntry] = []
        self._capacity = buffer_capacity
        self._log_file_path = Path(log_file_path or "./logs/tool_audit.jsonl")
        self._ensure_log_directory()

    def _ensure_log_directory(self) -> None:
        try:
            self._log_file_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

    def log_execution(
        self,
        tool_name: str,
        user_role: str,
        permission_level: PermissionLevel,
        parameters: Dict[str, Any],
        status: ExecutionStatus,
        execution_time_seconds: float,
        retry_count: int = 0,
        request_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        user_id: Optional[str] = None,
        rolled_back: bool = False,
        approval_source: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> AuditLogEntry:
        """
        Creates, buffers, and persists an audit log entry.
        """
        entry = AuditLogEntry(
            id=str(uuid.uuid4()),
            request_id=request_id or str(uuid.uuid4()),
            workflow_id=workflow_id,
            tool_name=tool_name,
            user_id=user_id,
            user_role=user_role,
            permission_level=permission_level,
            parameters=self._sanitize_parameters(parameters),
            status=status,
            execution_time_seconds=round(execution_time_seconds, 4),
            retry_count=retry_count,
            rolled_back=rolled_back,
            approval_source=approval_source,
            error_message=error_message,
            timestamp=datetime.utcnow()
        )

        # Append to buffer
        self._buffer.append(entry)
        if len(self._buffer) > self._capacity:
            self._buffer.pop(0)

        # Log via structlog
        logger.info(
            "tool_execution_audit",
            audit_id=entry.id,
            tool=tool_name,
            user_role=user_role,
            status=status.value,
            elapsed_seconds=entry.execution_time_seconds,
            rolled_back=rolled_back
        )

        # Append to disk asynchronously/safely
        self._persist_to_file(entry)
        return entry

    def _sanitize_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Redacts sensitive parameters (passwords, tokens, keys) before logging."""
        sanitized = {}
        sensitive_keys = {"password", "secret", "token", "key", "api_key", "auth", "private"}
        for k, v in params.items():
            if any(s in k.lower() for s in sensitive_keys):
                sanitized[k] = "******"
            elif isinstance(v, dict):
                sanitized[k] = self._sanitize_parameters(v)
            elif isinstance(v, (str, int, float, bool, list)):
                sanitized[k] = v
            else:
                sanitized[k] = str(v)
        return sanitized

    def _persist_to_file(self, entry: AuditLogEntry) -> None:
        """Appends JSON line entry to audit log file."""
        try:
            with open(self._log_file_path, "a", encoding="utf-8") as f:
                f.write(entry.model_dump_json() + "\n")
        except Exception as e:
            logger.warning("Audit log file append failed", error=str(e))

    def get_recent_logs(self, limit: int = 100, tool_name: Optional[str] = None) -> List[AuditLogEntry]:
        """Returns recent buffered audit log records."""
        logs = self._buffer
        if tool_name:
            logs = [l for l in logs if l.tool_name == tool_name]
        return logs[-limit:]


audit_logger = ToolAuditLogger()
