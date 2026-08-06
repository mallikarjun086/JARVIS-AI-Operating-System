"""
Deterministic 7-Step Desktop Recovery Engine.
Ladder: Retry Action -> Re-find Control -> Refocus Window -> Restore Window -> Restart Application -> Restore Session -> Abort.
"""

import asyncio
from typing import Any, Callable, Coroutine, Optional
import structlog

logger = structlog.get_logger(__name__)


class DesktopRecoveryEngine:
    """Handles deterministic recovery ladder for desktop automation failures."""

    @classmethod
    async def execute_with_recovery_ladder(
        cls,
        action_fn: Callable[[], Coroutine[Any, Any, Any]],
        refind_control_fn: Optional[Callable[[], Coroutine[Any, Any, Any]]] = None,
        refocus_window_fn: Optional[Callable[[], Coroutine[Any, Any, Any]]] = None,
        restore_window_fn: Optional[Callable[[], Coroutine[Any, Any, Any]]] = None,
        restart_app_fn: Optional[Callable[[], Coroutine[Any, Any, Any]]] = None,
        restore_session_fn: Optional[Callable[[], Coroutine[Any, Any, Any]]] = None,
        max_retries: int = 3
    ) -> Any:
        """Executes 7-step deterministic recovery ladder on action failure."""
        # Step 1: Retry Action
        for attempt in range(1, max_retries + 1):
            try:
                return await action_fn()
            except Exception as e:
                logger.warning("Recovery Step 1 (Action Retry) failed", attempt=attempt, error=str(e))
                await asyncio.sleep(0.3)

        # Step 2: Re-find Control
        if refind_control_fn:
            try:
                logger.info("Recovery Step 2: Attempting to re-find UI control")
                await refind_control_fn()
                return await action_fn()
            except Exception as e:
                logger.warning("Recovery Step 2 failed", error=str(e))

        # Step 3: Refocus Window
        if refocus_window_fn:
            try:
                logger.info("Recovery Step 3: Refocusing target window")
                await refocus_window_fn()
                return await action_fn()
            except Exception as e:
                logger.warning("Recovery Step 3 failed", error=str(e))

        # Step 4: Restore Window State
        if restore_window_fn:
            try:
                logger.info("Recovery Step 4: Restoring target window state")
                await restore_window_fn()
                return await action_fn()
            except Exception as e:
                logger.warning("Recovery Step 4 failed", error=str(e))

        # Step 5: Restart Application
        if restart_app_fn:
            try:
                logger.info("Recovery Step 5: Restarting application")
                await restart_app_fn()
                return await action_fn()
            except Exception as e:
                logger.warning("Recovery Step 5 failed", error=str(e))

        # Step 6: Restore Desktop Session
        if restore_session_fn:
            try:
                logger.info("Recovery Step 6: Restoring desktop automation session checkpoint")
                await restore_session_fn()
                return await action_fn()
            except Exception as e:
                logger.warning("Recovery Step 6 failed", error=str(e))

        # Step 7: Abort Execution
        logger.error("Desktop recovery ladder exhausted: aborting action execution")
        raise RuntimeError("Desktop action failed across all 7 recovery ladder steps.")


desktop_recovery = DesktopRecoveryEngine()

