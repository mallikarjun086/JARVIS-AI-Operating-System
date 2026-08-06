"""
Tool Parameter & Output Validation Engine.
Validates Pydantic schemas, parameter size limits, file path safety, command security policy rules.
"""

import os
import re
from pathlib import Path
from typing import Any, Dict
from pydantic import BaseModel, ValidationError
from app.tools.base import BaseTool

# Forbidden command patterns for shell executions
FORBIDDEN_COMMAND_PATTERNS = [
    r"\brm\s+-rf\s+/",
    r"\bmkfs\b",
    r"\bdd\b.*if=/dev/",
    r":\(\)\{\s*:\|\:&\s*\};:",  # Fork bomb
    r"\bchmod\s+-R\s+777\b",
]

# Max parameter payload size (10MB)
MAX_PARAMETER_SIZE_BYTES = 10 * 1024 * 1024


class ToolValidationEngine:
    """
    Validation engine evaluating input/output schemas, safety constraints, size limits, and security policies.
    """

    @classmethod
    def validate_input(cls, tool: BaseTool, raw_params: Dict[str, Any]) -> BaseModel:
        """
        Validates input payload against Pydantic schema, size limits, and security constraints.
        """
        # 1. Size Limit Check
        params_str = str(raw_params)
        if len(params_str.encode("utf-8")) > MAX_PARAMETER_SIZE_BYTES:
            raise ValueError(f"Parameter payload size exceeds maximum limit ({MAX_PARAMETER_SIZE_BYTES} bytes).")

        # 2. Command Safety Check
        if "command" in raw_params and isinstance(raw_params["command"], str):
            cls._validate_command_safety(raw_params["command"])

        # 3. Path Traversal & Existence Check (if path param present)
        for path_key in ("path", "file_path", "filepath", "dir_path"):
            if path_key in raw_params and isinstance(raw_params[path_key], str):
                cls._validate_path_safety(raw_params[path_key], check_exists=("read" in tool.name or "list" in tool.name))

        # 4. Pydantic Schema Validation
        try:
            return tool.input_schema.model_validate(raw_params)
        except ValidationError as ve:
            raise ValueError(f"Input validation schema error for tool '{tool.name}': {ve}")

    @classmethod
    def validate_output(cls, tool: BaseTool, raw_output: Any) -> BaseModel:
        """Validates output payload against tool's output schema."""
        try:
            if isinstance(raw_output, tool.output_schema):
                return raw_output
            if isinstance(raw_output, dict):
                return tool.output_schema.model_validate(raw_output)
            return tool.output_schema.model_validate({"result": raw_output})
        except ValidationError as ve:
            raise ValueError(f"Output validation schema error for tool '{tool.name}': {ve}")

    @classmethod
    def _validate_command_safety(cls, command: str) -> None:
        """Checks shell commands against forbidden security vulnerability patterns."""
        for pattern in FORBIDDEN_COMMAND_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                raise ValueError(f"Command execution rejected by security policy (matches forbidden pattern: '{pattern}').")

    @classmethod
    def _validate_path_safety(cls, path_str: str, check_exists: bool = False) -> None:
        """Checks for path traversal vulnerabilities and optional existence."""
        if ".." in path_str and (os.path.isabs(path_str) or ".." in Path(path_str).parts):
            # Check for suspicious parent directory traversal
            resolved = Path(path_str).resolve()
            # Allow workspace paths
            if not str(resolved).startswith(os.getcwd()) and not str(resolved).startswith(str(Path.home())):
                raise ValueError(f"Path traversal security policy violation for path: '{path_str}'")

        if check_exists:
            p = Path(path_str)
            if not p.exists():
                raise ValueError(f"File or directory does not exist: '{path_str}'")


validator_engine = ToolValidationEngine()
schema_validator = validator_engine  # Backward-compatible alias
