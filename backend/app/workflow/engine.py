"""
Microkernel Enterprise Workflow Engine (Sprint 10).
Orchestrates Event Sourcing, 12-State Runtime, Persistent Checkpoints, Saga Compensation, Versioning, and Resource Allocation.
Does NOT reason about goals, select agents, or execute tools directly.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.workflow.checkpoint import checkpoint_engine
from app.workflow.event_sourcing import event_sourcing_engine
from app.workflow.library import workflow_library
from app.workflow.policy_engine import workflow_policy_engine
from app.workflow.resource_manager import resource_reservation_manager
from app.workflow.runtime import workflow_runtime
from app.workflow.schemas import (
    WorkflowDefinition,
    WorkflowEventType,
    WorkflowInstance,
    WorkflowStatus,
)
from app.workflow.templates import get_all_enterprise_templates
from app.workflow.versioning import workflow_versioning_engine

logger = structlog.get_logger(__name__)


class WorkflowEngine:
    """Microkernel Workflow Engine Kernel."""

    def __init__(self) -> None:
        self._instances: Dict[str, WorkflowInstance] = {}

        # Register all 8 enterprise templates into workflow_library
        for tmpl in get_all_enterprise_templates():
            workflow_library.save_definition(tmpl)

    def list_definitions(self) -> List[WorkflowDefinition]:
        """Lists registered workflow definitions."""
        return workflow_library.search_definitions("")

    def create_definition(self, wf_def: WorkflowDefinition) -> WorkflowDefinition:
        """Registers custom workflow definition in library."""
        return workflow_library.save_definition(wf_def)

    async def execute_workflow(
        self,
        definition_id: str,
        initial_vars: Optional[Dict] = None,
        user_context: Optional[Dict] = None
    ) -> WorkflowInstance:
        """
        Triggers workflow instance execution:
        1. Retrieves blueprint from WorkflowLibrary.
        2. Validates security policy via PolicyEngine.
        3. Reserves compute resources via ResourceReservationManager.
        4. Binds immutable VersionInfo via WorkflowVersioningEngine.
        5. Emits WorkflowCreated and WorkflowValidated via EventSourcingEngine.
        6. Delegates execution to WorkflowRuntime.
        """
        wf_def = workflow_library._definitions.get(definition_id)
        if not wf_def:
            raise ValueError(f"Workflow definition '{definition_id}' not found.")

        # 2. Policy Engine Security Check
        valid_policy = workflow_policy_engine.validate_workflow_policy(wf_def, user_context)
        if not valid_policy:
            raise ValueError(f"Workflow policy validation failed for '{definition_id}'.")

        # 3. Reserve Resources
        resource_reservation_manager.reserve_resources(wf_def.resource_reservation)

        # 4. Create Instance & Bind Versioning
        instance = WorkflowInstance(
            definition_id=definition_id,
            name=wf_def.name,
            status=WorkflowStatus.CREATED,
            variables=initial_vars or {}
        )
        workflow_versioning_engine.bind_version_to_instance(instance, wf_def)
        self._instances[instance.instance_id] = instance

        # 5. Emit Events
        event_sourcing_engine.emit_event(definition_id, instance.execution_id, WorkflowEventType.WORKFLOW_CREATED)
        event_sourcing_engine.emit_event(definition_id, instance.execution_id, WorkflowEventType.WORKFLOW_VALIDATED)

        # 6. Execute via WorkflowRuntime
        res_instance = await workflow_runtime.advance_runtime(instance, wf_def, wf_def.nodes[0].node_id)
        
        # Release resources upon completion or failure
        resource_reservation_manager.release_resources(wf_def.resource_reservation)
        return res_instance

    async def grant_approval(self, instance_id: str, approved: bool) -> WorkflowInstance:
        """Grants human approval or triggers Saga compensation rollback."""
        instance = self._instances.get(instance_id)
        if not instance or instance.status != WorkflowStatus.WAITING_APPROVAL:
            raise ValueError("Instance not found or not pending approval.")

        wf_def = workflow_library._definitions[instance.definition_id]

        if not approved:
            event_sourcing_engine.emit_event(instance.definition_id, instance.execution_id, WorkflowEventType.APPROVAL_REJECTED)
            return await workflow_runtime.rollback_runtime(instance, wf_def)

        event_sourcing_engine.emit_event(instance.definition_id, instance.execution_id, WorkflowEventType.APPROVAL_GRANTED)
        instance.status = WorkflowStatus.RUNNING
        instance.pending_approval_id = None

        curr_node = next(n for n in wf_def.nodes if n.node_id == instance.current_node_id)
        next_id = curr_node.next_nodes[0] if curr_node.next_nodes else None
        return await workflow_runtime.advance_runtime(instance, wf_def, next_id)

    async def rollback_instance(self, instance_id: str) -> WorkflowInstance:
        """Manually triggers Saga compensation rollback for a workflow instance."""
        instance = self._instances.get(instance_id)
        if instance:
            wf_def = workflow_library._definitions[instance.definition_id]
            return await workflow_runtime.rollback_runtime(instance, wf_def)
        raise ValueError(f"Instance '{instance_id}' not found.")

    def get_instance(self, instance_id: str) -> Optional[WorkflowInstance]:
        """Retrieves workflow instance by ID."""
        return self._instances.get(instance_id)

    def list_instances(self) -> List[WorkflowInstance]:
        """Lists active and completed workflow instances."""
        return list(self._instances.values())


workflow_engine = WorkflowEngine()
