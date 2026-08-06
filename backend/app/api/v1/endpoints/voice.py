"""
FastAPI Endpoints for Enterprise Voice Intelligence Subsystem (Sprint 11).
Endpoints: /interact, /detect-wakeword, /stt, /tts, /interrupt, /profiles, /vad/config, /metrics, /health.
"""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, Query, status
from app.api.deps import get_current_user
from app.models.user import User
from app.voice.interruption import interruption_controller
from app.voice.manager import voice_manager
from app.voice.profile import voice_profile_store
from app.voice.schemas import (
    STTResponse,
    TTSRequest,
    TTSResponse,
    VADConfig,
    VoiceInteractionRequest,
    VoiceInteractionResponse,
    VoiceProfile,
    VoiceTelemetryMetrics,
    WakeWordStatus,
)
from app.voice.stt import stt_engine
from app.voice.telemetry import voice_telemetry
from app.voice.tts import tts_engine
from app.voice.vad import vad_engine
from app.voice.wake_word import wake_word_detector

router = APIRouter()


@router.post("/interact", response_model=VoiceInteractionResponse, summary="Full Voice Assistant Interaction")
async def interact_voice(
    req: VoiceInteractionRequest,
    current_user: User = Depends(get_current_user)
) -> VoiceInteractionResponse:
    """Executes full voice interaction loop (STT -> LLM reasoning -> TTS audio streaming)."""
    return await voice_manager.interact_voice(req)


@router.post("/detect-wakeword", response_model=WakeWordStatus, summary="Detect 'Hey JARVIS' Wake Word")
async def detect_wake_word(
    transcript: str = Query("Hey JARVIS", description="Input text or transcript"),
    current_user: User = Depends(get_current_user)
) -> WakeWordStatus:
    """Scans audio buffer or input text for wake word triggers."""
    return wake_word_detector.detect_wake_word(transcript=transcript)


@router.post("/stt", response_model=STTResponse, summary="Perform Low-Latency Speech-to-Text")
async def speech_to_text(
    audio_base64: str = Query("sample_audio_base64", description="Base64 audio bytes"),
    current_user: User = Depends(get_current_user)
) -> STTResponse:
    """Transcribes audio stream bytes into text with <150ms latency optimization."""
    return stt_engine.transcribe_audio(audio_base64)


@router.post("/tts", response_model=TTSResponse, summary="Perform Real-Time Text-to-Speech")
async def text_to_speech(
    req: TTSRequest,
    current_user: User = Depends(get_current_user)
) -> TTSResponse:
    """Synthesizes response text into Base64 audio stream chunks tailored to active voice profile."""
    return tts_engine.synthesize_speech(req)


@router.post("/interrupt", summary="Trigger Speech Interruption (Barge-In)")
async def trigger_speech_interruption(
    current_user: User = Depends(get_current_user)
):
    """Instantly halts active TTS audio synthesis stream when user speaks mid-response."""
    interruption_controller.trigger_interruption()
    return {"message": "Audio synthesis interrupted (barge-in active)."}


@router.get("/profiles", response_model=List[VoiceProfile], summary="List Voice Profiles")
async def list_voice_profiles(
    current_user: User = Depends(get_current_user)
) -> List[VoiceProfile]:
    """Lists available customizable voice profiles."""
    return voice_profile_store.list_profiles()


@router.post("/profiles", response_model=VoiceProfile, summary="Create Custom Voice Profile")
async def create_voice_profile(
    name: str = Query(..., description="Profile name"),
    pitch: float = Query(1.0, ge=0.5, le=2.0),
    speed: float = Query(1.0, ge=0.5, le=2.0),
    current_user: User = Depends(get_current_user)
) -> VoiceProfile:
    """Creates a new customizable voice profile."""
    return voice_profile_store.create_profile(name=name, pitch=pitch, speed=speed)


@router.post("/profiles/{profile_id}/activate", response_model=VoiceProfile, summary="Set Active Voice Profile")
async def activate_voice_profile(
    profile_id: str,
    current_user: User = Depends(get_current_user)
) -> VoiceProfile:
    """Sets active voice profile by ID."""
    prof = voice_profile_store.set_active(profile_id)
    return prof or voice_profile_store.get_active_profile()


@router.post("/vad/config", response_model=VADConfig, summary="Configure Voice Activity Detector")
async def configure_vad(
    config: VADConfig,
    current_user: User = Depends(get_current_user)
) -> VADConfig:
    """Configures Voice Activity Detector (VAD) sensitivity and silence threshold."""
    return vad_engine.set_config(config)


@router.get("/metrics", response_model=VoiceTelemetryMetrics, summary="Get Voice Telemetry Metrics")
async def get_voice_metrics(
    current_user: User = Depends(get_current_user)
) -> VoiceTelemetryMetrics:
    """Returns live telemetry performance metrics for Voice Subsystem."""
    return voice_telemetry.get_metrics()


@router.get("/health", summary="Voice Intelligence Health Diagnostic")
async def get_voice_health(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Returns detailed health status for Voice Assistant engines."""
    return {
        "status": "HEALTHY",
        "subsystem": "VoiceIntelligence",
        "stt_engine": "WhisperSTTEngine",
        "tts_engine": "StreamingTTSEngine",
        "wake_word_detector": "AcousticWakeWordDetector",
        "vad_engine": "VoiceActivityDetector",
        "active_profile": voice_profile_store.get_active_profile().name,
        "interrupted": interruption_controller.is_interrupted()
    }
