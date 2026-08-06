"""
Pytest Test Suite for Voice Assistant Subsystem.
Tests wake word detection, STT transcription, TTS synthesis, streaming, interruption barge-in, context awareness, voice profiles, and latency telemetry.
"""

from httpx import AsyncClient
import pytest
from app.voice.interruption import interruption_controller
from app.voice.manager import voice_manager
from app.voice.profile import voice_profile_store
from app.voice.schemas import TTSRequest, VoiceInteractionRequest
from app.voice.stt import stt_engine
from app.voice.tts import tts_engine
from app.voice.wake_word import wake_word_detector


@pytest.mark.asyncio
async def test_wake_word_detection():
    """Verifies 'Hey JARVIS' wake word detection with confidence scoring."""
    status = wake_word_detector.detect_wake_word(transcript="Hey JARVIS, state status")
    assert status.detected is True
    assert status.confidence >= 0.95
    assert status.wake_word == "Hey JARVIS"


@pytest.mark.asyncio
async def test_stt_and_tts_engines():
    """Tests low-latency STT transcription and TTS audio synthesis."""
    interruption_controller.reset_interruption()
    stt_res = stt_engine.transcribe_audio("audio_base64")

    assert len(stt_res.transcript) > 0
    assert stt_res.latency_ms < 250.0  # Latency optimized

    tts_res = tts_engine.synthesize_speech(TTSRequest(text="JARVIS Audio Synthesis Test"))
    assert len(tts_res.audio_base64) > 10
    assert tts_res.latency_ms < 300.0


@pytest.mark.asyncio
async def test_speech_interruption_barge_in():
    """Verifies interruption trigger halts active TTS audio synthesis."""
    interruption_controller.reset_interruption()
    assert interruption_controller.is_interrupted() is False

    # Trigger Interruption (barge-in)
    interruption_controller.trigger_interruption()
    assert interruption_controller.is_interrupted() is True

    # Synthesize speech during interruption
    tts_res = tts_engine.synthesize_speech(TTSRequest(text="Halting synthesis"))
    assert tts_res.audio_base64 == ""  # Halted!

    interruption_controller.reset_interruption()


@pytest.mark.asyncio
async def test_voice_profiles():
    """Tests voice profile creation and activation."""
    profiles = voice_profile_store.list_profiles()
    assert len(profiles) >= 3

    new_prof = voice_profile_store.create_profile("Custom Deep Voice", pitch=0.8, speed=1.1)
    assert new_prof.name == "Custom Deep Voice"

    activated = voice_profile_store.set_active(new_prof.profile_id)
    assert activated.is_active is True


@pytest.mark.asyncio
async def test_full_voice_interaction_manager():
    """Tests end-to-end Voice Assistant interaction loop and latency metrics."""
    req = VoiceInteractionRequest(text_prompt="Hey JARVIS, run diagnostic check.")
    resp = await voice_manager.interact_voice(req)

    assert resp.transcript == "Hey JARVIS, run diagnostic check."
    assert len(resp.response_text) > 0
    assert len(resp.audio_base64) > 10
    assert resp.latency_ms > 0.0


@pytest.mark.asyncio
async def test_voice_api_endpoints(client: AsyncClient):
    """Tests FastAPI REST endpoints for Voice Assistant."""
    # Register & login
    await client.post("/api/v1/auth/register", json={"email": "voice@jarvis.ai", "password": "Password123!", "full_name": "Voice User"})
    login_resp = await client.post("/api/v1/auth/login", data={"username": "voice@jarvis.ai", "password": "Password123!"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Full Voice Interaction Endpoint
    int_resp = await client.post("/api/v1/voice/interact", json={"text_prompt": "Hey JARVIS, status report"}, headers=headers)
    assert int_resp.status_code == 200
    assert "audio_base64" in int_resp.json()

    # Detect Wake Word Endpoint
    ww_resp = await client.post("/api/v1/voice/detect-wakeword?transcript=Hey+JARVIS", headers=headers)
    assert ww_resp.status_code == 200
    assert ww_resp.json()["detected"] is True

    # Interrupt Endpoint
    ir_resp = await client.post("/api/v1/voice/interrupt", headers=headers)
    assert ir_resp.status_code == 200

    # Profiles Endpoint
    prof_resp = await client.get("/api/v1/voice/profiles", headers=headers)
    assert prof_resp.status_code == 200
    assert len(prof_resp.json()) >= 3
