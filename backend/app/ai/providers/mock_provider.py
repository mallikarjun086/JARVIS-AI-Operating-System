"""
Mock / Offline LLM Provider Implementation for Testing & Offline Executions.
"""

import asyncio
import time
import uuid
from typing import AsyncIterator, List
from app.ai.providers.base import BaseLLMProvider
from app.ai.providers.pricing import pricing_registry
from app.ai.schemas import LLMRequest, LLMResponse, LLMStreamChunk, ProviderInfo


class MockProvider(BaseLLMProvider):
    """Offline mock provider yielding deterministic completions and streams."""

    @property
    def provider_name(self) -> str:
        return "MockProvider"

    @property
    def supported_models(self) -> List[str]:
        return ["mock-gpt", "mock-claude", "mock-gemini"]

    async def initialize(self) -> bool:
        return True

    def count_tokens(self, text: str, model: str = "") -> int:
        return len(text.split()) * 2

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float:
        return pricing_registry.calculate_cost(model, prompt_tokens, completion_tokens)

    async def health_check(self) -> bool:
        return True

    async def get_provider_info(self) -> ProviderInfo:
        return ProviderInfo(
            provider_name=self.provider_name,
            supported_models=self.supported_models,
            is_healthy=True,
            initialized=True
        )

    async def shutdown(self) -> None:
        pass

    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        start_time = time.time()
        await asyncio.sleep(0.05)

        last_user_msg = request.messages[-1].content if request.messages else "Hello"
        content = f"[Mock AI Core Response] Received prompt: '{last_user_msg[:60]}...'. Execution successful."

        prompt_tokens = self.count_tokens(" ".join(m.content for m in request.messages))
        completion_tokens = self.count_tokens(content)
        total_tokens = prompt_tokens + completion_tokens
        elapsed_ms = (time.time() - start_time) * 1000.0

        return LLMResponse(
            id=f"mock-{uuid.uuid4().hex[:8]}",
            model=request.model,
            provider=self.provider_name,
            content=content,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            estimated_cost_usd=0.0,
            execution_time_ms=round(elapsed_ms, 2)
        )

    async def generate(self, request: LLMRequest) -> LLMResponse:
        return await self.generate_response(request)

    async def stream_response(self, request: LLMRequest) -> AsyncIterator[LLMStreamChunk]:
        resp_id = f"stream-{uuid.uuid4().hex[:8]}"
        last_user_msg = request.messages[-1].content if request.messages else "Hello"
        full_text = f"[Mock Streaming AI Response] Echoing query: '{last_user_msg}'."

        words = full_text.split(" ")
        for idx, word in enumerate(words):
            await asyncio.sleep(0.02)
            chunk_text = word + (" " if idx < len(words) - 1 else "")
            yield LLMStreamChunk(
                id=resp_id,
                delta_content=chunk_text,
                finish_reason="stop" if idx == len(words) - 1 else None,
                model=request.model
            )

    async def generate_stream(self, request: LLMRequest) -> AsyncIterator[LLMStreamChunk]:
        async for chunk in self.stream_response(request):
            yield chunk
