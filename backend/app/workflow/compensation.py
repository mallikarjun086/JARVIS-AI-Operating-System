"""
Saga-Style Compensation Engine (Sprint 10).
Executes inverse compensation step handlers in reverse order upon step failure or rejection.
"""

from typing import Dict, List, Optional
import structlog

from app.workflow.execution_backend import ExecutionBackend, local_execution_backend
from app.workflow.schemas import WorkflowInstance, WorkflowNode

logger = structlog.get_logger(__name__)


class CompensationEngine:
    """Saga Compensation Engine for managing partial and full inverse rollbacks."""

    @classmethod
    async def execute_saga_compensation(
        cls,
        instance: WorkflowInstance,
        nodes: List[WorkflowNode],
        backend: Optional[ExecutionBackend] = None
    ) -> bool:
        """
        Traverses completed nodes in reverse order and executes defined compensation actions.
        """
        exec_backend = backend or local_execution_backend
        logger.info("Starting Saga compensation rollback chain", instance_id=instance.instance_id, completed_nodes=instance.completed_node_ids)

        node_map = {n.node_id: n for n in nodes}
        reverse_ids = list(reversed(instance.completed_node_ids))

        for node_id in reverse_ids:
            node = node_map.get(node_id)
            if node and node.compensation_action:
                logger.info("Executing inverse compensation step", node_id=node_id, action=node.compensation_action)
                try:
                    await exec_backend.dispatch_step_task(
                        goal=f"Compensate step '{node.name}' via inverse action '{node.compensation_action}'",
                        capability="general_processing"
                    )
                except Exception as e:
                    logger.error("Saga compensation step failed", node_id=node_id, error=str(e))

        logger.info("Saga compensation chain completed", instance_id=instance.instance_id)
        return True


compensation_engine = CompensationEngine()
