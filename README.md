<div align="center">

```text
       ██████╗  █████╗ ██████╗ ██╗   ██╗██╗███████╗     █████╗ ██╗      ██████╗ ███████╗
       ╚══██╔══╝██╔══██╗██╔══██╗██║   ██║██║██╔════╝    ██╔══██╗██║     ██╔═══██╗██╔════╝
          ██║   ███████║██████╔╝██║   ██║██║███████╗    ███████║██║     ██║   ██║███████╗
          ██║   ██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║    ██╔══██║██║     ██║   ██║╚════██║
          ██║   ██║  ██║██║  ██║ ╚████╔╝ ██║███████║    ██║  ██║██║     ╚██████╔╝███████║
          ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝    ╚═╝  ╚═╝╚═╝      ╚═════╝ ╚══════╝
```

# 🤖 JARVIS AI Operating System
### *Enterprise Multi-Agent OS Kernel & Autonomous Swarm Platform*

[![Version](https://img.shields.io/badge/Version-1.0.0-blue.svg?style=for-the-badge&logo=semver)](https://github.com/mallikarjun086/JARVIS-AI-Operating-System)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-3776AB.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.2.0-61DAFB.svg?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2-3178C6.svg?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Build](https://img.shields.io/badge/Build-Passing-brightgreen.svg?style=for-the-badge)](https://github.com/mallikarjun086/JARVIS-AI-Operating-System)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

---

</div>

## 📌 Executive Summary

**JARVIS AI OS** is a production-grade, enterprise autonomous multi-agent Artificial Intelligence Operating System kernel. Built upon a decoupled **Clean Architecture**, JARVIS integrates a **10-specialized agent swarm**, a **Directed Acyclic Graph (DAG) task planner**, a **12-state microkernel workflow engine**, a **7-stage LLM provider router**, a **multi-tier ChromaDB vector memory**, **Playwright web browser and Windows desktop automation**, **computer vision**, **voice intelligence**, and a state-of-the-art **glassmorphic React web dashboard**.

---

## 🏛️ System Architecture

```text
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                          React 18 / TypeScript Web Dashboard                           │
│                       (Glassmorphic Dark UI & Real-Time SSE)                            │
└───────────────────────────────────────────┬─────────────────────────────────────────────┘
                                            │ REST / SSE HTTP API
┌───────────────────────────────────────────▼─────────────────────────────────────────────┐
│                            FastAPI OS Kernel Router v1                                  │
└───────────────────────────────────────────┬─────────────────────────────────────────────┘
                                            │
   ┌───────────────────┬────────────────────┼────────────────────┬───────────────────┐
   │                   │                    │                    │                   │
┌──▼─────────────┐  ┌──▼──────────────┐  ┌──▼────────────────┐  ┌──▼──────────────┐  ┌──▼──────────────┐
│ 10-Agent Swarm │  │ Task Planner    │  │ 12-State Workflow │  │ 7-Stage LLM     │  │ Multi-Tier      │
│ Orchestration  │  │ (DAG Kernel)    │  │ Microkernel       │  │ Provider Router │  │ Vector Memory   │
└────────────────┘  └─────────────────┘  └───────────────────┘  └─────────────────┘  └─────────────────┘
```

---

## 🚀 Key Modules & Capabilities

| Subsystem Module | Description & Architecture Highlights |
| :--- | :--- |
| **🐝 10-Agent Swarm** | Specialized agents (`Coordinator`, `Planner`, `Research`, `Browser`, `Desktop`, `Coding`, `Memory`, `Vision`, `Voice`, `Verifier`) linked via inter-agent message bus & consensus voting. |
| **🗺️ DAG Task Planner** | Natural language intent decomposer using Kahn's topological sorting algorithm for parallel task batching and priority recovery. |
| **🔄 Workflow Microkernel** | 12-State execution machine (`CREATED` ➔ `RUNNING` ➔ `COMPLETED`) with automated step-by-step saga rollback compensation on error. |
| **🤖 7-Stage LLM Router** | Smart pipeline (Health ➔ Capability ➔ Cost ➔ Priority ➔ Dispatch ➔ Retry ➔ Fallback) across OpenAI, Gemini, Claude, and MockProvider. |
| **🧠 Vector Memory Store** | Multi-tier episodic and semantic storage backed by ChromaDB vector embeddings and multi-factor relevance ranking. |
| **🌐 Browser Automation** | Playwright async engine supporting Chromium/Firefox, element interaction, tab management, screenshots, and human safety approval. |
| **🖥️ OS Desktop Engine** | Windows High-DPI scaling process manager, window handle tracking, desktop input queues, and Tesseract OCR. |
| **👁️ Vision & Voice AI** | Speech-to-Text (STT), Text-to-Speech (TTS), Voice Activity Detection (VAD), visual bounding box detection, and UI clickability scoring. |
| **🔒 Enterprise Security** | JWT HS256 authentication, Bcrypt password hashing, administrator RBAC routes, and encrypted secret key vault storage. |

---

## 🐝 10 Specialized Swarm Agents

1. **👑 Coordinator Agent**: Manages top-level goal distribution and swarm task synchronization.
2. **🗺️ Planner Agent**: Decomposes complex instructions into Directed Acyclic Graphs (DAG).
3. **🔎 Research Agent**: Scrapes web docs, extracts knowledge items, and summarizes technical specs.
4. **🌐 Browser Agent**: Executes headless Playwright automation (form input, web navigation, downloads).
5. **🖥️ Desktop Agent**: Interacts with native OS desktop windows, OCR text recognition, and mouse/keyboard events.
6. **💻 Coding Agent**: Autonomous software engineering, AST analysis, and automated code generation.
7. **🧠 Memory Agent**: Stores, retrieves, and compresses short-term and long-term vector context.
8. **👁️ Vision Agent**: UI component bounding box parser and visual layout clickability scoring.
9. **🎙️ Voice Agent**: Handles STT speech recognition, TTS voice synthesis, and speaker profiling.
10. **🛡️ Verifier Agent**: Quality gate gatekeeper verifying execution outputs against acceptance criteria.

---

## 📁 Repository Directory Structure

```text
JARVIS AI Operating System/
├── backend/                  # FastAPI Application Kernel
│   ├── alembic/              # Database schema migrations
│   ├── app/
│   │   ├── ai/               # 7-stage LLM router, provider SDKs, prompts
│   │   ├── api/              # 16 v1 REST API endpoint routers & deps
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
- **Docker & Docker Compose** (Optional)

---

### 1️⃣ Start the Backend API Server

```powershell
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1   # On Windows
source venv/bin/activate       # On Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
> 🟢 **Backend Swagger API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### 2️⃣ Start the Frontend Dashboard UI

Open a **new terminal window**:

```powershell
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
> 🟢 **Web Dashboard**: [http://localhost:3000](http://localhost:3000)

---

### 3️⃣ Containerized Launch (Docker Compose)

```powershell
# Build and launch PostgreSQL + Backend + Nginx Frontend
docker-compose up --build -d
```

---

## 🔐 Default Administrator Login

| Parameter | Value |
| :--- | :--- |
| **Email** | `admin@jarvis.ai` |
| **Password** | `admin12345` |
| **API Base URL** | `http://localhost:8000/api/v1` |

---

## 🧪 Testing & Quality Assurance

Run the complete Pytest suite (174 unit and integration tests passing):

```powershell
cd backend
pytest tests/ -v
```

---

## 🔄 CI/CD Pipeline

The repository includes an optimized GitHub Actions matrix pipeline (`.github/workflows/ci.yml`):
- **Backend Job**: Python 3.11, PostgreSQL service container, Ruff linting, Pytest execution with coverage.
- **Frontend Job**: Node.js 20, dependency caching, TypeScript compilation, and production Vite build.

---

## 👤 Author & Maintainer

Developed and maintained exclusively by:
- **Mallikarjun Gala** ([@mallikarjun086](https://github.com/mallikarjun086))

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for details.