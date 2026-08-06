"""
Pydantic Schemas for Enterprise Security & Hardening Subsystem.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field, ConfigDict


class SecurityLevel(str, Enum):
    PUBLIC = "PUBLIC"
    USER = "USER"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"
    SYSTEM_CRITICAL = "SYSTEM_CRITICAL"


class SecretVaultEntry(BaseModel):
    """Encrypted secret entry metadata payload."""
    secret_id: str = Field(default_factory=lambda: f"sec-{uuid.uuid4().hex[:8]}")
    key_name: str
    encrypted_value: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class RateLimitConfig(BaseModel):
    """Rate limit configuration and telemetry payload."""
    ip_address: str
    requests_per_minute: int = 100
    current_count: int = 0
    is_rate_limited: bool = False


class CommandValidationResult(BaseModel):
    """Command injection validation result payload."""
    command: str
    is_safe: bool
    flagged_reasons: List[str] = Field(default_factory=list)
    sanitized_command: str


class OWASPAuditFinding(BaseModel):
    """OWASP Top 10 Security Audit finding item."""
    owasp_category: str  # A01:2021-Broken Access Control, A03:2021-Injection, etc.
    title: str
    status: str = "PASSED"  # PASSED, MITIGATED, WARNING
    mitigation_details: str


class OWASPAuditReport(BaseModel):
    """Comprehensive OWASP Security Audit Report."""
    findings: List[OWASPAuditFinding] = Field(default_factory=list)
    overall_compliance_score: float = 100.0
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class ThreatModelDocument(BaseModel):
    """STRIDE Threat Modeling Document item."""
    stride_category: str  # Spoofing, Tampering, Repudiation, Info Disclosure, DoS, Elevation of Privilege
    threat_vector: str
    impact: str
    likelihood: str
    mitigation_strategy: str


class PenTestChecklist(BaseModel):
    """Penetration Testing Verification Checklist item."""
    category: str
    test_case: str
    status: str = "VERIFIED_SECURE"  # VERIFIED_SECURE, PENDING, FAILED


class ProcessExecutionStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"
    CANCELLED = "CANCELLED"
    REQUIRES_HUMAN_APPROVAL = "REQUIRES_HUMAN_APPROVAL"
    BLOCKED_SECURITY = "BLOCKED_SECURITY"


class ProcessExecutionRequest(BaseModel):
    """Process execution payload enforcing security parameters."""
    command: str
    cwd: Optional[str] = None
    timeout_seconds: int = 15
    environment_variables: Dict[str, str] = Field(default_factory=dict)
    requires_approval: bool = False
    requested_by: str = "SYSTEM_USER"


class ProcessExecutionResult(BaseModel):
    """Audit payload containing process execution output and telemetry."""
    process_id: str = Field(default_factory=lambda: f"proc-{uuid.uuid4().hex[:8]}")
    command: str
    status: ProcessExecutionStatus
    exit_code: Optional[int] = None
    stdout: str = ""
    stderr: str = ""
    sandboxed: bool = True
    blocked: bool = False
    requires_approval: bool = False
    execution_time_ms: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)

