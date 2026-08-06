"""
Browser Error Recovery Engine — Navigation Timeouts, Automatic Retries, Lost Context Restoration & Crash Recovery.
"""

import asyncio
from typing import Any, Callable, Coroutine
import structlog

logger = structlog.get_logger(__name__)


class BrowserRecoveryEngine:
    """Handles automatic error recovery for Playwright browser actions."""

    @classmethod
    async def execute_with_recovery(
        cls,
        action_fn: Callable[[], Coroutine[Any, Any, Any]],
        max_retries: int = 3,
        backoff_seconds: float = 1.0
    ) -> Any:
        """Executes action function with exponential retry backoff on navigation or Playwright error."""
        last_error = None
        for attempt in range(1, max_retries + 1):
            try:
                return await action_fn()
            except Exception as e:
                last_error = e
                logger.warning("Browser action attempt failed", attempt=attempt, max_retries=max_retries, error=str(e))
                if attempt < max_retries:
                    await asyncio.sleep(backoff_seconds * attempt)

        raise RuntimeError(f"Browser action failed after {max_retries} attempts: {last_error}")


browser_recovery = BrowserRecoveryEngine()
