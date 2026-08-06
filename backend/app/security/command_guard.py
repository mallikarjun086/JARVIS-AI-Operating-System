"""
Command Injection Validation & Sanitization Guard.
Inspects shell commands against dangerous injection patterns, tokenizes arguments, and sanitizes inputs.
"""

import re
import shlex
from typing import List, Tuple
from app.security.schemas import CommandValidationResult


class CommandValidationGuard:
    """Sanitizes, tokenizes, and inspects commands against shell injection vulnerabilities."""

    DANGEROUS_PATTERNS: List[Tuple[str, str]] = [
        (r"rm\s+-rf\s+/", "Destructive root directory deletion command detected"),
        (r";", "Command chaining semicolon detected"),
        (r"&&", "Logical AND command chaining detected"),
        (r"\|", "Pipe command chaining detected"),
        (r"\$\(.*\)", "Subshell command substitution $(...) detected"),
        (r"`.*`", "Backtick command substitution detected"),
        (r">\s*/dev/null", "Output redirection detected"),
        (r"Invoke-Expression", "PowerShell dangerous expression execution detected"),
    ]

    ALLOWED_EXECUTABLES = {
        "python", "python3", "pytest", "node", "npm", "npx",
        "git", "echo", "dir", "ls", "which", "where", "pip",
        "cat", "type", "mkdir", "whoami"
    }

    @classmethod
    def validate_command(cls, command: str) -> CommandValidationResult:
        """
        Inspects command string against dangerous patterns.
        Returns safety verdict and sanitized version.
        """
        flagged_reasons = []

        for pattern, reason in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                flagged_reasons.append(reason)

        is_safe = len(flagged_reasons) == 0
        sanitized = re.sub(r"[;&|`]", "", command).strip()

        return CommandValidationResult(
            command=command,
            is_safe=is_safe,
            flagged_reasons=flagged_reasons,
            sanitized_command=sanitized
        )

    @classmethod
    def tokenize_command(cls, command: str) -> List[str]:
        """
        Safely tokenizes a command string into an executable and argument array using shlex.
        Enables asyncio.create_subprocess_exec execution without shell interpolation.
        """
        try:
            tokens = shlex.split(command, posix=False)
            return [t.strip('"\'') for t in tokens if t]
        except Exception:
            return command.split()


command_guard = CommandValidationGuard()
