"""
Abstract Base LLM Provider Protocol.
Enforces common contract for all LLM Provider integrations.
"""

from abc import ABC, abstractmethod
from typing import AsyncIterator, List
from app.ai.schemas import LLMRequest, LLMResponse, LLMStreamChunk, ProviderInfo


class BaseLLMProvider(ABC):
    """Abstract interface that all LLM providers must implement."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Unique provider identifier name."""
        pass

    @property
    @abstractmethod
    def supported_models(self) -> List[str]:
        """List of model identifiers supported by provider."""
        pass

    @abstractmethod
    async def initialize(self) -> bool:
        """Initializes provider client and validates credentials."""
        pass

    @abstractmethod
    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        """Performs non-streaming completion request."""
        pass

    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Backward-compatible alias for non-streaming completion."""
        pass

    @abstractmethod
    async def stream_response(self, request: LLMRequest) -> AsyncIterator[LLMStreamChunk]:
        """Performs real-time streaming completion emitting SSE chunks."""
        pass

    @abstractmethod
    async def generate_stream(self, request: LLMRequest) -> AsyncIterator[LLMStreamChunk]:
        """Backward-compatible alias for streaming completion."""
        pass

    @abstractmethod
    def count_tokens(self, text: str, model: str = "") -> int:
        """Counts or estimates token count for input text."""
        pass

    @abstractmethod
    def estimate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float:
        """Estimates USD financial cost for token usage."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Pings provider API endpoint to verify connectivity and credentials."""
        pass

    @abstractmethod
    async def get_provider_info(self) -> ProviderInfo:
        """Returns structured metadata payload for provider telemetry."""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Gracefully closes active HTTP client sessions and connection pools."""
        pass
