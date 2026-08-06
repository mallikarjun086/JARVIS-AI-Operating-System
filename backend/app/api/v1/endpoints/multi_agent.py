"""
FastAPI Endpoints for Enterprise Multi-Agent Orchestration Platform (Sprint 9).
Endpoints: /agents, /agents/{id}, /agents/health, /agents/capabilities, /agents/register, /agents/unregister, /agents/execute, /agents/workflow, /agents/workflows, /agents/metrics, /agents/events.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.api.deps import get_current_user
from app.core.event_bus import event_bus
from app.models.user import User
from app.multi_agent.capability_graph import capability_graph
from app.multi_agent.context import shared_context_builder
from app.multi_agent.message_bus import message_bus
from app.multi_agent.orchestrator import swarm_orchestrator
from app.multi_agent.registry import agent_registry
from app.multi_agent.schemas import (
    AgentMetadata,
    AgentMessage,
    AgentRole,
    AgentTaskTelemetry,
    SubTaskSpec,
    SwarmExecutionPlan,
)
from app.multi_agent.shared_memory import shared_swarm_memory

router = APIRouter()


@router.get("/agents", response_model=List[AgentMetadata], summary="List Registered Specialized Agents")
async def list_agents(
    current_user: User = Depends(get_current_user)
) -> List[AgentMetadata]:
    """Lists metadata of all registered specialized agents in the platform."""
    return agent_registry.list_agents()


@router.get("/agents/health", summary="Subsystem Multi-Agent Health Diagnostic")
async def get_multi_agent_health(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Returns detailed health diagnostics for all registered specialized agents."""
    return await agent_registry.get_all_health()


@router.get("/agents/capabilities", summary="Query CapabilityGraph Mappings")
async def get_capabilities_mapping(
    current_user: User = Depends(get_current_user)
) -> Dict[str, List[str]]:
    """Returns mapping of capabilities to supporting agent IDs."""
    return capability_graph.get_capability_mapping()


@router.get("/agents/metrics", response_model=List[AgentTaskTelemetry], summary="Get Agent Telemetry Metrics")
@router.get("/telemetry", response_model=List[AgentTaskTelemetry], summary="Get Agent Telemetry (Backward Compatible)")
async def get_agent_metrics(
    current_user: User = Depends(get_current_user)
) -> List[AgentTaskTelemetry]:
    """Returns live performance metrics for all registered agents."""
    return swarm_orchestrator.get_agent_telemetry()


@router.get("/agents/{agent_id}", response_model=AgentMetadata, summary="Get Agent Metadata by ID")
async def get_agent_by_id(
    agent_id: str,
    current_user: User = Depends(get_current_user)
) -> AgentMetadata:
    """Retrieves agent metadata descriptor by agent ID."""
    agent = agent_registry.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Agent '{agent_id}' not found.")
    return agent.metadata



@router.post("/agents/workflow", response_model=SwarmExecutionPlan, summary="Execute Multi-Agent Swarm Workflow")
@router.post("/dispatch", response_model=SwarmExecutionPlan, summary="Dispatch Swarm Goal (Backward Compatible)")
async def execute_swarm_workflow(
    goal: str = Query(..., description="High-level natural language goal"),
    current_user: User = Depends(get_current_user)
) -> SwarmExecutionPlan:
    """Dispatches multi-agent workflow goal across specialized agents."""
    return await swarm_orchestrator.dispatch_swarm_goal(goal)


@router.post("/agents/execute", summary="Execute Single Agent Task")
async def execute_agent_task(
    goal: str = Query(..., description="Subtask goal description"),
    capability: str = Query(default="general_processing", description="Required capability"),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Executes single subtask by selecting agent dynamically via CapabilityGraph."""
    agent = capability_graph.select_agent_for_capability(capability)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No agent found for capability '{capability}'.")

    subtask = SubTaskSpec(goal=goal, required_capability=capability)
    ctx = shared_context_builder.build_context()
    executed = await agent.execute(subtask, ctx)
    return executed.model_dump()


@router.get("/agents/workflows", response_model=List[SwarmExecutionPlan], summary="List Swarm Workflows")
async def list_swarm_workflows(
    current_user: User = Depends(get_current_user)
) -> List[SwarmExecutionPlan]:
    """Lists active and past swarm execution plans."""
    return swarm_orchestrator.list_plans()


@router.get("/status/{plan_id}", response_model=SwarmExecutionPlan, summary="Poll Swarm Plan Status")
async def get_plan_status(
    plan_id: str,
    current_user: User = Depends(get_current_user)
) -> SwarmExecutionPlan:
    """Polls execution plan status by ID."""
    plan = swarm_orchestrator.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Execution plan '{plan_id}' not found.")
    return plan



@router.get("/agents/events", summary="Get Inter-Agent Event Log")
@router.get("/messages", summary="Get Inter-Agent Message Log (Backward Compatible)")
async def list_agent_events(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Retrieves inter-agent communication messages and event bus audit trail."""
    return {
        "messages": [m.model_dump() for m in message_bus.list_all_messages()],
        "event_bus_history": event_bus.get_event_history(limit=50)
    }


@router.get("/shared-memory", summary="Get Shared Swarm Memory Workspace")
async def get_shared_memory(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Returns current shared swarm memory workspace context."""
    return shared_swarm_memory.get_all_context()
