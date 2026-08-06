"""
Pytest Integration Test Suite for Enterprise Voice Intelligence Subsystem (Sprint 11).
Tests STT, TTS, Wake Word Detection, VAD, Barge-In Interruption, Voice Profiles, Telemetry, and REST APIs.
"""

from httpx import AsyncClient
import pytest

from app.voice.interruption import interruption_controller
from app.voice.manager import voice_manager
from app.voice.profile import voice_profile_store
from app.voice.schemas import TTSRequest, VADConfig, VoiceInteractionRequest
from app.voice.stt import stt_engine
from app.voice.telemetry import voice_telemetry
from app.voice.tts import tts_engine
from app.voice.vad import vad_engine
from app.voice.wake_word import wake_word_detector


@pytest.mark.asyncio
async def test_stt_and_tts_engines():
    """Verifies low-latency STT transcription and streaming TTS synthesis engines."""
    # STT Test
    stt_res = stt_engine.transcribe_audio("sample_base64_audio_data")
    assert stt_res.transcript is not None
    assert stt_res.latency_ms < 200.0

    # TTS Test
    tts_req = TTSRequest(text="Hello world, JARVIS voice operational.")
    tts_res = tts_engine.synthesize_speech(tts_req)
    assert tts_res.audio_base64 is not None
    assert tts_res.sample_rate == 24000
    assert tts_res.latency_ms < 200.0


@pytest.mark.asyncio
async def test_wake_word_and_vad_engines():
    """Verifies Wake Word detector and Voice Activity Detector (VAD)."""
    ww_res = wake_word_detector.detect_wake_word(transcript="Hey JARVIS, check status")
    assert ww_res.detected is True
    assert ww_res.wake_word == "Hey JARVIS"

    has_speech, energy, duration = vad_engine.process_audio_buffer("audio_sample_bytes_base64")
    assert has_speech is True
    assert energy > 0.5

    cfg = vad_engine.set_config(VADConfig(sensitivity=0.8, silence_threshold_ms=250.0))
    assert cfg.sensitivity == 0.8


@pytest.mark.asyncio
async def test_interruption_and_profiles():
    """Verifies barge-in speech interruption controller and voice profile store."""
    interruption_controller.reset_interruption()
    assert interruption_controller.is_interrupted() is False

    interruption_controller.trigger_interruption()
    assert interruption_controller.is_interrupted() is True

    # Profile Store
    profiles = voice_profile_store.list_profiles()
    assert len(profiles) >= 3

    new_prof = voice_profile_store.create_profile("Custom Studio Voice", pitch=1.1, speed=0.95)
    assert new_prof.name == "Custom Studio Voice"

    active = voice_profile_store.set_active(new_prof.profile_id)
    assert active.profile_id == new_prof.profile_id
    assert voice_profile_store.get_active_profile().profile_id == new_prof.profile_id


@pytest.mark.asyncio
async def test_voice_assistant_manager_interaction():
    """Verifies end-to-end VoiceAssistantManager pipeline interaction."""
    req = VoiceInteractionRequest(text_prompt="Hey JARVIS, run diagnostic")
    resp = await voice_manager.interact_voice(req)

    assert resp.transcript == "Hey JARVIS, run diagnostic"
    assert resp.response_text is not None
    assert resp.audio_base64 is not None
    assert resp.total_latency_ms < 500.0


@pytest.mark.asyncio
async def test_voice_rest_api_endpoints(client: AsyncClient):
    """Verifies FastAPI REST endpoints for Voice Intelligence Subsystem."""
    await client.post("/api/v1/auth/register", json={"email": "voice@jarvis.ai", "password": "Password123!", "full_name": "Voice User"})
    login_resp = await client.post("/api/v1/auth/login", data={"username": "voice@jarvis.ai", "password": "Password123!"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Full Voice Interaction Endpoint
    int_resp = await client.post("/api/v1/voice/interact", json={"text_prompt": "Hey JARVIS, system status"}, headers=headers)
    assert int_resp.status_code == 200
    assert "response_text" in int_resp.json()

    # 2. Detect Wake Word Endpoint
    ww_resp = await client.post("/api/v1/voice/detect-wakeword?transcript=Hey+JARVIS", headers=headers)
    assert ww_resp.status_code == 200
    assert ww_resp.json()["detected"] is True

    # 3. List Profiles Endpoint
    prof_resp = await client.get("/api/v1/voice/profiles", headers=headers)
    assert prof_resp.status_code == 200
    assert len(prof_resp.json()) >= 3

    # 4. Voice Metrics Endpoint
    met_resp = await client.get("/api/v1/voice/metrics", headers=headers)
    assert met_resp.status_code == 200
    assert "avg_total_latency_ms" in met_resp.json()

    # 5. Voice Health Endpoint
    hlth_resp = await client.get("/api/v1/voice/health", headers=headers)
    assert hlth_resp.status_code == 200
    assert hlth_resp.json()["status"] == "HEALTHY"
