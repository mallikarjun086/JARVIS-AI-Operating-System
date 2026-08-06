# JARVIS AI Operating System (JARVIS-AI-OS) - Architecture Specification

## Overview

JARVIS-AI-OS is an enterprise-grade autonomous multi-agent operating system kernel built following **Clean Architecture (Hexagonal Architecture)** and **SOLID Principles**.

---

## Clean Architecture Layers

```
                      +------------------------------------------+
                      |         Presentation & API Layer          |
                      |   (FastAPI REST/WS, Typer CLI Controllers)|
                      +--------------------+---------------------+
                                           |
                                           v
                      +--------------------+---------------------+
                      |         Application Use Cases            |
                      | (Task Workflow, Agent Orchestration,     |
                      |  Memory Retrieval, System Scheduling)    |
                      +--------------------+---------------------+
                                           |
                                           v
                      +--------------------+---------------------+
                      |             Domain Core                  |
                      | (Agent Entities, Task Kernel, Scheduler, |
                      |  Memory Contracts, Security Rules, Tools)|
                      +--------------------+---------------------+
                                           ^
                                           |
                      +--------------------+---------------------+
                      |        Infrastructure & Adapters         |
                      | (LLM Gateway, FAISS/NumPy Vector Store,  |
                      |  Async Priority Queue, Structlog Engine) |
                      +------------------------------------------+
```

### 1. Domain Core (`jarvis.domain`)
- **Pure Entities**: `AgentProcess`, `TaskContext`, `MemoryRecord`, `ToolDefinition`, `ToolResult`, `KernelMetrics`.
- **Value Objects**: `ProcessStatus`, `TaskPriority`, `ToolPermission`, `MemoryType`.
- **Ports (Interfaces)**: `LLMProviderPort`, `VectorStorePort`, `ProcessSchedulerPort`, `ToolRegistryPort`, `SecuritySandboxPort`, `TaskRepositoryPort`.
- **Exceptions**: `JARVISError`, `ProcessNotFoundError`, `SecurityViolationError`, `LLMProviderError`, `TaskExecutionError`.

### 2. Application Layer (`jarvis.application`)
- **Use Cases**: `CreateAgentProcessUseCase`, `GetAgentProcessUseCase`, `ExecuteTaskUseCase`, `AddMemoryUseCase`, `SearchMemoryUseCase`, `ExecuteToolUseCase`.
- **DTOs**: Validated request and response payload schemas.

### 3. Infrastructure Layer (`jarvis.infrastructure`)
- **LLM Gateway**: Multi-provider async HTTP client with exponential retries and deterministic offline fallback engine.
- **Vector Memory Store**: NumPy-accelerated cosine similarity search engine with disk persistence.
- **Process Scheduler**: Async `PriorityQueue` execution engine with configurable concurrency pools.
- **Security Sandbox**: Workspace root containment and shell command whitelisting guard.
- **Persistence**: Async SQLAlchemy ORM and SQLite session manager.
- **Logging**: Structlog JSON formatter with correlation IDs.

### 4. Presentation Layer (`jarvis.presentation`)
- **FastAPI Server**: OpenAPI 3.1 REST endpoints and WebSocket telemetry stream.
- **Typer CLI**: Command-line control interface (`jarvis start`, `jarvis process submit`, `jarvis memory search`).

---

## Security Model

1. **Path Boundary Validation**: All file operations resolve relative to `WORKSPACE_ROOT` and verify parent hierarchy, preventing path traversal attacks.
2. **Command Execution Whitelisting**: Shell execution requires explicit privilege enablement (`ALLOW_SHELL_EXECUTION=True`) and strictly validates commands against safe command prefixes while blocking dangerous regex patterns.
3. **Privilege Scoping**: Every tool defines a required privilege (`READ_ONLY`, `FILE_WRITE`, `SYSTEM_EXECUTE`, `NETWORK_ACCESS`), which is checked prior to execution against agent process permissions.
