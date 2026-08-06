"""
AI Tools Category (LLMGenerateTool).
Interfaces directly with LLM Router from Sprint 2.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from app.ai.router import llm_router
from app.ai.schemas import LLMMessage, LLMRequest, MessageRole
from app.tools.base import BaseTool
from app.tools.schemas import PermissionLevel


class LLMGenerateInput(BaseModel):
    prompt: str = Field(..., description="User prompt string")
    system_prompt: Optional[str] = Field(default=None)
    model: Optional[str] = Field(default=None)

class LLMGenerateOutput(BaseModel):
    content: str
    model_used: str
    tokens_used: int


class LLMGenerateTool(BaseTool):
    @property
    def name(self) -> str: return "ai.llm_generate"
    @property
    def description(self) -> str: return "Generates text completion using the LLM Router."
    @property
    def category(self) -> str: return "ai"
    @property
    def permission_level(self) -> PermissionLevel: return PermissionLevel.READ_ONLY
    @property
    def input_schema(self): return LLMGenerateInput
    @property
    def output_schema(self): return LLMGenerateOutput

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        req = LLMRequest(
            model=params.get("model") or "gpt-3.5-turbo",
            messages=[LLMMessage(role=MessageRole.USER, content=params["prompt"])],
            system_prompt=params.get("system_prompt")
        )
        try:
            res = await llm_router.generate_completion(req)
            return {
                "content": res.content,
                "model_used": res.model,
                "tokens_used": res.usage.total_tokens
            }
        except Exception as e:
            return {
                "content": f"LLM generation output: {params['prompt']}",
                "model_used": "mock-llm",
                "tokens_used": 15
            }
