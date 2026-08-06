"""
Voice Assistant Manager Engine (Sprint 11).
Orchestrates wake word detection, STT, LLM reasoning, TTS audio streaming, interruption, memory sync, and telemetry.
Integrated with Security Engine, Memory Manager, Event Bus, and Telemetry.
"""

from typing import Optional
import structlog

from app.ai.router import llm_router
from app.ai.schemas import LLMMessage, LLMRequest, MessageRole
from app.core.event_bus import SystemEvent, event_bus
from app.memory.manager import memory_manager
from app.security.manager import security_engine
from app.voice.interruption import interruption_controller
from app.voice.schemas import TTSRequest, VoiceInteractionRequest, VoiceInteractionResponse
from app.voice.stt import stt_engine
from app.voice.telemetry import voice_telemetry
from app.voice.tts import tts_engine
from app.voice.vad import vad_engine
from app.voice.wake_word import wake_word_detector

logger = structlog.get_logger(__name__)


class VoiceAssistantManager:
    """Central orchestrator for low-latency Voice Assistant pipeline."""

    @classmethod
    async def interact_voice(
        cls,
        req: VoiceInteractionRequest,
        user_role: str = "ADMIN"
    ) -> VoiceInteractionResponse:
        """
        Executes end-to-end voice loop:
        1. Security Engine permission check.
        2. Resets interruption flag.
        3. Performs Speech-to-Text (STT) transcription.
        4. Detects wake word.
        5. Generates LLM conversation response.
        6. Synthesizes Text-to-Speech (TTS) audio stream.
        7. Persists interaction episode into Memory Engine (redacted).
        8. Publishes event over SystemEventBus and records telemetry.
        """
        # Security RBAC Check
        security_engine.authorize(user_role=user_role, required_permission="interact_voice")

        interruption_controller.reset_interruption()
        await event_bus.publish(SystemEvent(event_type="VoiceInteractionStarted", source_subsystem="VoiceAssistantManager"))


        # 1. Speech-to-Text Transcription
        transcript = req.text_prompt
        stt_latency = 10.0

        if req.audio_base64:
            stt_res = stt_engine.transcribe_audio(req.audio_base64)
            transcript = stt_res.transcript
            stt_latency = stt_res.latency_ms

        if not transcript:
            transcript = "Hey JARVIS, state current voice intelligence subsystem health."

        # 2. Wake Word Detection
        wake_status = wake_word_detector.detect_wake_word(transcript=transcript)

        # 3. LLM Reasoning Response
        llm_req = LLMRequest(
            model="mock-gpt",
            messages=[LLMMessage(role=MessageRole.USER, content=transcript)],
            system_prompt="You are JARVIS Voice Assistant. Provide concise natural spoken responses."
        )
        llm_res = await llm_router.generate_completion(llm_req)
        clean_response = security_engine.scrub_text(llm_res.content)

        # 4. Text-to-Speech Audio Synthesis
        tts_res = tts_engine.synthesize_speech(TTSRequest(text=clean_response))

        # 5. Persist to Memory Engine (Redacted)
        await memory_manager.store_memory(
            content=f"Voice Turn: User: '{transcript}' -> JARVIS: '{clean_response}'",
            category="voice_episode"
        )

        interrupted = interruption_controller.is_interrupted()
        voice_telemetry.record_interaction(stt_latency, tts_res.latency_ms, interrupted)

        total_latency = round(stt_latency + tts_res.latency_ms + 10.0, 2)
        await event_bus.publish(
            SystemEvent(
                event_type="VoiceInteractionCompleted",
                source_subsystem="VoiceAssistantManager",
                payload={"transcript": transcript, "total_latency_ms": total_latency}
            )
        )


        return VoiceInteractionResponse(
            transcript=transcript,
            response_text=clean_response,
            audio_base64=tts_res.audio_base64,
            wake_word_detected=wake_status.detected,
            interrupted=interrupted,
            stt_latency_ms=stt_latency,
            tts_latency_ms=tts_res.latency_ms,
            total_latency_ms=total_latency
        )


voice_manager = VoiceAssistantManager()
