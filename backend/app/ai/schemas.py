"""
Typed Pydantic Schemas for AI Core Requests, Responses, and Model Metadata.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class LLMMessage(BaseModel):
    """Single message turn in conversation."""
    role: MessageRole
    content: str


class LLMRequest(BaseModel):
    """Unified completion request schema across all LLM providers."""
    model: str = Field(default="gpt-4o", description="Target model identifier")
    messages: List[LLMMessage] = Field(..., description="Conversation turn history")
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=1024, ge=1, le=4096)
    system_prompt: Optional[str] = Field(default=None, description="Optional system override prompt")
    stream: bool = Field(default=False, description="Enable Server-Sent Events (SSE) streaming")


class LLMResponse(BaseModel):
    """Unified completion response schema."""
    id: str
    model: str
    provider: str
    content: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost_usd: float
    execution_time_ms: float
    created_at: datetime = Field(default_factory=datetime.utcnow)


class LLMStreamChunk(BaseModel):
    """Single streaming chunk emitted during real-time generation."""
    id: str
    delta_content: str
    finish_reason: Optional[str] = None
    model: str


class ModelInfo(BaseModel):
    """Model registry metadata."""
    model_id: str
    provider: str
    name: str
    max_context_tokens: int
    input_cost_per_1k: float
    output_cost_per_1k: float


class CostMetrics(BaseModel):
    """Cumulative token and financial cost telemetry tracking."""
    total_requests: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0


class ProviderInfo(BaseModel):
    """Provider metadata payload."""
    provider_name: str
    supported_models: List[str]
    is_healthy: bool = True
    initialized: bool = True

