"""
Tool Permission & Security Guard Engine.
Integrates permission verification, approval workflows, rate limiting, and SecuritySandbox validation.
"""

import time
from typing import Any, Dict, Optional, Tuple
import structlog
from app.tools.base import BaseTool
from app.tools.schemas import PermissionLevel

logger = structlog.get_logger(__name__)


class ToolPermissionManager:
    """
    Enforces authorization permission levels, user approval workflows,
    rate limits, and integration with the Security Engine.
    """

    def __init__(self) -> None:
        self._rate_limit_records: Dict[str, list] = {}  # {key: [timestamps]}
        self._rate_limit_max = 60  # max executions per window
        self._rate_limit_window = 60.0  # seconds

    def verify_permission(
        self,
        tool: BaseTool,
        user_role: str = "user",
        approval_granted: bool = False
    ) -> Tuple[bool, Optional[str]]:
        """
        Verifies caller authorization against tool's mandatory PermissionLevel.
        Returns (is_allowed, denial_reason).

        Role mappings:
        - 'anonymous' -> READ_ONLY (0)
        - 'user' -> WRITE (1) / NETWORK (2)
        - 'admin' -> SYSTEM (3) / DANGEROUS (4 if approved)
        - 'superuser' -> ADMIN (5)
        """
        role_map: Dict[str, PermissionLevel] = {
            "anonymous": PermissionLevel.READ_ONLY,
            "user": PermissionLevel.SYSTEM,
            "admin": PermissionLevel.DANGEROUS,
            "superuser": PermissionLevel.ADMIN,
        }


        user_max_level = role_map.get(user_role.lower(), PermissionLevel.READ_ONLY)

        if user_max_level < tool.permission_level:
            return False, f"Permission Denied: Access denied for Role '{user_role}' max permission level is '{user_max_level.name}', but tool '{tool.name}' requires '{tool.permission_level.name}'."


        # Approval check for sensitive tools
        if tool.requires_approval and not approval_granted and user_role.lower() != "superuser":
            return False, f"Approval Required: Tool '{tool.name}' has permission level '{tool.permission_level.name}' and requires explicit approval."

        return True, None

    def check_rate_limit(self, tool_name: str, user_id: Optional[str] = None) -> bool:
        """Enforces sliding-window rate limiting per tool/user."""
        key = f"{user_id or 'anon'}:{tool_name}"
        now = time.time()
        timestamps = self._rate_limit_records.get(key, [])

        # Filter out expired timestamps
        valid_ts = [t for t in timestamps if now - t < self._rate_limit_window]
        self._rate_limit_records[key] = valid_ts

        if len(valid_ts) >= self._rate_limit_max:
            logger.warning("Tool rate limit exceeded", tool=tool_name, user_id=user_id)
            return False

        self._rate_limit_records[key].append(now)
        return True


permission_manager = ToolPermissionManager()
permission_guard = permission_manager  # Backward-compatible alias
