"""
Immutable Event Sourcing Engine for Workflow Runtime (Sprint 10).
Records immutable workflow transition events and reconstructs workflow state from event streams.
"""

from datetime import datetime
from typing import Dict, List, Optional
import structlog

from app.workflow.schemas import WorkflowEvent, WorkflowEventType, WorkflowStatus

logger = structlog.get_logger(__name__)

# Mapping from event types to workflow runtime state transitions
EVENT_STATE_MAP = {
    WorkflowEventType.WORKFLOW_CREATED: WorkflowStatus.CREATED,
    WorkflowEventType.WORKFLOW_VALIDATED: WorkflowStatus.VALIDATED,
    WorkflowEventType.WORKFLOW_STARTED: WorkflowStatus.RUNNING,
    WorkflowEventType.WORKFLOW_PAUSED: WorkflowStatus.PAUSED,
    WorkflowEventType.WORKFLOW_RESUMED: WorkflowStatus.RUNNING,
    WorkflowEventType.APPROVAL_REQUESTED: WorkflowStatus.WAITING_APPROVAL,
    WorkflowEventType.APPROVAL_GRANTED: WorkflowStatus.RUNNING,
    WorkflowEventType.APPROVAL_REJECTED: WorkflowStatus.ROLLING_BACK,
    WorkflowEventType.RETRY_STARTED: WorkflowStatus.RETRYING,
    WorkflowEventType.ROLLBACK_STARTED: WorkflowStatus.ROLLING_BACK,
    WorkflowEventType.ROLLBACK_COMPLETED: WorkflowStatus.FAILED,
    WorkflowEventType.TASK_FAILED: WorkflowStatus.RETRYING,
    WorkflowEventType.WORKFLOW_COMPLETED: WorkflowStatus.COMPLETED,
    WorkflowEventType.WORKFLOW_ARCHIVED: WorkflowStatus.ARCHIVED,
}


class EventSourcingEngine:
    """Event Sourcing Manager storing immutable workflow event streams."""

    def __init__(self) -> None:
        self._streams: Dict[str, List[WorkflowEvent]] = {}

    def emit_event(
        self,
        workflow_id: str,
        execution_id: str,
        event_type: WorkflowEventType,
        payload: Optional[Dict] = None
    ) -> WorkflowEvent:
        """Emits an immutable WorkflowEvent and appends to event stream."""
        event = WorkflowEvent(
            workflow_id=workflow_id,
            execution_id=execution_id,
            event_type=event_type,
            payload=payload or {}
        )

        if workflow_id not in self._streams:
            self._streams[workflow_id] = []
        self._streams[workflow_id].append(event)
        logger.info("Emitted WorkflowEvent", workflow_id=workflow_id, event_type=event_type.value)
        return event

    def get_event_stream(self, workflow_id: str) -> List[WorkflowEvent]:
        """Retrieves immutable event stream for target workflow instance."""
        return self._streams.get(workflow_id, [])

    def reconstruct_state(self, workflow_id: str) -> WorkflowStatus:
        """Reconstructs current WorkflowStatus by replaying event stream from start to finish."""
        stream = self.get_event_stream(workflow_id)
        if not stream:
            return WorkflowStatus.CREATED

        current_status = WorkflowStatus.CREATED
        for event in stream:
            if event.event_type in EVENT_STATE_MAP:
                current_status = EVENT_STATE_MAP[event.event_type]

        logger.debug("Reconstructed workflow status from event stream", workflow_id=workflow_id, status=current_status.value)
        return current_status


event_sourcing_engine = EventSourcingEngine()
