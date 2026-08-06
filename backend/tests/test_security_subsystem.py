"""
Pytest Test Suite for Enterprise Security & Hardening Subsystem.
Tests AES-256 Fernet encryption, Secrets Vault, Rate Limiting, Command Injection Detection, Sandbox Execution, Secure Browser Context, OWASP Top 10 Audit, STRIDE Threat Model, and PenTest Checklist.
"""

from httpx import AsyncClient
import pytest
from app.security.command_guard import command_guard
from app.security.compliance import security_compliance
from app.security.crypto import crypto_engine
from app.security.rate_limiter import rate_limiter
from app.security.sandbox import sandbox_engine
from app.security.vault import secrets_vault


@pytest.mark.asyncio
async def test_aes256_fernet_encryption_and_secrets_vault():
    """Verifies AES-256 Fernet encryption and Secrets Vault storage at rest."""
    raw_secret = "sk-proj-test-secret-123456"
    encrypted = crypto_engine.encrypt_string(raw_secret)

    assert encrypted != raw_secret
    assert crypto_engine.decrypt_string(encrypted) == raw_secret

    # Vault Manager
    secrets_vault.set_secret("TEST_API_KEY", raw_secret)
    retrieved = secrets_vault.get_secret("TEST_API_KEY")
    assert retrieved == raw_secret


@pytest.mark.asyncio
async def test_rate_limiter_and_command_injection_guard():
    """Tests rate limiter telemetry and command injection sanitization guard."""
    rate = rate_limiter.check_rate_limit("127.0.0.1")
    assert rate.is_rate_limited is False

    # Safe Command
    safe_res = command_guard.validate_command("pytest tests/")
    assert safe_res.is_safe is True

    # Dangerous Command Injection
    danger_res = command_guard.validate_command("echo hello; rm -rf /")
    assert danger_res.is_safe is False
    assert len(danger_res.flagged_reasons) >= 1


@pytest.mark.asyncio
async def test_sandbox_execution_and_compliance():
    """Tests process isolation sandbox and compliance engines."""
    sb_res = sandbox_engine.execute_in_sandbox("echo SANDBOX_TEST")
    assert sb_res["sandboxed"] is True
    assert sb_res["blocked"] is False

    # OWASP Top 10 Report
    owasp = security_compliance.get_owasp_audit_report()
    assert owasp.overall_compliance_score == 100.0
    assert len(owasp.findings) == 9

    # STRIDE Threat Model
    stride = security_compliance.get_stride_threat_model()
    assert len(stride) >= 6

    # PenTest Checklist
    pentest = security_compliance.get_pentest_checklist()
    assert len(pentest) >= 5


@pytest.mark.asyncio
async def test_security_api_endpoints(client: AsyncClient):
    """Tests FastAPI REST endpoints for Security & Hardening."""
    # Register & login
    await client.post("/api/v1/auth/register", json={"email": "sec@jarvis.ai", "password": "Password123!", "full_name": "Sec User"})
    login_resp = await client.post("/api/v1/auth/login", data={"username": "sec@jarvis.ai", "password": "Password123!"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Store Secret in Vault Endpoint
    v_store = await client.post("/api/v1/security/vault/secrets?key_name=MY_SECRET&value=SecretVal123", headers=headers)
    assert v_store.status_code == 200
    assert "encrypted_value" in v_store.json()

    # 2. Retrieve Secret Endpoint
    v_get = await client.get("/api/v1/security/vault/secrets/MY_SECRET", headers=headers)
    assert v_get.status_code == 200
    assert v_get.json()["decrypted_value"] == "SecretVal123"

    # 3. Validate Command Endpoint
    cmd_resp = await client.post("/api/v1/security/validate-command?command=git+status", headers=headers)
    assert cmd_resp.status_code == 200
    assert cmd_resp.json()["is_safe"] is True

    # 4. OWASP Audit Endpoint
    owasp_resp = await client.get("/api/v1/security/owasp-audit", headers=headers)
    assert owasp_resp.status_code == 200
    assert owasp_resp.json()["overall_compliance_score"] == 100.0

    # 5. Threat Model Endpoint
    stride_resp = await client.get("/api/v1/security/threat-model", headers=headers)
    assert stride_resp.status_code == 200
    assert len(stride_resp.json()) >= 6

    # 6. PenTest Checklist Endpoint
    pt_resp = await client.get("/api/v1/security/pentest-checklist", headers=headers)
    assert pt_resp.status_code == 200
    assert len(pt_resp.json()) >= 5
