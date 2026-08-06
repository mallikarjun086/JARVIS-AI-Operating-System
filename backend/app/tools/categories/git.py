"""
Git Tools Category (GitStatusTool, GitLogTool).
"""

import asyncio
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.tools.base import BaseTool
from app.tools.schemas import PermissionLevel


class GitStatusInput(BaseModel):
    repo_path: Optional[str] = Field(default=".", description="Git repository working directory path")

class GitStatusOutput(BaseModel):
    status_output: str
    clean: bool

class GitLogInput(BaseModel):
    max_count: int = Field(default=5, ge=1, le=50)
    repo_path: Optional[str] = Field(default=".")

class GitLogOutput(BaseModel):
    log_output: str


class GitStatusTool(BaseTool):
    @property
    def name(self) -> str: return "git.status"
    @property
    def description(self) -> str: return "Checks repository git status."
    @property
    def category(self) -> str: return "git"
    @property
    def permission_level(self) -> PermissionLevel: return PermissionLevel.READ_ONLY
    @property
    def input_schema(self): return GitStatusInput
    @property
    def output_schema(self): return GitStatusOutput

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        cwd = params.get("repo_path") or "."
        proc = await asyncio.create_subprocess_shell(
            "git status -s",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd
        )
        stdout, _ = await proc.communicate()
        out = stdout.decode("utf-8").strip()
        return {"status_output": out or "Clean repository", "clean": len(out) == 0}


class GitLogTool(BaseTool):
    @property
    def name(self) -> str: return "git.log"
    @property
    def description(self) -> str: return "Fetches recent git commit log history."
    @property
    def category(self) -> str: return "git"
    @property
    def permission_level(self) -> PermissionLevel: return PermissionLevel.READ_ONLY
    @property
    def input_schema(self): return GitLogInput
    @property
    def output_schema(self): return GitLogOutput

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        n = params.get("max_count", 5)
        cwd = params.get("repo_path") or "."
        proc = await asyncio.create_subprocess_shell(
            f"git log -n {n} --oneline",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd
        )
        stdout, _ = await proc.communicate()
        return {"log_output": stdout.decode("utf-8").strip()}
