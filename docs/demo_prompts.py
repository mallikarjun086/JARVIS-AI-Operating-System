"""
JARVIS AI OS — Demo Sample Prompts & Scripted Demo Data
Use these to demonstrate capabilities to recruiters, stakeholders, and users.
"""

DEMO_PROMPTS = {
    "Code Generation": [
        "Build a production-ready FastAPI microservice for user order management with PostgreSQL, JWT auth, and rate limiting",
        "Create a Python class that implements a rate limiter using Redis with sliding window algorithm",
        "Write a React TypeScript component for a data visualization dashboard with real-time WebSocket updates",
        "Generate a Docker multi-stage build file for a Python FastAPI app optimized for production",
        "Implement a job queue system with retry logic, dead-letter queue, and monitoring hooks",
    ],
    "Research & Analysis": [
        "Research the latest advancements in AI agent frameworks — compare AutoGPT, LangGraph, CrewAI, and MetaGPT",
        "Summarize the key differences between RAG and fine-tuning for LLM customization",
        "Analyze the architecture of GPT-4o and explain how multimodal reasoning works",
        "What are the best practices for securing FastAPI applications in production?",
        "Compare PostgreSQL vs MongoDB for an AI application with vector similarity search needs",
    ],
    "Browser Automation": [
        "Open Chrome, navigate to GitHub.com, search for 'FastAPI repositories', and summarize the top 5 results",
        "Go to news.ycombinator.com and give me the top 10 headlines with their scores",
        "Navigate to the Python documentation and find the asyncio event loop lifecycle explanation",
        "Take a screenshot of localhost:8000/docs and describe what you see",
    ],
    "Desktop Automation": [
        "Open Notepad and type a professional email to a client about project delivery timeline",
        "Launch VS Code and create a new Python file named 'hello_jarvis.py'",
        "Take a screenshot of the current desktop and describe all visible applications",
        "Open File Explorer and navigate to the Downloads folder",
    ],
    "File & Git Operations": [
        "Create a new git branch called 'feature/user-authentication' and switch to it",
        "Scan my Python project for unused imports and dead code",
        "Generate a .gitignore file optimized for a Python FastAPI + React TypeScript monorepo",
        "Analyze the git log for this week and create a progress summary",
    ],
    "Memory & Knowledge": [
        "What do you remember about our previous conversations today?",
        "Store the fact that the production database is hosted on AWS RDS us-east-1",
        "Recall all tasks we discussed related to the JARVIS project",
        "Search memory for anything related to authentication implementation",
    ],
    "High-Risk Commands (Approval Required)": [
        "Delete all temporary files in /tmp directory",
        "Restart the backend service on production server",
        "Drop and recreate the test database schema",
    ],
}

DEMO_SCRIPT = """
JARVIS AI OS — 3-Minute Recruiter Demo Script
=============================================

[MINUTE 0:00 - 0:30] INTRODUCTION
-----------------------------------
"This is JARVIS AI OS — a production-ready autonomous AI Operating System I built
from scratch. It's a single interface where you can speak or type any complex goal
and JARVIS automatically orchestrates an entire AI agent swarm to execute it."

[MINUTE 0:30 - 1:30] JARVIS COMMAND CENTER DEMO
-------------------------------------------------
1. Open http://localhost:3000/jarvis-command-center
2. Show the interface: "Notice the voice microphone, live execution panel,
   and the status showing all 8 subsystems online."
3. Click Mic → Speak: "Build a microservice REST API for processing user orders"
4. Watch real-time execution: MEMORY → PLANNER → CODING → VERIFIER
5. Show the generated Python/FastAPI code artifact
6. "JARVIS spoke the response and showed the complete working code."

[MINUTE 1:30 - 2:00] COMMAND PALETTE & NAVIGATION
---------------------------------------------------
1. Press Ctrl+K
2. Type "memory" → navigate to Memory Console
3. "This is the ChromaDB vector memory system — semantic search over 1000+ stored facts"
4. Show memory search working

[MINUTE 2:00 - 2:30] APPROVAL GATE SAFETY DEMO
-----------------------------------------------
1. Return to Command Center
2. Type: "Delete database table and shutdown server"
3. "JARVIS classified this as CRITICAL risk — it requires operator authorization"
4. Show the approval modal → Click Reject
5. "Built-in safety: no destructive action executes without explicit operator approval"

[MINUTE 2:30 - 3:00] TECHNICAL ARCHITECTURE
--------------------------------------------
1. Open http://localhost:8000/docs
2. "35 API endpoints across 19 service modules — all documented with OpenAPI"
3. Show /api/v1/jarvis/execute in the docs
4. "180+ passing tests, Docker + Kubernetes ready, GitHub Actions CI/CD"
5. "Full security hardening: JWT + RBAC + Security Headers + Audit Logging"
"""

ARCHITECTURE_HIGHLIGHTS = {
    "Backend": {
        "Framework": "FastAPI 0.115 (async)",
        "Database": "PostgreSQL 16 + Alembic (SQLite fallback for dev)",
        "Cache": "Redis 7 (session + event queue)",
        "AI Routing": "Multi-provider: OpenAI / Anthropic / Gemini / Mock",
        "Memory": "ChromaDB vector store + Sentence Transformers",
        "Security": "JWT HS256 + RBAC + Security Headers + Rate Limiting",
        "Logging": "structlog (structured JSON)",
        "Testing": "pytest + pytest-asyncio (180+ tests)",
        "Deploy": "Docker + Kubernetes + Helm",
    },
    "Frontend": {
        "Framework": "React 18 + TypeScript 5 + Vite",
        "Styling": "Vanilla CSS (design system: glassmorphism + dark mode)",
        "Routing": "React Router v6",
        "State": "React Context (Auth + Toast + Command Palette)",
        "Voice": "Web Speech API (STT + TTS, browser-native)",
        "Build": "Vite + Nginx Docker",
        "Pages": "18 console pages across all JARVIS subsystems",
    },
    "AI Capabilities": {
        "Orchestration": "4-step pipeline: Memory → Planner → Agent → Verifier",
        "Agents": "10-agent swarm: Coordinator, Planner, Researcher, Coder, Browser, Desktop, Memory, Verifier, Voice, Security",
        "Tools": "35 registered tools: browser, desktop, git, file, web, shell, search",
        "Memory": "ChromaDB RAG with semantic similarity retrieval",
        "Planning": "DAG-based task decomposition with topological ordering",
        "Safety": "RBAC + approval gates + command injection protection",
    },
}
