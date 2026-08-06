"""
Unit Tests for JARVIS Infrastructure Security Sandbox Guards.
"""

import pytest
from jarvis.domain.exceptions import SecurityViolationError
from jarvis.infrastructure.security.sandbox import SecuritySandbox


def test_sandbox_path_containment(sandbox: SecuritySandbox):
    """Verifies path boundary validation and path traversal prevention."""
    # Valid relative path inside workspace
    assert sandbox.validate_path("output.txt") is True
    assert sandbox.validate_path("data/store.json") is True

    # Invalid path traversal attempt
    with pytest.raises(SecurityViolationError):
        sandbox.validate_path("../../etc/passwd")


def test_sandbox_command_validation(sandbox: SecuritySandbox):
    """Verifies shell command whitelisting and malicious pattern blocking."""
    # Allowed command
    assert sandbox.validate_command("echo JARVIS_TEST") is True
    assert sandbox.validate_command("python --version") is True

    # Blocked dangerous pattern
    with pytest.raises(SecurityViolationError):
        sandbox.validate_command("rm -rf /")
