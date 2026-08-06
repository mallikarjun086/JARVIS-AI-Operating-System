"""
Terminal Tools Category (ExecuteCommandTool).
"""

import asyncio
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from app.tools.base import BaseTool
from app.tools.schemas import PermissionLevel


class ExecuteCommandInput(BaseModel):
    command: str = Field(..., description="Shell command string to execute")
    cwd: Optional[str] = Field(default=None, description="Optional working directory")

class ExecuteCommandOutput(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
    command: str


class ExecuteCommandTool(BaseTool):
    @property
    def name(self) -> str: return "terminal.execute_command"
    @property
    def description(self) -> str: return "Executes a shell command asynchronously and captures output."
    @property
    def category(self) -> str: return "terminal"
    @property
    def permission_level(self) -> PermissionLevel: return PermissionLevel.SYSTEM
    @property
    def input_schema(self): return ExecuteCommandInput
    @property
    def output_schema(self): return ExecuteCommandOutput

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        cmd = params["command"]
        cwd = params.get("cwd")

        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd
        )
        stdout, stderr = await proc.communicate()

        return {
            "stdout": stdout.decode("utf-8", errors="replace").strip(),
            "stderr": stderr.decode("utf-8", errors="replace").strip(),
            "exit_code": proc.returncode or 0,
            "command": cmd
        }
