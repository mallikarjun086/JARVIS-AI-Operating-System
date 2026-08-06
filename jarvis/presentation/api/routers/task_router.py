"""
API Router for Tool Discovery & Execution.
"""

from typing import List
from fastapi import APIRouter, Request
from jarvis.application.dto import ExecuteToolRequest
from jarvis.application.use_cases.tool_use_cases import ExecuteToolUseCase, ListToolsUseCase
from jarvis.domain.entities import ToolDefinition, ToolResult

router = APIRouter(prefix="/api/v1/tools", tags=["Tools & Capabilities"])


@router.get("", response_model=List[ToolDefinition], summary="List Registered Tools")
async def list_tools(request: Request) -> List[ToolDefinition]:
    """Lists all executable capabilities registered in the AI OS kernel."""
    tool_registry = request.app.state.tool_registry
    use_case = ListToolsUseCase(tool_registry=tool_registry)
    return use_case.execute()


@router.post("/execute", response_model=ToolResult, summary="Execute System Tool")
async def execute_tool(req: ExecuteToolRequest, request: Request) -> ToolResult:
    """Executes a system tool directly with permission validation."""
    tool_registry = request.app.state.tool_registry
    use_case = ExecuteToolUseCase(tool_registry=tool_registry)
    return await use_case.execute(req)
