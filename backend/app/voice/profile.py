"""
Voice Profile Management Engine (Sprint 11).
Manages customizable voice profiles (pitch, speed, timbre warmth, voice ID).
"""

from typing import List, Optional
import structlog

from app.voice.schemas import VoiceProfile

logger = structlog.get_logger(__name__)


class VoiceProfileStore:
    """Manages active and saved voice profiles."""

    def __init__(self) -> None:
        self._profiles: List[VoiceProfile] = [
            VoiceProfile(profile_id="vprof-1", name="JARVIS Deep Male", pitch=0.9, speed=1.0, timbre_warmth=0.9, voice_id="jarvis_male_deep", is_active=True),
            VoiceProfile(profile_id="vprof-2", name="JARVIS Glass Female", pitch=1.1, speed=1.05, timbre_warmth=0.7, voice_id="jarvis_female_glass", is_active=False),
            VoiceProfile(profile_id="vprof-3", name="Natural Assistant", pitch=1.0, speed=1.0, timbre_warmth=0.8, voice_id="natural_assistant", is_active=False),
        ]

    def list_profiles(self) -> List[VoiceProfile]:
        """Lists all voice profiles."""
        return list(self._profiles)

    def get_profile(self, profile_id: str) -> Optional[VoiceProfile]:
        """Retrieves voice profile by ID."""
        return next((p for p in self._profiles if p.profile_id == profile_id), None)

    def get_active_profile(self) -> VoiceProfile:
        """Returns active voice profile."""
        return next((p for p in self._profiles if p.is_active), self._profiles[0])

    def create_profile(
        self,
        name: str,
        pitch: float = 1.0,
        speed: float = 1.0,
        timbre_warmth: float = 0.8,
        voice_id: str = "custom"
    ) -> VoiceProfile:
        """Creates a new custom voice profile."""
        prof = VoiceProfile(name=name, pitch=pitch, speed=speed, timbre_warmth=timbre_warmth, voice_id=voice_id)
        self._profiles.append(prof)
        logger.info("Created new voice profile", profile_id=prof.profile_id, name=name)
        return prof

    def set_active(self, profile_id: str) -> Optional[VoiceProfile]:
        """Sets active voice profile by ID."""
        target = self.get_profile(profile_id)
        if target:
            for p in self._profiles:
                p.is_active = False
            target.is_active = True
            logger.info("Activated voice profile", profile_id=profile_id, name=target.name)
        return target


voice_profile_store = VoiceProfileStore()
