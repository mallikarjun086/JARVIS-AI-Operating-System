# JARVIS AI Operating System — Security Architecture & Hardening Guide

## Security Overview

The **JARVIS AI Operating System** enforces defense-in-depth enterprise security across all 19 subservices.

---

## Core Security Components

### 1. Role-Based Access Control (RBAC)
- **Engine**: [backend/app/security/engine.py](file:///c:/Users/Mallikarjun%20Gala/OneDrive/Desktop/JARVIS%20AI%20Operating%20System/backend/app/security/engine.py)
- **Roles**:
  - `SUPERUSER` / `ADMIN`: Full system permissions across all endpoints, processes, and database operations.
  - `USER`: Restricted access permissions (`read_only`, `interact_voice`, `execute_workflows`). Attempts to execute unauthorized operations raise a `PermissionError`.
  - `AUDITOR`: Read-only access to audit logs and security telemetry.

### 2. Process Execution Sandbox
- **Engine**: [backend/app/security/sandbox.py](file:///c:/Users/Mallikarjun%20Gala/OneDrive/Desktop/JARVIS%20AI%20Operating%20System/backend/app/security/sandbox.py)
- **Safeguards**:
  - **Environment Scrubbing**: Sensitive keys (`SECRET_KEY`, `POSTGRES_PASSWORD`, `DATABASE_URL`, `OPENAI_API_KEY`, etc.) are stripped before subprocess invocation.
  - **Command Injection Guard**: Tokenizes input commands and blocks dangerous shell escape sequences.
  - **Workspace Path Isolation**: Restricts file read/write operations within `WORKSPACE_ROOT` to prevent path traversal attacks (`..` navigation).

### 3. JWT Authentication & Secret Protection
- **Module**: [backend/app/core/security.py](file:///c:/Users/Mallikarjun%20Gala/OneDrive/Desktop/JARVIS%20AI%20Operating%20System/backend/app/core/security.py)
- **Algorithm**: `HS256` token signing with configurable expiration (`ACCESS_TOKEN_EXPIRE_MINUTES`).
- **Production Key Validation**: `Settings.validate_production_security()` in [backend/app/config.py](file:///c:/Users/Mallikarjun%20Gala/OneDrive/Desktop/JARVIS%20AI%20Operating%20System/backend/app/config.py) logs a critical alert if default development keys are active when `ENV=production`.

### 4. Secret Redaction & Audit Logging
- **Logging**: Configured via `structlog` filters in `backend/app/core/logging.py`.
- **Censored Fields**: API keys, bearer authorization tokens, passwords, and raw JWT strings are automatically redacted prior to log emission.

---

## Security Verification Commands

To run static security linting and security dependency scanning locally or in CI:

```bash
# 1. Static Security Analysis with Bandit
bandit -r backend/app

# 2. Dependency Vulnerability Check with Safety
safety check -r backend/requirements.txt
```
