"""
FastAPI Endpoints for Enterprise Tool Framework.
Endpoints: GET /tools, GET /tools/categories, GET /tools/health, GET /tools/metrics, GET /tools/{name}, POST /tools/execute, POST /tools/execute-parallel, POST /tools/hot-reload.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_user
from app.models.user import User
from app.tools.executor import execution_manager
from app.tools.metrics import tool_metrics
from app.tools.registry import tool_registry
from app.tools.schemas import (
    ParallelToolRequest,
    ToolExecutionRequest,
    ToolExecutionResult,
    ToolHealthReport,
    ToolMetadata,
)

router = APIRouter()


@router.get("", response_model=List[ToolMetadata], summary="List Registered Tools")
async def list_tools(
    category: Optional[str] = Query(default=None, description="Optional category filter"),
    current_user: User = Depends(get_current_user)
) -> List[ToolMetadata]:
    """Lists metadata and schemas for registered tools."""
    return tool_registry.list_tools(category=category)


@router.get("/categories", response_model=List[str], summary="List Tool Categories")
async def list_categories(
    current_user: User = Depends(get_current_user)
) -> List[str]:
    """Lists all registered tool category namespaces."""
    return tool_registry.get_categories()


@router.get("/health", response_model=List[ToolHealthReport], summary="Check Tool Health")
async def check_tools_health(
    current_user: User = Depends(get_current_user)
) -> List[ToolHealthReport]:
    """Executes diagnostic health checks on all registered tools."""
    return await tool_registry.check_all_health()


@router.get("/metrics", response_model=Dict[str, Any], summary="Get Tool Execution Metrics")
async def get_tool_metrics(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Returns real-time tool execution metrics, success/failure rates, and runtimes."""
    return tool_metrics.to_dict(
        registered_tools_count=tool_registry.registered_count,
        active_tools_count=tool_registry.active_count
    )


@router.post("/execute", response_model=ToolExecutionResult, summary="Execute Single Tool Call")
async def execute_tool(
    req: ToolExecutionRequest,
    current_user: User = Depends(get_current_user)
) -> ToolExecutionResult:
    """
    Executes a tool call enforcing permissions, schema validation,
    timeouts, exponential retries, and audit logging.
    """
    user_role = "superuser" if current_user.is_superuser else "user"
    return await execution_manager.execute_tool(
        req,
        context={"user": current_user},
        user_role=user_role,
        user_id=current_user.id
    )


@router.post("/execute-parallel", response_model=List[ToolExecutionResult], summary="Execute Parallel Tool Batch")
async def execute_parallel_tools(
    req: ParallelToolRequest,
    current_user: User = Depends(get_current_user)
) -> List[ToolExecutionResult]:
    """Executes a batch of tool requests concurrently in parallel."""
    user_role = "superuser" if current_user.is_superuser else "user"
    return await execution_manager.execute_parallel(
        req.requests,
        context={"user": current_user},
        user_role=user_role,
        user_id=current_user.id
    )


@router.post("/hot-reload", summary="Hot Reload Tool Categories")
async def hot_reload_tools(
    current_user: User = Depends(get_current_user)
):
    """Hot-reloads modified tool modules at runtime."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Superuser privilege required.")
    count = tool_registry.hot_reload()
    return {"message": f"Hot reload complete. Discovered {count} tools."}


@router.get("/{name}", response_model=ToolMetadata, summary="Get Specific Tool Metadata")
async def get_tool(
    name: str,
    current_user: User = Depends(get_current_user)
) -> ToolMetadata:
    """Fetches input/output schemas and metadata for a specific tool."""
    tool = tool_registry.get_tool(name)
    if not tool:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tool '{name}' not found.")
    return tool.get_metadata()
