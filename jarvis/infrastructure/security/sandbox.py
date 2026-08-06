"""
Security Sandbox Infrastructure for Path Boundary and Command Execution Protection.
"""

from pathlib import Path
import re
from typing import List, Set
from jarvis.config import settings
from jarvis.domain.exceptions import SecurityViolationError
from jarvis.domain.ports import SecuritySandboxPort
from jarvis.infrastructure.logging.logger import get_logger

logger = get_logger("jarvis.security_sandbox")


class SecuritySandbox(SecuritySandboxPort):
    """
    Enforces isolation boundaries on file system paths and shell executions.
    """

    ALLOWED_COMMAND_PREFIXES: Set[str] = {
        "echo", "dir", "ls", "cat", "pwd", "python", "python3",
        "pytest", "git status", "git log", "whoami", "date", "time"
    }

    BLOCKED_PATTERNS: List[str] = [
        r"rm\s+-rf",
        r"format\s+",
        r"del\s+/f",
        r"del\s+/s",
        r"drop\s+database",
        r":\(\)\{\s*:\|:&\s*\};:",  # Fork bomb
        r"mkfs",
        r"shutdown"
    ]

    def __init__(self, workspace_root: Path | None = None) -> None:
        self.workspace_root = (workspace_root or settings.WORKSPACE_ROOT).resolve()

    def validate_path(self, target_path: str) -> bool:
        """
        Validates that target path is contained strictly within the workspace root.
        Raises SecurityViolationError if path attempts traversal outside boundaries.
        """
        try:
            resolved_target = (self.workspace_root / target_path).resolve()
            # Ensure workspace_root is parent or ancestor of resolved_target
            if not (resolved_target == self.workspace_root or self.workspace_root in resolved_target.parents):
                logger.error("Path traversal security violation", path=target_path, root=str(self.workspace_root))
                raise SecurityViolationError("File Access", target_path)
            return True
        except SecurityViolationError:
            raise
        except Exception as e:
            raise SecurityViolationError("Path Resolution", target_path) from e

    def validate_command(self, command: str) -> bool:
        """
        Validates shell command against security whitelists and blocked pattern lists.
        Raises SecurityViolationError if command is disallowed.
        """
        cmd_strip = command.strip().lower()

        # Check for blocked malicious patterns
        for pattern in self.BLOCKED_PATTERNS:
            if re.search(pattern, cmd_strip):
                logger.error("Blocked command security violation", command=command)
                raise SecurityViolationError("Command Execution", command)

        # Verify allowed prefixes
        is_allowed = any(cmd_strip.startswith(prefix) for prefix in self.ALLOWED_COMMAND_PREFIXES)
        if not is_allowed and not settings.ALLOW_SHELL_EXECUTION:
            logger.error("Disallowed command execution", command=command)
            raise SecurityViolationError("Command Execution", command)

        return True
