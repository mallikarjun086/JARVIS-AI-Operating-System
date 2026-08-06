"""
Anthropic Claude LLM Provider — Official SDK Implementation.
Uses the official `anthropic` Python SDK with async client, connection reuse,
fixed health check (HTTP 200 only), CancelledError handling, and centralized pricing.
"""

import asyncio
import re
import time
import uuid
from typing import AsyncIterator, List, Optional

from app.ai.providers.base import BaseLLMProvider
from app.ai.providers.pricing import pricing_registry
from app.ai.schemas import LLMRequest, LLMResponse, LLMStreamChunk, ProviderInfo
from app.config import settings
from app.core.logging import logger

# Module-level cached SDK client — initialized once, reused for all requests
_anthropic_client = None


def _get_anthropic_client():
    """Returns cached async Anthropic SDK client (created once per process)."""
    global _anthropic_client
    if _anthropic_client is None:
        try:
            import anthropic
            _anthropic_client = anthropic.AsyncAnthropic(
                api_key=settings.ANTHROPIC_API_KEY,
                timeout=float(settings.REQUEST_TIMEOUT),
                max_retries=0  # Retries managed by LLMRouter
            )
        except Exception as e:
            logger.warning("Anthropic SDK client initialization failed", error=str(e))
            _anthropic_client = False  # Sentinel: unavailable
    return _anthropic_client if _anthropic_client is not False else None


class AnthropicClaudeProvider(BaseLLMProvider):
    """Anthropic Claude API integration using official anthropic Python SDK."""

    @property
    def provider_name(self) -> str:
        return "Anthropic"

    @property
    def supported_models(self) -> List[str]:
        return ["claude-3-5-sonnet", "claude-3-opus", "claude-3-haiku"]

    async def initialize(self) -> bool:
        if not settings.ANTHROPIC_API_KEY:
            logger.info("Anthropic API key absent — running in offline mode")
            return False
        client = _get_anthropic_client()
        if client is None:
            return False
        return await self.health_check()

    async def shutdown(self) -> None:
        global _anthropic_client
        if _anthropic_client and _anthropic_client is not False:
            try:
                await _anthropic_client.close()
            except Exception:
                pass
        _anthropic_client = None

    def count_tokens(self, text: str, model: str = "") -> int:
        """Word-based estimation (Anthropic SDK token counting requires a separate API call)."""
        words = re.findall(r"\w+|\S", text)
        return int(len(words) * 1.3)

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float:
        return pricing_registry.calculate_cost(model, prompt_tokens, completion_tokens)

    async def health_check(self) -> bool:
        """
        Verifies connectivity by sending a minimal completion request.
        Only returns True on HTTP 200 — never accepts 400/404 as healthy.
        """
        if not settings.ANTHROPIC_API_KEY:
            return False
        client = _get_anthropic_client()
        if client is None:
            return False
        try:
            import anthropic
            await client.messages.create(
                model="claude-3-haiku",
                max_tokens=1,
                messages=[{"role": "user", "content": "ping"}]
            )
            return True
        except Exception as e:
            err_str = str(e)
            # anthropic SDK raises APIStatusError — we specifically allow only success
            logger.warning("Anthropic health check failed", error=err_str)
            return False

    async def get_provider_info(self) -> ProviderInfo:
        healthy = await self.health_check()
        return ProviderInfo(
            provider_name=self.provider_name,
            supported_models=self.supported_models,
            is_healthy=healthy,
            initialized=bool(settings.ANTHROPIC_API_KEY)
        )

    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        start_time = time.time()
        client = _get_anthropic_client()

        if not settings.ANTHROPIC_API_KEY or client is None:
            from app.ai.providers.mock_provider import MockProvider
            return await MockProvider().generate(request)

        # Anthropic separates system from turn messages
        messages = [
            {"role": m.role.value, "content": m.content}
            for m in request.messages
            if m.role.value != "system"
        ]
        system = request.system_prompt or ""

        try:
            resp = await client.messages.create(
                model=request.model,
                messages=messages,
                system=system,
                max_tokens=request.max_tokens or 1024,
                temperature=request.temperature
            )
            content = resp.content[0].text if resp.content else ""
            usage = resp.usage
            prompt_tokens = usage.input_tokens if usage else self.count_tokens(" ".join(m["content"] for m in messages))
            completion_tokens = usage.output_tokens if usage else self.count_tokens(content)
            total_tokens = prompt_tokens + completion_tokens
            elapsed_ms = (time.time() - start_time) * 1000.0
            cost = self.estimate_cost(prompt_tokens, completion_tokens, request.model)

            logger.info(
                "Anthropic completion successful",
                model=request.model,
                tokens=total_tokens,
                cost_usd=cost,
                latency_ms=round(elapsed_ms, 1)
            )
            return LLMResponse(
                id=resp.id or f"msg-{uuid.uuid4().hex[:8]}",
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
            logger.warning("Anthropic completion cancelled", model=request.model)
            raise
        except Exception as e:
            logger.error("Anthropic API completion failed", model=request.model, error=str(e))
            from app.ai.providers.mock_provider import MockProvider
            return await MockProvider().generate(request)

    async def generate(self, request: LLMRequest) -> LLMResponse:
        return await self.generate_response(request)

    async def stream_response(self, request: LLMRequest) -> AsyncIterator[LLMStreamChunk]:
        client = _get_anthropic_client()
        if not settings.ANTHROPIC_API_KEY or client is None:
            from app.ai.providers.mock_provider import MockProvider
            async for chunk in MockProvider().generate_stream(request):
                yield chunk
            return

        messages = [
            {"role": m.role.value, "content": m.content}
            for m in request.messages
            if m.role.value != "system"
        ]

        try:
            async with client.messages.stream(
                model=request.model,
                messages=messages,
                system=request.system_prompt or "",
                max_tokens=request.max_tokens or 1024,
                temperature=request.temperature
            ) as stream:
                async for text in stream.text_stream:
                    try:
                        yield LLMStreamChunk(
                            id=f"claude-stream-{uuid.uuid4().hex[:6]}",
                            delta_content=text,
                            finish_reason=None,
                            model=request.model
                        )
                    except asyncio.CancelledError:
                        logger.warning("Anthropic stream cancelled mid-flight", model=request.model)
                        raise
                # Emit final chunk with stop reason
                final = await stream.get_final_message()
                yield LLMStreamChunk(
                    id=f"claude-stream-final-{uuid.uuid4().hex[:4]}",
                    delta_content="",
                    finish_reason=final.stop_reason or "stop",
                    model=request.model
                )
        except asyncio.CancelledError:
            logger.warning("Anthropic stream cancelled", model=request.model)
            raise
        except Exception as e:
            logger.error("Anthropic streaming failed", model=request.model, error=str(e))
            from app.ai.providers.mock_provider import MockProvider
            async for chunk in MockProvider().generate_stream(request):
                yield chunk

    async def generate_stream(self, request: LLMRequest) -> AsyncIterator[LLMStreamChunk]:
        async for chunk in self.stream_response(request):
            yield chunk
