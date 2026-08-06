"""
Pydantic Schemas for Enterprise Voice Intelligence Subsystem (Sprint 11).
Defines STT, TTS, WakeWord, VAD, VoiceProfiles, Telemetry, and Voice Interactions.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field, ConfigDict


class AudioFormat(str, Enum):
    WAV = "WAV"
    MP3 = "MP3"
    PCM = "PCM"
    OGG = "OGG"


class STTEngineType(str, Enum):
    WHISPER = "WHISPER"
    LOCAL_FAST = "LOCAL_FAST"
    DEEP_SPEECH = "DEEP_SPEECH"


class TTSEngineType(str, Enum):
    STREAMING = "STREAMING"
    LOCAL_NEURAL = "LOCAL_NEURAL"
    ELEVEN_LABS = "ELEVEN_LABS"


class WakeWordStatus(BaseModel):
    """Wake Word detection result payload."""
    detected: bool = False
    confidence: float = Field(default=0.99, ge=0.0, le=1.0)
    wake_word: str = "Hey JARVIS"
    audio_segment_ms: float = 450.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class VADConfig(BaseModel):
    """Voice Activity Detection Configuration."""
    sensitivity: float = Field(default=0.75, ge=0.0, le=1.0)
    silence_threshold_ms: float = 300.0
    speech_pad_ms: float = 100.0
    enabled: bool = True


class VoiceProfile(BaseModel):
    """Voice profile settings payload."""
    profile_id: str = Field(default_factory=lambda: f"vprof-{uuid.uuid4().hex[:8]}")
    name: str
    pitch: float = Field(default=1.0, ge=0.5, le=2.0)
    speed: float = Field(default=1.0, ge=0.5, le=2.0)
    timbre_warmth: float = Field(default=0.8, ge=0.0, le=1.0)
    voice_id: str = "jarvis_male_deep"
    is_active: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


class STTRequest(BaseModel):
    """Speech-to-Text transcription request payload."""
    audio_base64: str
    language: str = "en"
    engine_type: STTEngineType = STTEngineType.WHISPER


class STTResponse(BaseModel):
    """Speech-to-Text transcription output payload."""
    transcript: str
    confidence: float = 0.98
    language: str = "en"
    words_count: int = 8
    latency_ms: float = 120.0


class TTSRequest(BaseModel):
    """Text-to-Speech synthesis request payload."""
    text: str
    voice_profile_id: Optional[str] = None
    format: AudioFormat = AudioFormat.WAV
    engine_type: TTSEngineType = TTSEngineType.STREAMING
    stream: bool = True


class TTSResponse(BaseModel):
    """Text-to-Speech synthesis output payload."""
    audio_base64: str = Field(..., description="Base64 encoded audio bytes")
    format: AudioFormat = AudioFormat.WAV
    sample_rate: int = 24000
    channels: int = 1
    duration_seconds: float = 2.5
    latency_ms: float = 135.0


class VoiceInteractionRequest(BaseModel):
    """Full voice interaction payload."""
    audio_base64: Optional[str] = None
    text_prompt: Optional[str] = None
    allow_interruption: bool = True
    session_id: Optional[str] = None


class VoiceInteractionResponse(BaseModel):
    """Full voice interaction response payload."""
    model_config = ConfigDict(from_attributes=True)

    interaction_id: str = Field(default_factory=lambda: f"vact-{uuid.uuid4().hex[:8]}")
    session_id: str = Field(default_factory=lambda: f"vsession-{uuid.uuid4().hex[:8]}")
    transcript: str
    response_text: str
    audio_base64: str
    wake_word_detected: bool = True
    interrupted: bool = False
    stt_latency_ms: float = 110.0
    tts_latency_ms: float = 125.0
    total_latency_ms: float = 235.0
    latency_ms: float = 235.0
    executed_at: datetime = Field(default_factory=datetime.utcnow)



class VoiceTelemetryMetrics(BaseModel):
    """Telemetry metrics for Voice Assistant subsystem."""
    total_interactions: int = 0
    successful_stt_count: int = 0
    successful_tts_count: int = 0
    interruption_count: int = 0
    avg_stt_latency_ms: float = 115.0
    avg_tts_latency_ms: float = 130.0
    avg_total_latency_ms: float = 245.0
    uptime_seconds: float = 0.0
