"""
Google Gemini LLM Provider — Official SDK Implementation.
Uses the official `google-generativeai` Python SDK with async client, connection reuse,
usageMetadata token reading, systemInstruction support, CancelledError handling,
and centralized pricing registry.
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

# Module-level cached Gemini model client instances
_gemini_models: dict = {}
_gemini_initialized: bool = False


def _ensure_gemini_configured() -> bool:
    """Configures the Gemini SDK once using the API key from settings."""
    global _gemini_initialized
    if _gemini_initialized:
        return True
    if not settings.GEMINI_API_KEY:
        return False
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _gemini_initialized = True
        return True
    except Exception as e:
        logger.warning("Gemini SDK configuration failed", error=str(e))
        return False


def _get_gemini_model(model_name: str):
    """Returns a cached GenerativeModel instance for the given model name."""
    if not _ensure_gemini_configured():
        return None
    if model_name not in _gemini_models:
        try:
            import google.generativeai as genai
            _gemini_models[model_name] = genai.GenerativeModel(model_name)
        except Exception as e:
            logger.warning("Gemini model instantiation failed", model=model_name, error=str(e))
            return None
    return _gemini_models.get(model_name)


def _build_gemini_model_with_system(model_name: str, system_instruction: Optional[str]):
    """Builds a GenerativeModel with optional system_instruction."""
    if not _ensure_gemini_configured():
        return None
    try:
        import google.generativeai as genai
        if system_instruction:
            return genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system_instruction
            )
        return _get_gemini_model(model_name)
    except Exception as e:
        logger.warning("Gemini model with system instruction failed", error=str(e))
        return None


class GeminiProvider(BaseLLMProvider):
    """Google Gemini API integration using official google-generativeai Python SDK."""

    @property
    def provider_name(self) -> str:
        return "Gemini"

    @property
    def supported_models(self) -> List[str]:
        return ["gemini-1.5-pro", "gemini-1.5-flash"]

    async def initialize(self) -> bool:
        if not settings.GEMINI_API_KEY:
            logger.info("Gemini API key absent — running in offline mode")
            return False
        return _ensure_gemini_configured() and await self.health_check()

    async def shutdown(self) -> None:
        global _gemini_models, _gemini_initialized
        _gemini_models.clear()
        _gemini_initialized = False

    def count_tokens(self, text: str, model: str = "") -> int:
        """Word-based estimation; Gemini SDK token counting is sync-only and expensive."""
        words = re.findall(r"\w+|\S", text)
        return int(len(words) * 1.3)

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float:
        return pricing_registry.calculate_cost(model, prompt_tokens, completion_tokens)

    async def health_check(self) -> bool:
        if not settings.GEMINI_API_KEY:
            return False
        if not _ensure_gemini_configured():
            return False
        try:
            import google.generativeai as genai
            models = list(genai.list_models())
            return len(models) > 0
        except Exception as e:
            logger.warning("Gemini health check failed", error=str(e))
            return False

    async def get_provider_info(self) -> ProviderInfo:
        healthy = await self.health_check()
        return ProviderInfo(
            provider_name=self.provider_name,
            supported_models=self.supported_models,
            is_healthy=healthy,
            initialized=bool(settings.GEMINI_API_KEY)
        )

    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        start_time = time.time()

        if not settings.GEMINI_API_KEY or not _ensure_gemini_configured():
            from app.ai.providers.mock_provider import MockProvider
            return await MockProvider().generate(request)

        model_name = request.model if "gemini" in request.model else "gemini-1.5-flash"

        # Build model — include systemInstruction if provided
        model = _build_gemini_model_with_system(model_name, request.system_prompt)
        if model is None:
            from app.ai.providers.mock_provider import MockProvider
            return await MockProvider().generate(request)

        # Build conversation history in Gemini format
        contents = []
        for m in request.messages:
            role = "user" if m.role.value == "user" else "model"
            contents.append({"role": role, "parts": [{"text": m.content}]})

        try:
            import google.generativeai as genai

            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: model.generate_content(contents)
            )

            text = response.text or ""
            elapsed_ms = (time.time() - start_time) * 1000.0

            # Read actual token counts from usageMetadata (never estimate if available)
            usage_meta = getattr(response, "usage_metadata", None)
            if usage_meta:
                prompt_tokens = getattr(usage_meta, "prompt_token_count", None) or self.count_tokens(" ".join(m.content for m in request.messages))
                completion_tokens = getattr(usage_meta, "candidates_token_count", None) or self.count_tokens(text)
                total_tokens = getattr(usage_meta, "total_token_count", None) or (prompt_tokens + completion_tokens)
            else:
                prompt_tokens = self.count_tokens(" ".join(m.content for m in request.messages))
                completion_tokens = self.count_tokens(text)
                total_tokens = prompt_tokens + completion_tokens

            cost = self.estimate_cost(prompt_tokens, completion_tokens, request.model)

            logger.info(
                "Gemini completion successful",
                model=request.model,
                tokens=total_tokens,
                cost_usd=cost,
                latency_ms=round(elapsed_ms, 1),
                usage_from_api=usage_meta is not None
            )

            return LLMResponse(
                id=f"gemini-{uuid.uuid4().hex[:8]}",
                model=request.model,
                provider=self.provider_name,
                content=text,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                estimated_cost_usd=cost,
                execution_time_ms=round(elapsed_ms, 2)
            )
        except asyncio.CancelledError:
            logger.warning("Gemini completion cancelled", model=request.model)
            raise
        except Exception as e:
            logger.error("Gemini API completion failed", model=request.model, error=str(e))
            from app.ai.providers.mock_provider import MockProvider
            return await MockProvider().generate(request)

    async def generate(self, request: LLMRequest) -> LLMResponse:
        return await self.generate_response(request)

    async def stream_response(self, request: LLMRequest) -> AsyncIterator[LLMStreamChunk]:
        if not settings.GEMINI_API_KEY or not _ensure_gemini_configured():
            from app.ai.providers.mock_provider import MockProvider
            async for chunk in MockProvider().generate_stream(request):
                yield chunk
            return

        model_name = request.model if "gemini" in request.model else "gemini-1.5-flash"
        model = _build_gemini_model_with_system(model_name, request.system_prompt)

        if model is None:
            from app.ai.providers.mock_provider import MockProvider
            async for chunk in MockProvider().generate_stream(request):
                yield chunk
            return

        contents = []
        for m in request.messages:
            role = "user" if m.role.value == "user" else "model"
            contents.append({"role": role, "parts": [{"text": m.content}]})

        stream_id = f"gemini-stream-{uuid.uuid4().hex[:6]}"
        try:
            def _generate_stream():
                return model.generate_content(contents, stream=True)

            stream = await asyncio.get_event_loop().run_in_executor(None, _generate_stream)

            for chunk in stream:
                try:
                    text = chunk.text if hasattr(chunk, "text") else ""
                    if text:
                        yield LLMStreamChunk(
                            id=stream_id,
                            delta_content=text,
                            finish_reason=None,
                            model=request.model
                        )
                except asyncio.CancelledError:
                    logger.warning("Gemini stream cancelled mid-flight", model=request.model)
                    raise
                except Exception:
                    continue

            # Final chunk with stop reason
            yield LLMStreamChunk(
                id=stream_id,
                delta_content="",
                finish_reason="stop",
                model=request.model
            )

        except asyncio.CancelledError:
            logger.warning("Gemini stream cancelled", model=request.model)
            raise
        except Exception as e:
            logger.error("Gemini streaming failed", model=request.model, error=str(e))
            from app.ai.providers.mock_provider import MockProvider
            async for chunk in MockProvider().generate_stream(request):
                yield chunk

    async def generate_stream(self, request: LLMRequest) -> AsyncIterator[LLMStreamChunk]:
        async for chunk in self.stream_response(request):
            yield chunk
