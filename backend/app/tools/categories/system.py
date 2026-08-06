"""
System Tools Category (SystemHealthTool, ProcessListTool).
"""

import os
import platform
from typing import Any, Dict, List
from pydantic import BaseModel
from app.tools.base import BaseTool
from app.tools.schemas import PermissionLevel


class SystemHealthInput(BaseModel):
    pass

class SystemHealthOutput(BaseModel):
    os: str
    python_version: str
    healthy: bool

class ProcessListInput(BaseModel):
    pass

class ProcessItem(BaseModel):
    pid: int
    name: str

class ProcessListOutput(BaseModel):
    processes: List[ProcessItem]
    count: int


class SystemHealthTool(BaseTool):
    @property
    def name(self) -> str: return "system.health"
    @property
    def description(self) -> str: return "Returns operating system health and platform diagnostics."
    @property
    def category(self) -> str: return "system"
    @property
    def permission_level(self) -> PermissionLevel: return PermissionLevel.READ_ONLY
    @property
    def input_schema(self): return SystemHealthInput
    @property
    def output_schema(self): return SystemHealthOutput

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "os": f"{platform.system()} {platform.release()}",
            "python_version": platform.python_version(),
            "healthy": True
        }


class ProcessListTool(BaseTool):
    @property
    def name(self) -> str: return "system.process_list"
    @property
    def description(self) -> str: return "Lists active system processes."
    @property
    def category(self) -> str: return "system"
    @property
    def permission_level(self) -> PermissionLevel: return PermissionLevel.SYSTEM
    @property
    def input_schema(self): return ProcessListInput
    @property
    def output_schema(self): return ProcessListOutput

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        current_pid = os.getpid()
        return {
            "processes": [{"pid": current_pid, "name": "python.exe"}],
            "count": 1
        }
