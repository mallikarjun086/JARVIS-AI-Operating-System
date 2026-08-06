"""
Security Audit Logger Engine (Sprint 1).
Provides structured security audit trail recording, threat logging, and policy violation reporting.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid
import structlog

logger = structlog.get_logger(__name__)


class SecurityAuditor:
    """Central Security Audit Logger capturing security events, violations, and access trails."""

    def __init__(self) -> None:
        self._audit_trail: List[Dict[str, Any]] = []

    def log_event(
        self,
        event_type: str,
        severity: str = "INFO",
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Logs structured security audit event."""
        entry = {
            "id": f"secaudit-{uuid.uuid4().hex[:8]}",
            "event_type": event_type,
            "severity": severity.upper(),
            "user_id": user_id,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        self._audit_trail.append(entry)
        logger.info("Security Audit Logged", event_type=event_type, severity=severity, user_id=user_id)
        return entry

    def get_audit_trail(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Returns recent security audit logs."""
        return self._audit_trail[-limit:]


security_auditor = SecurityAuditor()
