"""
Workflow Tools Category (WorkflowTriggerTool).
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from app.tools.base import BaseTool
from app.tools.schemas import PermissionLevel


class WorkflowTriggerInput(BaseModel):
    workflow_name: str = Field(..., description="Target workflow to trigger")
    input_data: Dict[str, Any] = Field(default_factory=dict)

class WorkflowTriggerOutput(BaseModel):
    workflow_id: str
    workflow_name: str
    status: str


class WorkflowTriggerTool(BaseTool):
    @property
    def name(self) -> str: return "workflow.trigger"
    @property
    def description(self) -> str: return "Triggers an automated workflow execution graph."
    @property
    def category(self) -> str: return "workflow"
    @property
    def permission_level(self) -> PermissionLevel: return PermissionLevel.WRITE
    @property
    def input_schema(self): return WorkflowTriggerInput
    @property
    def output_schema(self): return WorkflowTriggerOutput

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        import uuid
        return {
            "workflow_id": str(uuid.uuid4()),
            "workflow_name": params["workflow_name"],
            "status": "TRIGGERED"
        }
