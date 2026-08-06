"""
Enterprise System Integration & Regression Test Suite (Sprint 7.5).
Validates end-to-end communication across all 7 core subsystems: Security, AI Providers, Memory, Tool Framework, Planner, Browser, and Desktop.
"""

import asyncio
from httpx import AsyncClient
import pytest

from app.core.event_bus import SystemEvent, event_bus
from app.core.exceptions import (
    BrowserException,
    DesktopException,
    MemoryException,
    PlannerException,
    SecurityException,
    ToolExecutionException,
)
from app.core.health_manager import global_health_manager
from app.core.telemetry import system_telemetry


@pytest.mark.asyncio
async def test_global_health_manager_all_subsystems():
    """Phase 4: Verifies GlobalHealthManager aggregates all 7 core subsystems."""
    summary = await global_health_manager.get_summary_health()
    assert summary["status"] in ["HEALTHY", "DEGRADED"]
    assert summary["healthy_subsystems_count"] >= 5
    assert summary["total_subsystems_count"] >= 7

    full = await global_health_manager.get_full_health()
    assert "subsystems" in full
    subsystems = full["subsystems"]
    assert "security" in subsystems
    assert "ai_providers" in subsystems
    assert "memory" in subsystems
    assert "tools" in subsystems
    assert "planner" in subsystems
    assert "browser" in subsystems
    assert "desktop" in subsystems


@pytest.mark.asyncio
async def test_internal_async_event_bus():
    """Phase 10: Verifies EventBus pub/sub dispatching and event history."""
    received_events = []

    async def sample_handler(evt: SystemEvent):
        received_events.append(evt)

    event_bus.subscribe("PlannerStepCompleted", sample_handler)

    test_event = SystemEvent(
        event_type="PlannerStepCompleted",
        source_subsystem="planner",
        payload={"step": 1, "action": "browser_navigate"}
    )
    await event_bus.publish(test_event)

    assert len(received_events) == 1
    assert received_events[0].payload["action"] == "browser_navigate"

    history = event_bus.get_event_history(limit=10)
    assert len(history) >= 1
    assert history[-1]["event_type"] == "PlannerStepCompleted"


@pytest.mark.asyncio
async def test_unified_telemetry_collector():
    """Phase 9: Verifies SystemTelemetryManager metric collection and success rate."""
    system_telemetry.record_planner_execution(latency_ms=120.0, success=True)
    system_telemetry.record_memory_operation(is_store=False, latency_ms=15.0)
    system_telemetry.record_tool_execution(latency_ms=45.0, success=True)
    system_telemetry.record_browser_operation(latency_ms=350.0)
    system_telemetry.record_desktop_operation(latency_ms=85.0)
    system_telemetry.record_llm_call(latency_ms=450.0)
    system_telemetry.record_recovery()

    t_dict = system_telemetry.to_dict()
    assert t_dict["uptime_seconds"] >= 0.0
    assert t_dict["overall_success_rate"] == 100.0
    assert t_dict["counts"]["planner_plans_executed"] >= 1
    assert t_dict["counts"]["total_recoveries"] >= 1
    assert t_dict["avg_latencies_ms"]["planner"] > 0.0


@pytest.mark.asyncio
async def test_unified_exception_hierarchy():
    """Phase 12: Verifies standardized exception serialization and error codes."""
    sec_exc = SecurityException("Unauthorized sandbox execution", details={"user": "test_user"})
    assert sec_exc.error_code == "SECURITY_VIOLATION"
    assert sec_exc.is_recoverable is False
    assert sec_exc.to_dict()["details"]["user"] == "test_user"

    tool_exc = ToolExecutionException("Tool execution timed out", tool_name="browser_navigate")
    assert tool_exc.error_code == "TOOL_EXECUTION_FAILED"
    assert tool_exc.is_recoverable is True
    assert tool_exc.to_dict()["details"]["tool_name"] == "browser_navigate"


@pytest.mark.asyncio
async def test_end_to_end_planner_tool_subsystem_integration():
    """Phase 5 & 7: Verifies Planner -> Tool Framework -> Browser/Desktop -> Memory integration."""
    from app.planner.planner import task_planner
    from app.tools.registry import tool_registry
    from app.desktop.manager import desktop_manager
    from app.browser.manager import browser_manager

    # 1. Verify Tools discovered in Tool Registry
    tools = tool_registry.list_tools()
    assert len(tools) >= 5

    # 2. Verify Planner active plans
    plan = task_planner.create_plan(title="End-to-End System Test", goal="Verify unified orchestration")
    assert plan.plan_id is not None
    assert plan.status.value in ["PENDING", "IN_PROGRESS", "COMPLETED", "PLANNED", "RUNNING", "CREATED"]


    # 3. Verify Browser Engine instance
    brw_health = await browser_manager.get_health_status()
    assert "initialized" in brw_health

    # 4. Verify Desktop Engine instance
    dsk_health = await desktop_manager.get_health_status()
    assert "initialized" in dsk_health


@pytest.mark.asyncio
async def test_health_rest_api_endpoints(client: AsyncClient):
    """Phase 4 & REST Validation: Verifies GET /api/v1/health and GET /api/v1/health/full."""
    # Summary Health Endpoint
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "healthy_subsystems_count" in data

    # Full Health Diagnostic Endpoint
    full_resp = await client.get("/api/v1/health/full")
    assert full_resp.status_code == 200
    full_data = full_resp.json()
    assert "subsystems" in full_data
    assert "security" in full_data["subsystems"]
    assert "ai_providers" in full_data["subsystems"]
    assert "memory" in full_data["subsystems"]
    assert "tools" in full_data["subsystems"]
    assert "planner" in full_data["subsystems"]
    assert "browser" in full_data["subsystems"]
    assert "desktop" in full_data["subsystems"]

    # Readiness Endpoint
    read_resp = await client.get("/api/v1/health/readiness")
    assert read_resp.status_code == 200
    assert read_resp.json()["status"] == "READY"
