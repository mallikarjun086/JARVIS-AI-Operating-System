# 🤖 JARVIS AI Operating System (Enterprise Multi-Agent OS Kernel)

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg)
![React](https://img.shields.io/badge/React-18.2.0-61DAFB.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5.2-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

An enterprise-grade, autonomous multi-agent Artificial Intelligence Operating System kernel. **JARVIS AI OS** provides an intelligent orchestrator featuring a 10-specialized agent swarm, Directed Acyclic Graph (DAG) task planner, 12-state microkernel workflow engine, 7-stage LLM provider router, multi-tier vector memory, Playwright browser and Windows desktop automation, computer vision, voice intelligence, and a modern glassmorphic web dashboard.

---

## 🌟 Key Architecture & Subsystems

```
                               ┌─────────────────────────────────────────┐
                               │  React 18 / TypeScript Web Dashboard    │
                               │        (Glassmorphic Dark UI)           │
                               └────────────────────┬────────────────────┘
                                                    │ REST / SSE API
                               ┌────────────────────▼────────────────────┐
                               │         FastAPI Kernel & Router         │
                               └────────────────────┬────────────────────┘
                                                    │
        ┌───────────────────┬───────────────────────┼───────────────────────┬───────────────────┐
        │                   │                       │                       │                   │
┌───────▼────────┐  ┌───────▼────────┐  ┌───────────▼───────────┐  ┌─────────▼────────┐  ┌───────▼────────┐
│  10-Agent Swarm│  │ Task Planner   │  │ 12-State Workflow     │  │  7-Stage LLM      │  │ Multi-Tier     │
│  Orchestration │  │ (DAG Engine)   │  │ Microkernel Engine    │  │  Provider Router  │  │ Vector Memory  │
└────────────────┘  └────────────────┘  └───────────────────────┘  └───────────────────┘  └────────────────┘
```

### 🐝 1. 10-Specialized Agent Swarm Topology
- **Agents**: `Coordinator`, `Planner`, `Research`, `Browser`, `Desktop`, `Coding`, `Memory`, `Vision`, `Voice`, and `Verifier`.
- **Inter-Agent Message Bus**: Asynchronous message passing, capability graph routing, shared memory context synchronization, and quality gate consensus voting.

### 🗺️ 2. Intelligent Task Planner Kernel
- **Intent Understanding**: Decomposes natural language user goals into atomic execution tasks.
- **DAG Execution Engine**: Kahn's topological sorting algorithm for parallel task batching.
- **Resilience**: Priority-based failure recovery policies (Retry, Skip non-critical, Rollback).

### 🔄 3. Microkernel Workflow Engine
- **12 Execution States**: `CREATED`, `PLANNED`, `VALIDATED`, `WAITING_APPROVAL`, `READY`, `RUNNING`, `PAUSED`, `RETRYING`, `FAILED`, `ROLLING_BACK`, `COMPLETED`, `CANCELLED`.
- **Saga Compensation**: Automated step-by-step saga rollback compensation on error.
- **Checkpoints**: Immutable execution history logging and resource reservation management.

### 🤖 4. 7-Stage LLM Provider Router
- **Pipeline**: Health Filter ➔ Capability Filter ➔ Cost Filter ➔ Priority Rules ➔ Dispatch ➔ Retry ➔ Fallback.
- **Multi-Provider Support**: OpenAI (`gpt-4o`), Google Gemini (`gemini-1.5-pro`), Anthropic Claude (`claude-3-5-sonnet`), and `MockProvider` for offline testing.
- **SSE Streaming**: Real-time Server-Sent Events token streaming and cost tracking telemetry.

### 🧠 5. Multi-Tier Memory Subsystem
- **Hybrid Storage**: Short-term conversation history + long-term ChromaDB vector embeddings.
- **Ranking Engine**: Multi-factor scoring combining recency decay, frequency, similarity, and importance.

### 🌐 6. Browser & Windows Desktop Automation
- **Playwright Web Controller**: Automated navigation, click, typing, screenshots, uploads, and human approval safety gatekeeper.
- **Windows Desktop Engine**: High-DPI scaling awareness, window handle tracking, process management, OCR text detection, and desktop input queues.

### 👁️ 7. Voice & Computer Vision Subsystem
- **Vision Intelligence**: Visual OCR, bounding box UI element detection, and layout clickability scoring.
- **Voice Intelligence**: Speech-To-Text (STT), Text-To-Speech (TTS), and Voice Activity Detection (VAD).

### 🔒 8. Enterprise Security & Vault
- **Authentication**: JWT Bearer authentication (`HS256`), Bcrypt password hashing.
- **RBAC**: Administrator privilege verification (`get_current_active_superuser`).
- **Audit Logs**: Encrypted secret key vault and system audit log trail.

---

## 📁 Repository Directory Structure

```text
JARVIS AI Operating System/
├── backend/                  # FastAPI Application Kernel
│   ├── alembic/              # Database schema migrations
│   ├── app/
│   │   ├── ai/               # 7-stage LLM router, provider SDKs, prompts
│   │   ├── api/              # 16 v1 REST API endpoint routers & dependency injection
│   │   ├── automation/       # Automation controller
│   │   ├── browser/          # Playwright browser manager & safety gatekeeper
│   │   ├── core/             # Event bus, logging, health manager, telemetry
│   │   ├── db/               # SQLAlchemy async engine, session, initial seeders
│   │   ├── desktop/          # Windows DPI, window manager, OCR, input queue
│   │   ├── memory/           # ChromaDB vector store, RAG, compression, ranking
│   │   ├── models/           # SQLAlchemy ORM models (User, Memory, Workflow)
│   │   ├── multi_agent/      # 10-Agent swarm pool, message bus, capability graph
│   │   ├── planner/          # DAG graph engine, intent decomposer, state machine
│   │   ├── schemas/          # Pydantic v2 schemas
│   │   ├── security/         # JWT auth, audit logging, RBAC, vault
│   │   ├── swe_agent/        # AST engine, patch engine, build manager
│   │   ├── tools/            # Enterprise Tool Registry across 11 categories
│   │   ├── vision/           # Computer vision bounding box & clickability scoring
│   │   ├── voice/            # Speech-to-Text, Text-to-Speech, VAD
│   │   └── workflow/         # 12-state workflow engine & saga compensation
│   ├── tests/                # Pytest unit & integration test suite (174 tests)
│   ├── Dockerfile            # Multi-stage Python 3.11 slim backend image
│   └── requirements.txt      # Backend Python dependencies
├── frontend/                 # React 18 + TypeScript + Vite Dashboard
│   ├── src/
│   │   ├── components/       # ProtectedRoute, Navbar, Sidebar
│   │   ├── context/          # AuthContext provider
│   │   ├── pages/            # 16 Console Pages (AIChat, MultiAgent, Planner, etc.)
│   │   ├── services/         # Axios API client interceptors
│   │   └── index.css         # Glassmorphism dark mode CSS design system
│   ├── Dockerfile            # Multi-stage Node 20 builder -> Nginx runner
│   └── package.json          # Frontend dependencies & build scripts
├── k8s/                      # Kubernetes deployment, service & HPA manifests
├── .github/workflows/        # GitHub Actions CI/CD matrix pipeline (ci.yml)
├── docker-compose.yml        # Docker Compose stack (PostgreSQL + Backend + Frontend)
└── pyproject.toml            # Project setup & pytest config
```

---

## ⚡ Quick Start Guide

### Prerequisites
- **Python**: 3.11 or 3.12
- **Node.js**: 20+ and **npm**
- **Docker & Docker Compose** (Optional for containerized mode)

---

### Option A: Local Development Setup

#### 1. Start the Backend API Server
```powershell
# Navigate to backend directory
cd backend

# Create and activate virtual environment (optional)
python -m venv venv
.\venv\Scripts\Activate.ps1   # On Windows
source venv/bin/activate       # On Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
> 🟢 **Backend API**: [http://localhost:8000/docs](http://localhost:8000/docs) (Interactive Swagger UI)

#### 2. Start the Frontend Dashboard UI
Open a **new terminal window**:
```powershell
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
> 🟢 **Web Application**: [http://localhost:3000](http://localhost:3000)

---

### Option B: Containerized Launch with Docker Compose

```powershell
# Build and launch all services (PostgreSQL + FastAPI + Nginx React Frontend)
docker-compose up --build -d

# View running container status
docker-compose ps
```

---

## 🔐 Default Login Credentials

- **Email**: `admin@jarvis.ai`
- **Password**: `admin12345`

---

## 🧪 Testing & Quality Assurance

Run the comprehensive Pytest suite (174 unit and integration tests):

```powershell
cd backend
pytest tests/ -v
```

---

## 🚀 CI/CD Pipeline

The repository includes a GitHub Actions pipeline (`.github/workflows/ci.yml`) performing:
- **Backend Linting & Tests**: Python 3.11, PostgreSQL service container, Ruff linting, Pytest execution with coverage.
- **Frontend Build Verification**: Node.js 20, dependency installation, TypeScript compilation, and production build check.

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.r e f r e s h   c o n t r i b u t o r   c a c h e  
 