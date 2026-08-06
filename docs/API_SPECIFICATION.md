# JARVIS AI Operating System - API Specification

Base URI: `http://localhost:8000/api/v1`

---

## 1. System Health & Metrics

### `GET /api/v1/health`
Returns system health status overview.

**Response `200 OK`**:
```json
{
  "status": "HEALTHY",
  "app_name": "JARVIS AI Operating System",
  "version": "1.0.0",
  "active_processes": 0,
  "total_processes": 5,
  "uptime_seconds": 124.5,
  "environment": "development"
}
```

### `GET /api/v1/metrics`
Returns detailed kernel telemetry.

---

## 2. Agent Process Management

### `POST /api/v1/processes`
Submits and schedules a new autonomous agent process.

**Request Body**:
```json
{
  "agent_name": "DevAgent",
  "role": "Autonomous Software Engineer",
  "goal": "Write a python script",
  "priority": 2,
  "max_steps": 10,
  "permissions": ["READ_ONLY", "FILE_WRITE"]
}
```

### `GET /api/v1/processes`
Lists all active and completed processes.

### `GET /api/v1/processes/{process_id}`
Retrieves details and execution history of a specific process.

### `DELETE /api/v1/processes/{process_id}`
Cancels a queued or running process.

---

## 3. Vector Memory Store

### `POST /api/v1/memory`
Embeds and indexes a new memory record.

### `POST /api/v1/memory/search`
Searches top-k relevant memory entries by vector similarity.

---

## 4. Tools & Capabilities

### `GET /api/v1/tools`
Lists all registered executable system capabilities.

### `POST /api/v1/tools/execute`
Executes a system tool directly with permission checking.

---

## 5. WebSocket Telemetry Stream

### `WS /ws/telemetry`
Real-time telemetry stream broadcasting kernel execution events and active metrics updates.
