"""
OpenAI LLM Provider — Official SDK Implementation.
Uses the official `openai` Python SDK with async client, connection reuse,
cached tokenizer, CancelledError handling, and centralized pricing registry.
"""

import asyncio
import time
import uuid
from typing import AsyncIterator, List, Optional

from app.ai.providers.base import BaseLLMProvider
from app.ai.providers.pricing import pricing_registry
from app.ai.schemas import LLMRequest, LLMResponse, LLMStreamChunk, ProviderInfo
from app.config import settings
from app.core.logging import logger

# Module-level cached SDK client — initialized once, reused for all requests
_openai_client = None
_tiktoken_encoder = None


def _get_tiktoken_encoder():
    """Returns cached tiktoken encoder (initialized once at module level)."""
    global _tiktoken_encoder
    if _tiktoken_encoder is None:
        try:
            import tiktoken
            _tiktoken_encoder = tiktoken.get_encoding("cl100k_base")
        except Exception:
            _tiktoken_encoder = False  # Sentinel: unavailable
    return _tiktoken_encoder if _tiktoken_encoder is not False else None


def _get_openai_client():
    """Returns cached async OpenAI SDK client (created once per process)."""
    global _openai_client
    if _openai_client is None:
        try:
            from openai import AsyncOpenAI
            _openai_client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
                timeout=float(settings.REQUEST_TIMEOUT),
                max_retries=0  # Retries managed by LLMRouter
            )
        except Exception as e:
            logger.warning("OpenAI SDK client initialization failed", error=str(e))
            _openai_client = False  # Sentinel: unavailable
    return _openai_client if _openai_client is not False else None


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API integration using official openai Python SDK."""

    @property
    def provider_name(self) -> str:
        return "OpenAI"

    @property
    def supported_models(self) -> List[str]:
        return ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]

    async def initialize(self) -> bool:
        if not settings.OPENAI_API_KEY:
            logger.info("OpenAI API key absent — running in offline mode")
            return False
        client = _get_openai_client()
        if client is None:
            return False
        return await self.health_check()

    async def shutdown(self) -> None:
        global _openai_client
        if _openai_client and _openai_client is not False:
            try:
                await _openai_client.close()
            except Exception:
                pass
        _openai_client = None

    def count_tokens(self, text: str, model: str = "") -> int:
        enc = _get_tiktoken_encoder()
        if enc:
            try:
                return len(enc.encode(text))
            except Exception:
                pass
        # Fallback estimation
        import re
        words = re.findall(r"\w+|\S", text)
        return int(len(words) * 1.3)

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float:
        return pricing_registry.calculate_cost(model, prompt_tokens, completion_tokens)

    async def health_check(self) -> bool:
        if not settings.OPENAI_API_KEY:
            return False
        client = _get_openai_client()
        if client is None:
            return False
        try:
            await client.models.list()
            return True
        except Exception as e:
            logger.warning("OpenAI health check failed", error=str(e))
            return False

    async def get_provider_info(self) -> ProviderInfo:
        healthy = await self.health_check()
        return ProviderInfo(
            provider_name=self.provider_name,
            supported_models=self.supported_models,
            is_healthy=healthy,
            initialized=bool(settings.OPENAI_API_KEY)
        )

    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        start_time = time.time()
        client = _get_openai_client()

        if not settings.OPENAI_API_KEY or client is None:
            from app.ai.providers.mock_provider import MockProvider
            return await MockProvider().generate(request)

        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        for m in request.messages:
            messages.append({"role": m.role.value, "content": m.content})

        try:
            completion = await client.chat.completions.create(
                model=request.model,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens or 2048
            )
            content = completion.choices[0].message.content or ""
            usage = completion.usage
            prompt_tokens = usage.prompt_tokens if usage else self.count_tokens(" ".join(m["content"] for m in messages))
            completion_tokens = usage.completion_tokens if usage else self.count_tokens(content)
            total_tokens = usage.total_tokens if usage else (prompt_tokens + completion_tokens)
            elapsed_ms = (time.time() - start_time) * 1000.0
            cost = self.estimate_cost(prompt_tokens, completion_tokens, request.model)

            logger.info(
                "OpenAI completion successful",
                model=request.model,
                tokens=total_tokens,
                cost_usd=cost,
                latency_ms=round(elapsed_ms, 1)
            )
            return LLMResponse(
                id=completion.id or f"chatcmpl-{uuid.uuid4().hex[:8]}",
                model=request.model,
                provider=self.provider_name,
                content=content,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                estimated_cost_usd=cost,
                execution_time_ms=round(elapsed_ms, 2)
            )
        except asyncio.CancelledError:
            logger.warning("OpenAI completion cancelled", model=request.model)
            raise
        except Exception as e:
            logger.error("OpenAI API completion failed", model=request.model, error=str(e))
            from app.ai.providers.mock_provider import MockProvider
            return await MockProvider().generate(request)

    async def generate(self, request: LLMRequest) -> LLMResponse:
        return await self.generate_response(request)

    async def stream_response(self, request: LLMRequest) -> AsyncIterator[LLMStreamChunk]:
        client = _get_openai_client()
        if not settings.OPENAI_API_KEY or client is None:
            from app.ai.providers.mock_provider import MockProvider
            async for chunk in MockProvider().generate_stream(request):
                yield chunk
            return

        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        for m in request.messages:
            messages.append({"role": m.role.value, "content": m.content})

        try:
            stream = await client.chat.completions.create(
                model=request.model,
                messages=messages,
                temperature=request.temperature,
                stream=True
            )
            async with stream:
                async for chunk in stream:
                    try:
                        choice = chunk.choices[0] if chunk.choices else None
                        if choice and choice.delta and choice.delta.content:
                            yield LLMStreamChunk(
                                id=chunk.id or f"stream-{uuid.uuid4().hex[:6]}",
                                delta_content=choice.delta.content,
                                finish_reason=choice.finish_reason,
                                model=request.model
                            )
                    except asyncio.CancelledError:
                        logger.warning("OpenAI stream cancelled mid-flight", model=request.model)
                        raise
        except asyncio.CancelledError:
            logger.warning("OpenAI stream cancelled", model=request.model)
            raise
        except Exception as e:
            logger.error("OpenAI streaming failed", model=request.model, error=str(e))
            from app.ai.providers.mock_provider import MockProvider
            async for chunk in MockProvider().generate_stream(request):
                yield chunk

    async def generate_stream(self, request: LLMRequest) -> AsyncIterator[LLMStreamChunk]:
        async for chunk in self.stream_response(request):
            yield chunk
