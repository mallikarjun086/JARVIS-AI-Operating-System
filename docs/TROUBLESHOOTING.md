# JARVIS AI Operating System — Operational Troubleshooting & Diagnostics Guide

## Diagnostic Checklist & Common Resolutions

### 1. Database Connection Failures
- **Symptom**: `asyncpg.exceptions.CannotConnectNowError` or `sqlite3.OperationalError`.
- **Cause**: Database container not healthy or incorrect `DATABASE_URL`.
- **Resolution**:
  - Check container health status: `docker-compose ps`.
  - Verify PostgreSQL logs: `docker-compose logs db`.
  - Execute fallback SQLite connection by unsetting `DATABASE_URL` (uses `./jarvis_dev.db`).

### 2. Sandbox Subprocess ACL Restrictions
- **Symptom**: `opening NUL for ACL write: Access is denied` during subprocess invocation.
- **Cause**: Windows terminal sandbox ACL restrictions on `NUL` handle.
- **Resolution**:
  - Run commands in an unrestricted PowerShell terminal or Docker Linux container.
  - Verify sandbox health via `GET /api/v1/security/health`.

### 3. Alembic Database Migration Issues
- **Symptom**: `alembic.util.exc.CommandError: Can't locate revision`.
- **Cause**: Uninitialized migration environment or missing head revision.
- **Resolution**:
  ```bash
  cd backend
  alembic current
  alembic upgrade head
  ```

### 4. AI Provider API Key Fallbacks
- **Symptom**: `AIProviderError: Provider OpenAI API key missing`.
- **Cause**: API key environment variable not set.
- **Resolution**:
  - Set `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or `GEMINI_API_KEY` in `.env`.
  - Default routing falls back automatically to `MockProvider` when fallback is enabled (`ENABLE_PROVIDER_FALLBACK=true`).

---

## Operational Diagnostic Commands

```bash
# Check system health endpoints
curl -s http://localhost:8000/api/v1/health | jq .

# Inspect telemetry counters
curl -s http://localhost:8000/api/v1/telemetry | jq .
```
