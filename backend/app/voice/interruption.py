"""
Speech Interruption and Barge-In Controller (Sprint 11).
Halts active TTS synthesis streams when user speech is detected and emits event over SystemEventBus.
"""

import structlog
from app.core.event_bus import SystemEvent, event_bus

logger = structlog.get_logger(__name__)


class SpeechInterruptionController:
    """Manages audio barge-in interruption state and event dispatching."""

    def __init__(self) -> None:
        self._interrupted: bool = False

    def is_interrupted(self) -> bool:
        """Returns current interruption flag."""
        return self._interrupted

    def trigger_interruption(self) -> None:
        """Triggers interruption barge-in to halt active TTS audio synthesis."""
        self._interrupted = True
        logger.info("Triggered audio synthesis barge-in interruption")
        
        # Publish event over event bus
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(
                    event_bus.publish(
                        SystemEvent(
                            event_type="VoiceInterruptionTriggered",
                            source_subsystem="SpeechInterruptionController",
                            payload={"interrupted": True}
                        )
                    )
                )
        except Exception:
            pass


    def reset_interruption(self) -> None:
        """Resets interruption flag prior to new synthesis turn."""
        self._interrupted = False


interruption_controller = SpeechInterruptionController()
