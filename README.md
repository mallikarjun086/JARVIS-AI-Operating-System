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

*Production-Grade Autonomous AI Agent & Operating System Platform*

[![CI Pipeline](https://github.com/mallikarjun086/JARVIS-AI-Operating-System/actions/workflows/ci.yml/badge.svg)](https://github.com/mallikarjun086/JARVIS-AI-Operating-System/actions)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB?logo=react)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?logo=typescript)](https://typescriptlang.org)
[![Tests](https://img.shields.io/badge/Tests-184%20Passed%20(100%25)-brightgreen)](file:///c:/Users/Mallikarjun%20Gala/OneDrive/Desktop/JARVIS%20AI%20Operating%20System/backend/run_all_tests.py)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

</div>

---

## 🌟 Overview

**JARVIS AI OS** is a production-ready, enterprise-grade AI Operating System that turns natural language and voice commands into real, automated desktop, web, system, file, code, and workflow executions.

**One Interface. Infinite Autonomous Capability.**

Type or speak any goal to JARVIS, and it autonomously orchestrates a **10-Agent Swarm Mesh**, **48-Tool Executable Framework**, **ChromaDB Vector Memory RAG**, **Real-Time Voice Intelligence (STT/TTS/VAD/Wake-Word)**, and **Desktop Automation Engine** — featuring live SSE execution streaming, approval gatekeepers, and full system observability.

---

## 🏗️ Architecture Blueprint

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    JARVIS AI OPERATING SYSTEM v1.0                      │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │           UNIFIED MULTIMODAL COMMAND CENTER (HUD & DASHBOARD)    │   │
│  │     Voice STT ←→ Chat Interface ←→ Streaming TTS Audio           │   │
│  │         Command Palette (⌘K) · Real-Time Telemetry Consoles      │   │
│  └─────────────────────────┬───────────────────────────────────────┘   │
│                            │ Voice / Text Command                       │
│                            ▼                                            │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                JARVIS MULTIMODAL ORCHESTRATOR Engine            │   │
│  │  LLM Intent Parse → DAG Task Plan → Swarm Dispatch → Consensus   │   │
│  │              (RBAC Guard · Approval Gates · SSE Stream)          │   │
│  └───┬─────────────┬─────────────┬─────────────┬─────────────┬─────┘   │
│      │             │             │             │             │          │
│      ▼             ▼             ▼             ▼             ▼          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐ │
│  │MEMORY RAG│ │DAG PLNR  │ │CODING SWE│ │RESRCH BWS│ │ 48-TOOL SYSTEM│ │
│  │ChromaDB  │ │Graph     │ │AST Engine│ │Playwright│ │ Filesystem    │ │
│  │Vector    │ │Topology  │ │Patch/Repo│ │Automation│ │ Terminal/Exec │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └───────────────┘ │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                 10-SPECIALIZED AGENT SWARM MESH                 │   │
│  │  Coordinator · Planner · Research · Coder · Browser · Desktop   │   │
│  │  Memory · Verifier · Voice · Security / Vision                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                  INFRASTRUCTURE & CORE ENGINE                   │   │
│  │  FastAPI + Uvicorn · SQLite/PostgreSQL · Redis Session Cache     │   │
│  │  JWT Auth + RBAC · Structured Logger · Prometheus Telemetry      │   │
│  │  Docker Compose + Kubernetes · 184 / 184 Verified Pytest Suite   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start & Installation

### Prerequisites
- **Python 3.11+**
- **Node.js 20+**
- **Git**

### 1. Clone Repository
```powershell
git clone https://github.com/mallikarjun086/JARVIS-AI-Operating-System.git
cd "JARVIS AI Operating System"
```

### 2. Launch Backend API Server
```powershell
cd backend
python -m venv venv
venv\Scripts\activate            # Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Launch Frontend Web Dashboard
```powershell
cd frontend
npm install
npm run dev
# Dashboard opens live on http://localhost:3000
```

### 4. Admin Seeding & Credentials
| Field | Value |
|---|---|
| **Email** | `admin@jarvis.ai` |
| **Password** | `AdminPassword123!` |

---

## ⚡ Comprehensive Feature Matrix

| Subsystem Component | Capability Status | Technical Stack |
|:---|:---:|:---|
| **Multimodal Orchestrator** | ✅ 100% Operational | Real LLM Intent Classifier + DAG Execution |
| **10-Agent Swarm Mesh** | ✅ 100% Operational | Parallel DAG Scheduler + Verifier Consensus |
| **48-Tool System Framework** | ✅ 100% Operational | Sandboxed Execution + Path/Cmd Safety |
| **Voice STT & Audio VAD** | ✅ 100% Operational | `faster-whisper` + 16-bit PCM Energy VAD |
| **Streaming Voice TTS** | ✅ 100% Operational | Thread-Pooled `pyttsx3` + PCM Audio Generator |
| **Wake Word Detection** | ✅ 100% Operational | "Hey JARVIS" / "JARVIS" Phrase Engine |
| **Desktop Automation Engine** | ✅ 100% Operational | `pyautogui` + `pywinauto` + `pyperclip` |
| **Browser Automation Engine** | ✅ 100% Operational | Playwright DOM & Tab Controller |
| **Long-Term Memory RAG** | ✅ 100% Operational | ChromaDB Vector Store + HashEmbedding |
| **Multi-Provider LLM Router** | ✅ 100% Operational | OpenAI / Anthropic / Gemini / Mock Router |
| **Enterprise Security Subsystem** | ✅ 100% Operational | Fernet Secrets Vault + Command Guard |
| **Autonomous Workflow Engine** | ✅ 100% Operational | State Machine + Rollback + Checkpointing |
| **Global Health & Observability** | ✅ 100% Operational | 8-Subsystem Health Manager + Prometheus |
| **Verified Test Suite** | ✅ 184 / 184 Passed | Pytest + pytest-asyncio (100% Pass) |

---

## 🤖 The 10 Specialized Swarm Agents

1. **`CoordinatorAgent`**: Manages swarm execution lifecycle and task delegation.
2. **`PlannerAgent`**: Uses LLM graph reasoning to decompose goals into parallel DAG subtasks.
3. **`ResearchAgent`**: Conducts web research, documentation scraping, and synthesis.
4. **`CoderAgent`**: Executes AST multi-language code generation, patching, and build/test pipelines.
5. **`BrowserAgent`**: Automates web navigation, form handling, cookies, and DOM interaction.
6. **`DesktopAgent`**: Controls native Windows OS windows, mouse/keyboard inputs, and app launching.
7. **`MemoryAgent`**: Manages vector memory retrieval, secret redaction, and episodic persistence.
8. **`VerifierAgent`**: Evaluates task execution outputs against quality acceptance criteria.
9. **`VoiceAgent`**: Handles real-time speech recognition (STT) and voice synthesis (TTS).
10. **`SecurityAgent / VisionAgent`**: Performs command risk evaluation, sandboxed execution, and OCR image reasoning.

---

## 🔑 Key API Reference

| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/api/v1/health` | Global Aggregate Health Summary (8 / 8 Subsystems) |
| `GET` | `/api/v1/health/full` | Deep Subsystem Diagnostics & Latency Reports |
| `POST` | `/api/v1/auth/login` | Authenticate User & Obtain JWT Bearer Token |
| `POST` | `/api/v1/jarvis/command` | Execute Multimodal Orchestrated Goal |
| `GET` | `/api/v1/jarvis/stream` | Real-Time Live Execution SSE Event Stream |
| `POST` | `/api/v1/voice/interact` | End-to-End Voice Loop (STT -> LLM -> Tools -> TTS) |
| `POST` | `/api/v1/voice/detect-wakeword` | Scan Audio/Transcript for "Hey JARVIS" |
| `GET` | `/api/v1/multi-agent/agents` | Enumerate 10 Specialized Swarm Agents |
| `GET` | `/api/v1/tools` | List 48 Executable System Tools |
| `GET` | `/api/v1/metrics` | Prometheus-Compatible System Telemetry Metrics |

Interactive API Documentation: [`http://127.0.0.1:8000/docs`](http://127.0.0.1:8000/docs)

---

## 🧪 Testing & Verification

Run the entire test suite covering all 8 phases:

```powershell
cd backend
python run_all_tests.py
```

Output:
```text
================== 184 passed, 1 warning in 61.48s (0:01:01) ==================
[SUCCESS] ALL UNIT & INTEGRATION TESTS PASSED 100% SUCCESSFULLY!
```

---

## 📁 Repository Directory Map

```text
JARVIS AI Operating System/
├── backend/
│   ├── app/
│   │   ├── ai/              # Multi-Provider LLM Router (OpenAI, Anthropic, Gemini)
│   │   ├── automation/      # Desktop Control & Perception Engine
│   │   ├── browser/         # Playwright Browser Automation Manager
│   │   ├── core/            # Global Health Manager & Event Bus
│   │   ├── desktop/         # PyAutoGUI & PyWinAuto Platform Adapters
│   │   ├── jarvis/          # Multimodal LLM Orchestrator & SSE Engine
│   │   ├── memory/          # ChromaDB Vector Store & Embedding Fallback
│   │   ├── multi_agent/     # 10 Specialized Agents Pool, Coordinator & Consensus
│   │   ├── planner/         # Task DAG Planner & Topological Batch Engine
│   │   ├── security/        # Fernet Vault, Command Guard & Sandbox
│   │   ├── swe_agent/       # AST Parser, Patch Engine & Git Build Manager
│   │   ├── tools/           # 48 Registered Tools Framework (Filesystem, Terminal, Network, etc.)
│   │   ├── vision/          # Computer Vision & OCR Extraction
│   │   ├── voice/           # STT, VAD, Streaming TTS & Wake Word Engine
│   │   └── main.py          # FastAPI Application & Lifespan Service
│   └── tests/               # 184 Verified Pytest Unit & Integration Tests
├── frontend/                # React 18 + Vite + TypeScript Dashboard (Port 3000)
├── k8s/                     # Kubernetes Deployment Manifests
├── docker-compose.yml       # Production Container Stack
└── README.md                # Project Architecture & Documentation
```

---

## 📄 License

MIT License — Copyright (c) 2026 **Mallikarjun Gala**

---

<div align="center">
  <strong>Built with ❤️ by Mallikarjun Gala</strong><br>
  <a href="https://github.com/mallikarjun086">GitHub</a> ·
  <a href="http://127.0.0.1:8000/docs">API Specs</a>
</div>