# JARVIS AI Operating System v1.0

<div align="center">

```
     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗     █████╗ ██╗
     ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝    ██╔══██╗██║
     ██║███████║██████╔╝██║   ██║██║███████╗    ███████║██║
██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║    ██╔══██║██║
╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║    ██║  ██║██║
 ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝    ╚═╝  ╚═╝╚═╝
```

**Just A Rather Very Intelligent System — AI Operating System v1.0**

*Production-Grade Autonomous AI Agent Platform*

[![CI Pipeline](https://github.com/mallikarjun086/JARVIS-AI-Operating-System/actions/workflows/ci.yml/badge.svg)](https://github.com/mallikarjun086/JARVIS-AI-Operating-System/actions)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB?logo=react)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?logo=typescript)](https://typescriptlang.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0.0-blue)](VERSION)

</div>

---

## Overview

JARVIS AI OS is a **production-ready, enterprise-grade AI Operating System** that transforms natural language commands into fully automated task executions — across the web, desktop, files, code, and cloud infrastructure.

**One interface. Infinite capability.**

Type or speak any goal to JARVIS, and it autonomously orchestrates a **10-Agent Swarm Mesh**, **35-Tool Framework**, **ChromaDB Vector Memory**, and **Code Synthesis Engine** to execute it end-to-end — with live execution streaming, approval gates, and full observability.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                   JARVIS AI OPERATING SYSTEM v1.0                   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │           UNIFIED MULTIMODAL COMMAND CENTER (HUD)            │   │
│  │     Voice STT ←→ Chat Interface ←→ TTS Audio Output          │   │
│  │         Command Palette (⌘K) · Toast Notifications           │   │
│  └───────────────────────┬─────────────────────────────────────┘   │
│                          │ Natural Language Command                 │
│                          ▼                                          │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              JARVIS ORCHESTRATION ENGINE                      │   │
│  │  Intent Parse → DAG Plan → Agent Select → Execute → Verify   │   │
│  │                  (RBAC · Approval Gates · SSE Stream)         │   │
│  └──┬──────────┬──────────┬──────────┬──────────┬──────────────┘   │
│     │          │          │          │          │                    │
│     ▼          ▼          ▼          ▼          ▼                    │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────────────────────┐    │
│  │MEMORY│ │PLNR  │ │CODING│ │RESRCH│ │   TOOL FRAMEWORK      │    │
│  │RAG   │ │DAG   │ │SWE   │ │BROWSER│ │  35 Registered Tools  │    │
│  │Chroma│ │Engine│ │Agent │ │Agent  │ │  • browser • desktop  │    │
│  └──────┘ └──────┘ └──────┘ └──────┘ │  • git • file • net   │    │
│                                       └──────────────────────┘    │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                10-AGENT SWARM MESH                            │   │
│  │  Coordinator · Planner · Researcher · Coder · Browser ·      │   │
│  │  Desktop · Memory · Verifier · Voice · Security               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                INFRASTRUCTURE LAYER                           │   │
│  │  FastAPI + Uvicorn · PostgreSQL + Alembic · Redis Cache       │   │
│  │  JWT Auth + RBAC · Structured Logging · Prometheus Metrics    │   │
│  │  Docker + Kubernetes · GitHub Actions CI/CD                   │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Git

### 1. Clone & Setup
```bash
git clone https://github.com/mallikarjun086/JARVIS-AI-Operating-System.git
cd "JARVIS AI Operating System"
```

### 2. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

### 4. Login
| Field | Value |
|-------|-------|
| Email | `operator@jarvis.ai` |
| Password | `SecurePass123!` |

---

## 🐳 Docker Compose (Recommended)

```bash
# Copy environment template
cp .env.example .env
# Edit .env with your API keys and SECRET_KEY

# Build & start all services
docker compose up -d --build

# Run database migrations
docker compose exec backend alembic upgrade head

# View logs
docker compose logs -f backend
```

**Services:** PostgreSQL 16 · Redis 7 · FastAPI Backend · Nginx Frontend

---

## ⚡ Feature Matrix

| Feature | Status | Technology |
|---------|--------|-----------|
| Unified Voice+Chat HUD | ✅ Live | Web Speech API + FastAPI |
| Natural Language Orchestration | ✅ Live | 4-step Pipeline |
| 10-Agent Swarm Execution | ✅ Live | Custom Orchestrator |
| ChromaDB Vector Memory RAG | ✅ Live | ChromaDB + Sentence Transformers |
| Task Planner DAG Engine | ✅ Live | Custom Graph Engine |
| Browser Automation | ✅ Live | Playwright |
| Desktop Automation | ✅ Live | PyAutoGUI + pywinauto |
| Software Engineering Agent | ✅ Live | Custom SWE Framework |
| Computer Vision | ✅ Live | Pillow + OpenAI Vision |
| Voice STT/TTS | ✅ Live | Web Speech API + Custom |
| Multi-Provider LLM Routing | ✅ Live | OpenAI / Anthropic / Gemini |
| Security Sandbox | ✅ Live | Process isolation + allowlist |
| RBAC + Approval Gates | ✅ Live | JWT + Risk Evaluation |
| Prometheus Metrics | ✅ Live | `/api/v1/metrics` |
| Command Palette (Ctrl+K) | ✅ Live | React |
| Toast Notifications | ✅ Live | React Context |
| Real-time SSE Streaming | ✅ Live | FastAPI StreamingResponse |
| Security Headers | ✅ Live | Starlette Middleware |
| CI/CD Pipeline | ✅ Active | GitHub Actions (5 jobs) |
| Docker + Kubernetes | ✅ Ready | Docker Compose + Helm |
| 180+ Backend Tests | ✅ Passing | Pytest + pytest-asyncio |

---

## 🎯 Demo Walkthrough (3 Minutes)

### Step 1 — Open JARVIS Command Center
Navigate to `http://localhost:3000/jarvis-command-center`

### Step 2 — Voice Command
1. Click the **🎤 Microphone** button
2. Speak: *"Build a microservice REST API for processing user orders"*
3. Watch the **4-step execution timeline** animate in real time:
   - **[MEMORY]** — ChromaDB retrieves relevant context
   - **[PLANNER]** — Task DAG decomposes the goal into subtasks
   - **[CODING]** — SWE Agent generates typed FastAPI code
   - **[VERIFIER]** — Quality gate evaluates output (100% consensus)
4. JARVIS speaks the response back via TTS

### Step 3 — Approval Gate Test
1. Type: *"Delete database table and shutdown server"*
2. The **High-Risk Approval Modal** appears (CRITICAL risk)
3. Click **Reject** or **Authorize**

### Step 4 — Command Palette
1. Press **Ctrl+K** (or ⌘K on Mac)
2. Type "memory" — instantly navigates to Memory Console
3. All 12 JARVIS consoles are searchable

---

## 🔑 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/login` | Obtain JWT access token |
| `POST` | `/api/v1/jarvis/execute` | Execute natural language command |
| `GET` | `/api/v1/jarvis/stream` | SSE real-time execution stream |
| `POST` | `/api/v1/jarvis/approve` | Authorize/reject high-risk action |
| `GET` | `/api/v1/jarvis/history` | Retrieve session conversation history |
| `GET` | `/api/v1/metrics` | Prometheus-compatible metrics |
| `GET` | `/api/v1/health` | Liveness probe |
| `GET` | `/api/v1/readiness` | Readiness probe (DB + LLM) |
| `POST` | `/api/v1/ai/chat/completions` | Multi-provider LLM completion |
| `POST` | `/api/v1/memory/store` | Store vector memory |
| `GET` | `/api/v1/memory/search` | Semantic memory search |
| `POST` | `/api/v1/planner/create` | Create task execution plan |
| `POST` | `/api/v1/multi-agent/dispatch` | Dispatch swarm goal |
| `POST` | `/api/v1/tools/execute` | Execute registered tool |
| `POST` | `/api/v1/swe-agent/action` | SWE agent action |

Interactive docs: `http://localhost:8000/docs`

---

## 🧪 Testing

```bash
# Full backend test suite (180+ tests)
cd backend
pytest tests/ -v --cov=app --cov-report=term-missing

# Specific subsystem tests
pytest tests/test_jarvis_command_center.py -v   # JARVIS Command Center
pytest tests/test_multi_agent.py -v            # Swarm Orchestration
pytest tests/test_ai_providers.py -v           # LLM Providers (75 tests)

# Frontend type check and build
cd frontend
npx tsc --noEmit
npm run build
```

---

## 🔐 Security

- **JWT Authentication** on all protected endpoints
- **RBAC** with superuser/user role enforcement
- **Approval Gates** for HIGH/CRITICAL risk commands
- **Security Headers**: X-Frame-Options, HSTS, X-Content-Type-Options, CSP
- **Request Correlation IDs** for distributed tracing
- **Secret Redaction** in logs via structured logging
- **Command Injection Protection** via `SecuritySandboxEngine`
- **Path Traversal Protection** in file operations
- **Rate Limiting** configurable via `RATE_LIMIT_REQUESTS`

---

## 📁 Project Structure

```
JARVIS AI Operating System/
├── backend/
│   ├── app/
│   │   ├── ai/          # LLM providers (OpenAI, Anthropic, Gemini, Mock)
│   │   ├── jarvis/      # Unified orchestration engine ← NEW
│   │   ├── memory/      # ChromaDB RAG + vector store
│   │   ├── planner/     # Task DAG decomposition
│   │   ├── multi_agent/ # 10-agent swarm mesh
│   │   ├── tools/       # 35-tool execution framework
│   │   ├── swe_agent/   # Software engineering automation
│   │   ├── browser/     # Playwright browser automation
│   │   ├── desktop/     # Desktop automation
│   │   ├── vision/      # Computer vision subsystem
│   │   ├── voice/       # STT/TTS voice subsystem
│   │   ├── security/    # RBAC, vault, sandbox
│   │   ├── workflow/    # Workflow automation engine
│   │   └── api/v1/      # FastAPI router assembly
│   └── tests/           # 180+ pytest tests
├── frontend/
│   └── src/
│       ├── pages/       # 18 console pages
│       ├── components/  # Sidebar, Navbar, CommandPalette ← NEW
│       ├── context/     # AuthContext, ToastContext ← NEW
│       └── services/    # API client
├── k8s/                 # Kubernetes manifests
├── .github/workflows/   # 5-job CI/CD pipeline
├── docker-compose.yml   # Production compose stack
├── VERSION              # Semantic version tag
└── CHANGELOG.md         # Release history
```

---

## 🗺️ Roadmap

- [ ] OpenTelemetry full distributed tracing
- [ ] Multi-user workspaces with team collaboration
- [ ] Plugin marketplace for custom agents
- [ ] Mobile app (React Native)
- [ ] Fine-tuning pipeline UI
- [ ] On-premises LLM (Ollama) integration
- [ ] GitHub Copilot-style IDE extension

---

## 📄 License

MIT License — Copyright (c) 2026 Mallikarjun Gala

---

<div align="center">
  <strong>Built with ❤️ by Mallikarjun Gala</strong><br>
  <a href="https://github.com/mallikarjun086">GitHub</a> ·
  <a href="http://localhost:8000/docs">API Docs</a> ·
  <a href="CHANGELOG.md">Changelog</a>
</div>