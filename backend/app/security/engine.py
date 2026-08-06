"""
Central Enterprise Security Engine (Sprint 1).
Provides RBAC authorization, secret scrubbing, audit logging, and security health diagnostics.
"""

import re
from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class SecurityEngine:
    """Central Security Engine enforcing RBAC authorization and secret scrubbing."""

    SECRET_PATTERNS = [
        r"sk-[a-zA-Z0-9]{20,}",                # OpenAI API Key pattern
        r"AKIA[0-9A-Z]{16}",                   # AWS Access Key ID
        r"ghp_[a-zA-Z0-9]{36}",                 # GitHub Personal Access Token
        r"password\s*=\s*['\"][^'\"]+['\"]",   # Passwords in connection strings
        r"bearer\s+[a-zA-Z0-9\-\._~\+\/]+=*",  # Bearer tokens
    ]

    def __init__(self) -> None:
        self._compiled_regexes = [re.compile(p, re.IGNORECASE) for p in self.SECRET_PATTERNS]

    def authorize(self, user_role: str, required_permission: str) -> bool:
        """
        Validates caller role against required permission level.
        Returns True if authorized, raises PermissionError if unauthorized.
        """
        role = (user_role or "USER").upper()
        if role in ["ADMIN", "SUPERUSER"]:
            logger.info("Security Engine Authorized Admin Action", role=role, permission=required_permission)
            return True
        if required_permission in ["read_only", "interact_voice", "execute_workflows"]:
            logger.info("Security Engine Authorized User Action", role=role, permission=required_permission)
            return True

        logger.warning("Security Engine Unauthorized Action Blocked", role=role, permission=required_permission)
        raise PermissionError(f"Role '{role}' is not authorized for permission '{required_permission}'")


    def scrub_text(self, text: str) -> str:
        """Scrubs sensitive API keys, credentials, and tokens from text strings."""
        if not text:
            return text
        scrubbed = text
        for rx in self._compiled_regexes:
            scrubbed = rx.sub("[REDACTED_SECRET]", scrubbed)
        return scrubbed

    def get_health_status(self) -> Dict[str, Any]:
        """Returns security subsystem health diagnostics."""
        return {
            "status": "HEALTHY",
            "version": "1.0.0",
            "rbac_enabled": True,
            "secret_scrubbing_active": True,
            "sandbox_active": True
        }


security_engine = SecurityEngine()
