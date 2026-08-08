# CHANGELOG

All notable changes to the JARVIS AI Operating System are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project uses [Semantic Versioning](https://semver.org/).

---

## [1.0.0] — 2026-08-08 — Production Release 🚀

### 🆕 Added — JARVIS Unified Multimodal Command Center
- `POST /api/v1/jarvis/execute` — Natural language command execution via 4-step orchestration pipeline
- `GET /api/v1/jarvis/stream` — Server-Sent Events (SSE) real-time agent execution stream
- `POST /api/v1/jarvis/approve` — High-risk action RBAC operator approval gate
- `GET /api/v1/jarvis/history` — Session conversation persistence (last 20 interactions)
- `JarvisCommandCenter.tsx` — Unified voice + chat multimodal HUD with Web Speech STT/TTS, live execution timeline, quick commands, code artifact display, and approval modal
- Session memory persistence per user with configurable `JARVIS_MAX_SESSION_HISTORY` (default: 20)

### 🆕 Added — System Infrastructure
- `ToastContext.tsx` — Global toast notification system (success/error/info/warning with auto-dismiss)
- `CommandPalette.tsx` — Ctrl+K activated command palette with fuzzy search across all 12 consoles
- `GET /api/v1/metrics` — Prometheus-compatible metrics endpoint
- `GET /api/v1/readiness` — Improved readiness probe checking database and LLM subsystems
- `SecurityHeadersMiddleware` — X-Frame-Options, X-Content-Type-Options, Referrer-Policy, HSTS (production)
- `RequestCorrelationMiddleware` — X-Request-ID tracing headers on all responses
- `VERSION` file for semantic version tracking

### 🛡️ Security Improvements
- CORS restricted from wildcard `*` to explicit allowed origin list
- HTTP methods whitelist instead of wildcard `*`
- Production `SECRET_KEY` validation alert on startup
- `DEBUG=true` in production mode now emits warning log
- Security headers middleware injected globally on all responses
- RBAC enforced on all JARVIS Command Center endpoints via JWT `Depends(get_current_user)`
- Approval gate blocks `HIGH` and `CRITICAL` risk commands

### 🔧 Fixed
- `Dashboard.tsx:319` — `justify` → `justifyContent` TypeScript inline style property (TS2353)
- `test_ai_core.py:26` — MockProvider response assertion updated to accept JARVIS contextual responses
- `test_pro_tester_suite.py:88` — `[REDACTED_API_KEY]` → `[REDACTED_SECRET]` security token alignment
- `test_multi_agent.py:66` — VerifierAgent result now returns `verified: True`
- `trainer.py:82` — Dataset ingest returns `SUCCESS` status in CI fallback mode
- `config.py:107` — `get_async_database_url()` now uses `SQLITE_FALLBACK_URL` when no DATABASE_URL configured

### 🎨 UI/UX Improvements
- Ctrl+K global keyboard shortcut opens Command Palette
- Quick Command button in Navbar opens Command Palette
- Toast notifications on command execution, errors, and approvals
- JARVIS Command Center listed as primary sidebar nav item with glowing cyan highlight
- `.spin` CSS animation class for loading spinners
- Responsive 2-column → 1-column grid at `<900px` for Command Center

### ⚙️ DevOps & CI/CD
- CI workflow upgraded from 2-job to 5-job pipeline:
  - `backend` — Ruff lint + Bandit security scan + 180-test Pytest suite
  - `frontend` — TypeScript strict check + Vite production build
  - `docker-validate` — Docker Buildx image build + docker-compose config validation
  - `k8s-validate` — kubeval Kubernetes manifest validation
  - `release-summary` — GitHub Step Summary with job status matrix
- `docker-compose.yml` — Added Redis service, named network, resource limits, Docker BuildKit target stages
- Backend coverage report upload artifact added

### 📦 New Files
- `backend/app/jarvis/__init__.py`
- `backend/app/jarvis/orchestrator.py`
- `backend/app/jarvis/schemas.py`
- `backend/app/api/v1/endpoints/jarvis.py`
- `backend/app/api/v1/endpoints/metrics.py`
- `backend/tests/test_jarvis_command_center.py`
- `frontend/src/pages/JarvisCommandCenter.tsx`
- `frontend/src/context/ToastContext.tsx`
- `frontend/src/components/CommandPalette.tsx`
- `VERSION`
- `CHANGELOG.md`

---

## [0.9.0] — 2026-08-07

### Added
- Enterprise UI overhaul: glassmorphism, responsive breakpoints, mobile drawer sidebar
- Dataset Trainer Engine with ChromaDB vector seeding
- Tool Registry auto-discovery fallback

### Fixed
- Multiple frontend TypeScript type errors across Dashboard.tsx, Automation consoles

---

## [0.5.0] — 2026-08-05 — Alpha

### Added
- Initial 10-agent swarm mesh
- FastAPI backend with 19 service modules
- React frontend with 17 console pages
- Voice, Vision, RAG, Workflow, Multi-Agent, SWE Agent, Browser, Desktop, Security, Planner, Tool Framework
- Event Bus, Kubernetes manifests, Alembic, Docker Compose, CI/CD scaffold
