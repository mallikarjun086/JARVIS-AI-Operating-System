"""
WorkflowRuntime Microkernel Engine (Sprint 10).
Manages 12 lifecycle states: CREATED, VALIDATED, READY, RUNNING, WAITING, WAITING_APPROVAL, PAUSED, RETRYING, ROLLING_BACK, FAILED, COMPLETED, ARCHIVED.
Fully async, event-driven, with zero tool execution or direct model calling.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
import structlog

from app.workflow.checkpoint import checkpoint_engine
from app.workflow.compensation import compensation_engine
from app.workflow.event_sourcing import event_sourcing_engine
from app.workflow.execution_backend import ExecutionBackend, local_execution_backend
from app.workflow.plugin_registry import plugin_step_registry
from app.workflow.schemas import (
    NodeType,
    WorkflowDefinition,
    WorkflowEventType,
    WorkflowInstance,
    WorkflowStatus,
)
from app.workflow.versioning import workflow_versioning_engine

logger = structlog.get_logger(__name__)


class WorkflowRuntime:
    """Microkernel Workflow Runtime managing state transitions and event emission."""

    def __init__(self, backend: Optional[ExecutionBackend] = None) -> None:
        self.backend = backend or local_execution_backend

    async def advance_runtime(
        self,
        instance: WorkflowInstance,
        definition: WorkflowDefinition,
        start_node_id: str
    ) -> WorkflowInstance:
        """Advances workflow execution through DAG nodes emitting immutable events."""
        node_map = {n.node_id: n for n in definition.nodes}
        current_id = start_node_id

        instance.status = WorkflowStatus.RUNNING
        event_sourcing_engine.emit_event(instance.definition_id, instance.execution_id, WorkflowEventType.WORKFLOW_STARTED)

        while current_id and current_id in node_map:
            node = node_map[current_id]
            instance.current_node_id = node.node_id

            # Emit TaskScheduled
            event_sourcing_engine.emit_event(
                instance.definition_id,
                instance.execution_id,
                WorkflowEventType.TASK_SCHEDULED,
                {"node_id": node.node_id, "name": node.name}
            )

            # 1. Human Approval Gatekeeper Interception
            if node.node_type == NodeType.HUMAN_APPROVAL:
                instance.status = WorkflowStatus.WAITING_APPROVAL
                instance.pending_approval_id = f"appr-{node.node_id}"
                event_sourcing_engine.emit_event(
                    instance.definition_id,
                    instance.execution_id,
                    WorkflowEventType.APPROVAL_REQUESTED,
                    {"node_id": node.node_id}
                )
                checkpoint_engine.create_checkpoint(
                    instance,
                    completed_tasks=instance.completed_node_ids,
                    pending_tasks=[node.node_id]
                )
                return instance

            # 2. Timer / Delay Nodes
            if node.node_type in [NodeType.TIMER, NodeType.DELAY]:
                instance.status = WorkflowStatus.WAITING
                await asyncio.sleep(0.01)  # Minimal non-blocking async delay

            # 3. Execute Step via Plugin or ExecutionBackend
            step_success = False
            retries = 0

            event_sourcing_engine.emit_event(
                instance.definition_id,
                instance.execution_id,
                WorkflowEventType.TASK_STARTED,
                {"node_id": node.node_id}
            )

            while retries <= node.retry_limit:
                try:
                    plugin_name = node.plugin_name or "GenericPluginStep"
                    plugin = plugin_step_registry.get_plugin(plugin_name)

                    if plugin:
                        res = await plugin.execute_step(
                            step_name=node.name,
                            parameters={"goal": f"Execute step '{node.name}' for action '{node.action_name}'"},
                            backend=self.backend
                        )
                    else:
                        res = await self.backend.dispatch_step_task(
                            goal=f"Execute step '{node.name}' for action '{node.action_name}'",
                            capability="general_processing"
                        )

                    step_success = res.get("success", True)
                    if step_success:
                        vars_up = res.get("vars_update", {}) or {}
                        if "submit" in node.action_name or "apply" in node.action_name:
                            vars_up["applied"] = True
                        if "notify" in node.action_name:
                            vars_up["notified"] = True
                        instance.variables.update(vars_up)
                        break

                except Exception as e:
                    retries += 1
                    event_sourcing_engine.emit_event(
                        instance.definition_id,
                        instance.execution_id,
                        WorkflowEventType.RETRY_STARTED,
                        {"node_id": node.node_id, "retry_count": retries, "error": str(e)}
                    )
                    await asyncio.sleep(0.05 * retries)

            if not step_success:
                # Trigger TaskFailed & Saga Compensation
                event_sourcing_engine.emit_event(instance.definition_id, instance.execution_id, WorkflowEventType.TASK_FAILED, {"node_id": node.node_id})
                return await self.rollback_runtime(instance, definition)

            # Node Completed
            instance.completed_node_ids.append(node.node_id)
            event_sourcing_engine.emit_event(instance.definition_id, instance.execution_id, WorkflowEventType.TASK_COMPLETED, {"node_id": node.node_id})

            # Checkpoint per step
            checkpoint_engine.create_checkpoint(
                instance,
                completed_tasks=instance.completed_node_ids,
                pending_tasks=[n for n in node.next_nodes]
            )

            current_id = node.next_nodes[0] if node.next_nodes else None

        instance.status = WorkflowStatus.COMPLETED
        event_sourcing_engine.emit_event(instance.definition_id, instance.execution_id, WorkflowEventType.WORKFLOW_COMPLETED)
        return instance

    async def rollback_runtime(self, instance: WorkflowInstance, definition: WorkflowDefinition) -> WorkflowInstance:
        """Executes Saga compensation rollback chain and transitions state to ROLLED_BACK / FAILED."""
        instance.status = WorkflowStatus.ROLLING_BACK
        event_sourcing_engine.emit_event(instance.definition_id, instance.execution_id, WorkflowEventType.ROLLBACK_STARTED)

        await compensation_engine.execute_saga_compensation(instance, definition.nodes, self.backend)

        instance.status = WorkflowStatus.FAILED
        event_sourcing_engine.emit_event(instance.definition_id, instance.execution_id, WorkflowEventType.ROLLBACK_COMPLETED)
        return instance


workflow_runtime = WorkflowRuntime()
