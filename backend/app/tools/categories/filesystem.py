"""
Filesystem Tools Category (ReadFileTool, WriteFileTool, ListDirectoryTool, DeleteFileTool).
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.tools.base import BaseTool
from app.tools.schemas import PermissionLevel


# Schemas
class ReadFileInput(BaseModel):
    path: str = Field(..., description="Absolute or relative file path to read")
    start_line: Optional[int] = Field(default=None, description="Optional start line offset")
    end_line: Optional[int] = Field(default=None, description="Optional end line offset")

class ReadFileOutput(BaseModel):
    content: str
    total_lines: int
    bytes_read: int

class WriteFileInput(BaseModel):
    path: str = Field(..., description="Destination file path")
    content: str = Field(..., description="Text content to write")
    append: bool = Field(default=False, description="True to append instead of overwrite")

class WriteFileOutput(BaseModel):
    path: str
    bytes_written: int
    message: str

class ListDirInput(BaseModel):
    path: str = Field(default=".", description="Target directory path")

class ListDirItem(BaseModel):
    name: str
    is_dir: bool
    size_bytes: int

class ListDirOutput(BaseModel):
    items: List[ListDirItem]
    total_count: int

class DeleteFileInput(BaseModel):
    path: str = Field(..., description="File path to delete")

class DeleteFileOutput(BaseModel):
    path: str
    deleted: bool
    message: str


# Tools
class ReadFileTool(BaseTool):
    @property
    def name(self) -> str: return "filesystem.read_file"
    @property
    def description(self) -> str: return "Reads content of a file with optional line range limits."
    @property
    def category(self) -> str: return "filesystem"
    @property
    def permission_level(self) -> PermissionLevel: return PermissionLevel.READ_ONLY
    @property
    def input_schema(self): return ReadFileInput
    @property
    def output_schema(self): return ReadFileOutput

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        p = Path(params["path"]).resolve()
        if not p.exists():
            raise FileNotFoundError(f"File not found: {params['path']}")
        
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        start = (params.get("start_line") or 1) - 1
        end = params.get("end_line") or len(lines)
        selected_lines = lines[max(0, start):min(len(lines), end)]
        content = "".join(selected_lines)

        return {
            "content": content,
            "total_lines": len(lines),
            "bytes_read": len(content.encode("utf-8"))
        }

class WriteFileTool(BaseTool):
    @property
    def name(self) -> str: return "filesystem.write_file"
    @property
    def description(self) -> str: return "Writes content to a file, creating parent directories if needed."
    @property
    def category(self) -> str: return "filesystem"
    @property
    def permission_level(self) -> PermissionLevel: return PermissionLevel.WRITE
    @property
    def input_schema(self): return WriteFileInput
    @property
    def output_schema(self): return WriteFileOutput

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        p = Path(params["path"]).resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        mode = "a" if params.get("append", False) else "w"
        content = params["content"]
        
        with open(p, mode, encoding="utf-8") as f:
            f.write(content)

        return {
            "path": str(p),
            "bytes_written": len(content.encode("utf-8")),
            "message": f"Successfully wrote {len(content)} characters to '{p.name}'"
        }

class ListDirectoryTool(BaseTool):
    @property
    def name(self) -> str: return "filesystem.list_dir"
    @property
    def description(self) -> str: return "Lists files and subdirectories inside target path."
    @property
    def category(self) -> str: return "filesystem"
    @property
    def permission_level(self) -> PermissionLevel: return PermissionLevel.READ_ONLY
    @property
    def input_schema(self): return ListDirInput
    @property
    def output_schema(self): return ListDirOutput

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        target = Path(params.get("path", ".")).resolve()
        if not target.exists() or not target.is_dir():
            raise NotADirectoryError(f"Directory not found: '{target}'")
        
        items = []
        for entry in os.scandir(target):
            try:
                stat = entry.stat()
                items.append({
                    "name": entry.name,
                    "is_dir": entry.is_dir(),
                    "size_bytes": stat.st_size if not entry.is_dir() else 0
                })
            except Exception:
                pass

        return {"items": items, "total_count": len(items)}

class DeleteFileTool(BaseTool):
    @property
    def name(self) -> str: return "filesystem.delete_file"
    @property
    def description(self) -> str: return "Deletes a specified file from the filesystem."
    @property
    def category(self) -> str: return "filesystem"
    @property
    def permission_level(self) -> PermissionLevel: return PermissionLevel.WRITE
    @property
    def input_schema(self): return DeleteFileInput
    @property
    def output_schema(self): return DeleteFileOutput

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        p = Path(params["path"]).resolve()
        if not p.exists():
            return {"path": str(p), "deleted": False, "message": "File does not exist."}
        if p.is_dir():
            raise IsADirectoryError("delete_file cannot delete directories.")
        
        p.unlink()
        return {"path": str(p), "deleted": True, "message": "File deleted successfully."}
