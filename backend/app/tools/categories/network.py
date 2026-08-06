"""
Network Tools Category (WebSearchTool, HttpRequestTool).
"""

from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel, Field
from app.tools.base import BaseTool
from app.tools.schemas import PermissionLevel


class WebSearchInput(BaseModel):
    query: str = Field(..., description="Search query string")
    max_results: int = Field(default=5, ge=1, le=20)

class SearchResultItem(BaseModel):
    title: str
    snippet: str
    url: str

class WebSearchOutput(BaseModel):
    query: str
    results: List[SearchResultItem]

class HttpRequestInput(BaseModel):
    url: str = Field(..., description="Target HTTP/HTTPS URL")
    method: str = Field(default="GET", description="HTTP Method (GET, POST, etc.)")
    headers: Optional[Dict[str, str]] = Field(default=None)

class HttpRequestOutput(BaseModel):
    status_code: int
    content: str
    headers: Dict[str, str]


class WebSearchTool(BaseTool):
    @property
    def name(self) -> str: return "network.web_search"
    @property
    def description(self) -> str: return "Performs real-time web search for information lookup."
    @property
    def category(self) -> str: return "network"
    @property
    def permission_level(self) -> PermissionLevel: return PermissionLevel.NETWORK
    @property
    def input_schema(self): return WebSearchInput
    @property
    def output_schema(self): return WebSearchOutput

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        q = params["query"]
        return {
            "query": q,
            "results": [
                {
                    "title": f"Results for '{q}'",
                    "snippet": f"Simulated intelligence search result snippet for '{q}'.",
                    "url": "https://search.jarvis.ai/result"
                }
            ]
        }


class HttpRequestTool(BaseTool):
    @property
    def name(self) -> str: return "network.http_request"
    @property
    def description(self) -> str: return "Makes an HTTP request to a target web URL."
    @property
    def category(self) -> str: return "network"
    @property
    def permission_level(self) -> PermissionLevel: return PermissionLevel.NETWORK
    @property
    def input_schema(self): return HttpRequestInput
    @property
    def output_schema(self): return HttpRequestOutput

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        url = params["url"]
        method = params.get("method", "GET").upper()
        headers = params.get("headers") or {}

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.request(method, url, headers=headers)
            return {
                "status_code": resp.status_code,
                "content": resp.text[:2000],  # Truncate content
                "headers": dict(resp.headers)
            }
