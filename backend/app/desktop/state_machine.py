"""
Window State Machine — Enforces valid window lifecycle state transitions.
"""

from typing import Dict, Set
import structlog
from app.desktop.schemas import WindowState

logger = structlog.get_logger(__name__)

# Valid state transition rules
VALID_WINDOW_TRANSITIONS: Dict[WindowState, Set[WindowState]] = {
    WindowState.CREATED: {WindowState.OPENING, WindowState.ERROR, WindowState.CLOSED},
    WindowState.OPENING: {WindowState.READY, WindowState.ERROR, WindowState.CLOSED},
    WindowState.READY: {WindowState.ACTIVE, WindowState.BACKGROUND, WindowState.CLOSED, WindowState.ERROR},
    WindowState.ACTIVE: {WindowState.BACKGROUND, WindowState.MINIMIZED, WindowState.MAXIMIZED, WindowState.SUSPENDED, WindowState.CLOSED, WindowState.ERROR},
    WindowState.BACKGROUND: {WindowState.ACTIVE, WindowState.MINIMIZED, WindowState.CLOSED, WindowState.ERROR},
    WindowState.MINIMIZED: {WindowState.ACTIVE, WindowState.READY, WindowState.CLOSED},
    WindowState.MAXIMIZED: {WindowState.ACTIVE, WindowState.READY, WindowState.CLOSED},
    WindowState.SUSPENDED: {WindowState.ACTIVE, WindowState.ERROR, WindowState.CLOSED},
    WindowState.CLOSED: set(),
    WindowState.ERROR: {WindowState.READY, WindowState.CLOSED},
}


class WindowStateMachine:
    """Enforces state machine transition rules for desktop window handles."""

    @classmethod
    def transition(cls, current_state: WindowState, target_state: WindowState) -> WindowState:
        """Transitions window state if valid."""
        if current_state == target_state:
            return current_state

        valid_targets = VALID_WINDOW_TRANSITIONS.get(current_state, set())
        if target_state not in valid_targets:
            msg = f"Invalid window transition from '{current_state.value}' to '{target_state.value}'."
            logger.error("Window state machine transition error", current=current_state.value, target=target_state.value)
            raise ValueError(msg)

        logger.info("Window state transition", current=current_state.value, target=target_state.value)
        return target_state


window_state_machine = WindowStateMachine()
