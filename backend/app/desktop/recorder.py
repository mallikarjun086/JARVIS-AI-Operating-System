"""
Desktop Workflow Recording Engine — Records user automation actions for Planner replay.
"""

from datetime import datetime
from typing import Any, Dict, List
import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)


class RecordedActionStep(BaseModel):
    """Recorded action step descriptor."""
    step_id: int
    app_name: str
    window_title: str
    action_type: str
    parameters: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str = "SUCCESS"


class RecordedWorkflow(BaseModel):
    """Recorded desktop workflow script."""
    workflow_name: str
    steps: List[RecordedActionStep] = Field(default_factory=list)
    recorded_at: datetime = Field(default_factory=datetime.utcnow)


class WorkflowRecorder:
    """Records desktop automation sequences into replayable RecordedWorkflow models."""

    def __init__(self) -> None:
        self._is_recording: bool = False
        self._current_steps: List[RecordedActionStep] = []

    def start_recording(self) -> None:
        """Starts recording action steps."""
        self._is_recording = True
        self._current_steps.clear()
        logger.info("Started desktop workflow recording")

    def record_step(
        self,
        app_name: str,
        window_title: str,
        action_type: str,
        parameters: Dict[str, Any],
        status: str = "SUCCESS"
    ) -> None:
        """Appends step if recording is active."""
        if not self._is_recording:
            return

        step = RecordedActionStep(
            step_id=len(self._current_steps) + 1,
            app_name=app_name,
            window_title=window_title,
            action_type=action_type,
            parameters=parameters,
            status=status
        )
        self._current_steps.append(step)

    def stop_recording(self, workflow_name: str = "Recorded_Workflow") -> RecordedWorkflow:
        """Stops recording and returns RecordedWorkflow script."""
        self._is_recording = False
        wf = RecordedWorkflow(
            workflow_name=workflow_name,
            steps=list(self._current_steps)
        )
        logger.info("Stopped desktop workflow recording", step_count=len(wf.steps))
        return wf


workflow_recorder = WorkflowRecorder()
