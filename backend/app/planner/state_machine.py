"""
Execution State Machine — Enforces valid state transition rules across 11 plan lifecycle states.
"""

from typing import Dict, Set
import structlog
from app.planner.schemas import ExecutionState

logger = structlog.get_logger(__name__)

# Valid state transition graph
VALID_TRANSITIONS: Dict[ExecutionState, Set[ExecutionState]] = {
    ExecutionState.CREATED: {ExecutionState.PLANNED, ExecutionState.FAILED, ExecutionState.CANCELLED},
    ExecutionState.PLANNED: {ExecutionState.VALIDATED, ExecutionState.FAILED, ExecutionState.CANCELLED},
    ExecutionState.VALIDATED: {ExecutionState.WAITING_APPROVAL, ExecutionState.READY, ExecutionState.FAILED, ExecutionState.CANCELLED},
    ExecutionState.WAITING_APPROVAL: {ExecutionState.READY, ExecutionState.CANCELLED, ExecutionState.FAILED},
    ExecutionState.READY: {ExecutionState.RUNNING, ExecutionState.CANCELLED, ExecutionState.PAUSED},
    ExecutionState.RUNNING: {ExecutionState.PAUSED, ExecutionState.RETRYING, ExecutionState.ROLLING_BACK, ExecutionState.COMPLETED, ExecutionState.FAILED, ExecutionState.CANCELLED},
    ExecutionState.PAUSED: {ExecutionState.RUNNING, ExecutionState.CANCELLED},
    ExecutionState.RETRYING: {ExecutionState.RUNNING, ExecutionState.ROLLING_BACK, ExecutionState.FAILED},
    ExecutionState.ROLLING_BACK: {ExecutionState.FAILED, ExecutionState.CANCELLED},
    ExecutionState.COMPLETED: set(),
    ExecutionState.FAILED: set(),
    ExecutionState.CANCELLED: set(),
}


class ExecutionStateMachine:
    """Enforces state machine transitions for ExecutionPlan instances."""

    @classmethod
    def transition(cls, current_state: ExecutionState, target_state: ExecutionState) -> ExecutionState:
        """
        Validates and transitions state from current_state to target_state.
        Raises ValueError if transition is invalid.
        """
        if current_state == target_state:
            return current_state

        valid_targets = VALID_TRANSITIONS.get(current_state, set())
        if target_state not in valid_targets:
            msg = f"Invalid state transition: Cannot transition from '{current_state.value}' to '{target_state.value}'."
            logger.error("State machine transition error", current=current_state.value, target=target_state.value)
            raise ValueError(msg)

        logger.info("State machine transition", current=current_state.value, target=target_state.value)
        return target_state


state_machine = ExecutionStateMachine()
