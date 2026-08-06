"""
Checkpoint Manager — Periodically saves execution state checkpoints for crash recovery and execution resumption.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import structlog

logger = structlog.get_logger(__name__)


class ExecutionCheckpoint(BaseModel):
    """Execution checkpoint snapshot."""
    plan_id: str
    checkpoint_id: str
    completed_task_ids: List[str]
    pending_task_ids: List[str]
    task_outputs: Dict[str, Any]
    current_batch_id: int
    execution_state: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CheckpointManager:
    """Manages creation, storage, and retrieval of execution checkpoints."""

    def __init__(self) -> None:
        self._checkpoints: Dict[str, List[ExecutionCheckpoint]] = {}  # {plan_id -> list[Checkpoint]}

    def save_checkpoint(
        self,
        plan_id: str,
        batch_id: int,
        completed_ids: List[str],
        pending_ids: List[str],
        outputs: Dict[str, Any],
        state: str
    ) -> ExecutionCheckpoint:
        """Saves a checkpoint snapshot for a plan."""
        cp = ExecutionCheckpoint(
            plan_id=plan_id,
            checkpoint_id=f"cp-{batch_id}-{int(datetime.utcnow().timestamp())}",
            completed_task_ids=list(completed_ids),
            pending_task_ids=list(pending_ids),
            task_outputs=dict(outputs),
            current_batch_id=batch_id,
            execution_state=state
        )
        if plan_id not in self._checkpoints:
            self._checkpoints[plan_id] = []
        self._checkpoints[plan_id].append(cp)

        logger.info("Saved execution checkpoint", plan_id=plan_id, batch_id=batch_id, completed_count=len(completed_ids))
        return cp

    def get_latest_checkpoint(self, plan_id: str) -> Optional[ExecutionCheckpoint]:
        """Returns latest checkpoint snapshot for plan resumption."""
        cps = self._checkpoints.get(plan_id, [])
        return cps[-1] if cps else None


checkpoint_manager = CheckpointManager()
