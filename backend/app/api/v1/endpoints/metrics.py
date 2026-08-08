"""
JARVIS AI OS — Prometheus-Compatible Metrics Endpoint.
Exposes system health and performance counters in Prometheus text format.
"""
from typing import Any, Dict
import time
from fastapi import APIRouter

router = APIRouter()

# In-memory counters (per-process; use Redis for multi-instance)
_start_time = time.time()
_counters: Dict[str, Any] = {
    "requests_total": 0,
    "jarvis_executions_total": 0,
    "agent_tasks_total": 0,
    "llm_completions_total": 0,
    "errors_total": 0,
}


def increment(key: str, amount: int = 1) -> None:
    _counters[key] = _counters.get(key, 0) + amount


@router.get("/metrics", tags=["Observability"], summary="Prometheus-compatible metrics endpoint")
async def prometheus_metrics() -> str:
    """
    Exposes key JARVIS AI OS metrics in Prometheus text format.
    """
    uptime_seconds = time.time() - _start_time

    # Collect live metrics from sub-systems
    try:
        from app.ai.router import llm_router
        llm_metrics = llm_router.get_metrics()
        total_completions = llm_metrics.get("total_requests", 0)
        total_errors = llm_metrics.get("total_errors", 0)
        avg_latency = llm_metrics.get("avg_latency_ms", 0.0)
    except Exception:
        total_completions, total_errors, avg_latency = 0, 0, 0.0

    try:
        from app.tools.registry import tool_registry
        tool_count = len(tool_registry.list_tools())
    except Exception:
        tool_count = 0

    lines = [
        "# HELP jarvis_uptime_seconds Total uptime in seconds",
        "# TYPE jarvis_uptime_seconds gauge",
        f"jarvis_uptime_seconds {uptime_seconds:.2f}",
        "",
        "# HELP jarvis_llm_completions_total Total LLM completion calls",
        "# TYPE jarvis_llm_completions_total counter",
        f"jarvis_llm_completions_total {total_completions}",
        "",
        "# HELP jarvis_llm_errors_total Total LLM error count",
        "# TYPE jarvis_llm_errors_total counter",
        f"jarvis_llm_errors_total {total_errors}",
        "",
        "# HELP jarvis_llm_avg_latency_ms Average LLM response latency in milliseconds",
        "# TYPE jarvis_llm_avg_latency_ms gauge",
        f"jarvis_llm_avg_latency_ms {avg_latency:.2f}",
        "",
        "# HELP jarvis_registered_tools_total Total registered tool count",
        "# TYPE jarvis_registered_tools_total gauge",
        f"jarvis_registered_tools_total {tool_count}",
        "",
        "# HELP jarvis_info JARVIS AI OS build info",
        "# TYPE jarvis_info gauge",
        'jarvis_info{version="1.0.0",env="' + "production" + '"} 1',
    ]
    return "\n".join(lines)


@router.get("/health", tags=["System Health"], summary="Health check endpoint")
async def health_check() -> Dict[str, Any]:
    """Basic liveness probe endpoint."""
    return {"status": "healthy", "service": "JARVIS AI OS", "version": "1.0.0"}


@router.get("/readiness", tags=["System Health"], summary="Readiness probe endpoint")
async def readiness_check() -> Dict[str, Any]:
    """Readiness probe checking all critical subsystems."""
    checks: Dict[str, str] = {}

    try:
        from app.db.session import async_session_factory
        async with async_session_factory() as db:
            await db.execute(__import__("sqlalchemy", fromlist=["text"]).text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {str(e)[:80]}"

    try:
        from app.ai.router import llm_router
        checks["llm_router"] = "ok"
    except Exception as e:
        checks["llm_router"] = f"error: {str(e)[:80]}"

    all_ok = all(v == "ok" for v in checks.values())
    return {
        "status": "ready" if all_ok else "degraded",
        "checks": checks,
        "version": "1.0.0"
    }
