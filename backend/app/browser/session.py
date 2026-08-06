"""
Session Persistence Manager — Saves and restores Playwright storageState, cookies, and local/session storage profiles.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import structlog
from app.browser.schemas import SessionProfile

logger = structlog.get_logger(__name__)


class SessionManager:
    """Manages browser cookie, storageState, and persistent profile storage on disk."""

    def __init__(self, storage_dir: str = "./browser_sessions") -> None:
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _profile_path(self, profile_name: str) -> Path:
        safe_name = "".join(c for c in profile_name if c.isalnum() or c in ("-", "_")).lower()
        return self.storage_dir / f"{safe_name}.json"

    def save_session(
        self,
        profile_name: str,
        cookies: List[Dict[str, Any]],
        local_storage: Optional[Dict[str, Any]] = None,
        session_storage: Optional[Dict[str, Any]] = None
    ) -> SessionProfile:
        """Saves session cookies and storage states to profile JSON file."""
        profile = SessionProfile(
            profile_name=profile_name,
            cookies=cookies,
            local_storage=local_storage or {},
            session_storage=session_storage or {}
        )
        path = self._profile_path(profile_name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(profile.model_dump_json(indent=2))

        logger.info("Saved browser session profile", profile_name=profile_name, path=str(path))
        return profile

    def load_session(self, profile_name: str) -> Optional[SessionProfile]:
        """Loads persistent session profile from disk."""
        path = self._profile_path(profile_name)
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return SessionProfile.model_validate(data)
        except Exception as e:
            logger.error("Failed to load browser session profile", profile_name=profile_name, error=str(e))
            return None

    def list_profiles(self) -> List[str]:
        """Lists available saved profile names."""
        return [p.stem for p in self.storage_dir.glob("*.json")]

    def delete_profile(self, profile_name: str) -> bool:
        """Deletes saved profile file."""
        path = self._profile_path(profile_name)
        if path.exists():
            path.unlink()
            return True
        return False


session_manager = SessionManager()
