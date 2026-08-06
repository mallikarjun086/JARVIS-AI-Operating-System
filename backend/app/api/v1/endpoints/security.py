"""
FastAPI Endpoints for Enterprise Security & Hardening Subsystem.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.api.deps import get_current_user
from app.models.user import User
from app.security.command_guard import command_guard
from app.security.compliance import security_compliance
from app.security.rate_limiter import rate_limiter
from app.security.schemas import (
    CommandValidationResult,
    OWASPAuditReport,
    PenTestChecklist,
    ProcessExecutionRequest,
    ProcessExecutionResult,
    RateLimitConfig,
    SecretVaultEntry,
    ThreatModelDocument,
)
from app.security.sandbox import sandbox_engine
from app.security.vault import secrets_vault

router = APIRouter()


@router.get("/health", summary="Get Security Engine Health Telemetry")
async def get_security_health():
    """Returns Process Execution Engine health telemetry."""
    return sandbox_engine.get_health_status()


@router.get("/metrics", summary="Get Process Execution Metrics")
async def get_security_metrics():
    """Returns telemetry counters for executed, blocked, and timed out sandboxed processes."""
    return sandbox_engine.get_metrics()


@router.post("/sandbox/execute", response_model=ProcessExecutionResult, summary="Execute Isolated Process in Sandbox")
async def execute_sandboxed_process(
    req: ProcessExecutionRequest,
    current_user: User = Depends(get_current_user)
) -> ProcessExecutionResult:
    """
    Asynchronously executes a shell process within an isolated sandbox environment
    enforcing command validation, environment scrubbing, working directory bounds, and resource limits.
    """
    return await sandbox_engine.execute_in_sandbox_async(
        command=req.command,
        timeout_seconds=req.timeout_seconds,
        cwd=req.cwd
    )


@router.post("/vault/secrets", response_model=SecretVaultEntry, summary="Store Encrypted Secret in Vault")
async def store_secret(
    key_name: str = Query(..., description="Secret key name identifier"),
    value: str = Query(..., description="Secret raw value to encrypt"),
    current_user: User = Depends(get_current_user)
) -> SecretVaultEntry:
    """Encrypts raw secret value using AES-256 Fernet and stores entry in Secrets Vault."""
    return secrets_vault.set_secret(key_name, value)


@router.get("/vault/secrets/{key_name}", summary="Retrieve Decrypted Secret from Vault")
async def retrieve_secret(
    key_name: str,
    current_user: User = Depends(get_current_user)
):
    """Decrypts and returns plaintext secret by key name."""
    secret = secrets_vault.get_secret(key_name)
    if not secret:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Secret key '{key_name}' not found.")
    return {"key_name": key_name, "decrypted_value": secret}


@router.get("/vault/secrets", response_model=List[SecretVaultEntry], summary="List Secrets Metadata")
async def list_secrets(
    current_user: User = Depends(get_current_user)
) -> List[SecretVaultEntry]:
    """Lists secret metadata entries stored in vault (values remain encrypted)."""
    return secrets_vault.list_secret_entries()


@router.post("/validate-command", response_model=CommandValidationResult, summary="Validate Command for Injection")
async def validate_command_injection(
    command: str = Query(..., description="Shell command string to inspect"),
    current_user: User = Depends(get_current_user)
) -> CommandValidationResult:
    """Inspects shell command for dangerous injection patterns (;, &&, |, $(...)) and returns safety verdict."""
    return command_guard.validate_command(command)


@router.get("/rate-limit-status", response_model=RateLimitConfig, summary="Check Rate Limit Telemetry")
async def check_rate_limit_status(
    current_user: User = Depends(get_current_user)
) -> RateLimitConfig:
    """Returns sliding-window rate limit status for current requester."""
    return rate_limiter.check_rate_limit()


@router.get("/owasp-audit", response_model=OWASPAuditReport, summary="Get OWASP Top 10 Audit Report")
async def get_owasp_audit_report(
    current_user: User = Depends(get_current_user)
) -> OWASPAuditReport:
    """Retrieves comprehensive OWASP Top 10 Security Audit Findings."""
    return security_compliance.get_owasp_audit_report()


@router.get("/threat-model", response_model=List[ThreatModelDocument], summary="Get STRIDE Threat Model")
async def get_stride_threat_model(
    current_user: User = Depends(get_current_user)
) -> List[ThreatModelDocument]:
    """Retrieves STRIDE Threat Modeling Document items."""
    return security_compliance.get_stride_threat_model()


@router.get("/pentest-checklist", response_model=List[PenTestChecklist], summary="Get Penetration Testing Checklist")
async def get_pentest_checklist(
    current_user: User = Depends(get_current_user)
) -> List[PenTestChecklist]:
    """Retrieves automated Penetration Testing Verification Checklist."""
    return security_compliance.get_pentest_checklist()
