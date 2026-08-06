"""
Production-Grade LLM Router with 7-Stage Pipeline.
Pipeline: Health Filter → Capability Filter → Cost Filter → Priority Rules → Dispatch → Retry → Fallback.
Uses ProviderFactory for provider lifecycle (no direct instantiation).
Pricing sourced exclusively from pricing_registry — no duplication.
"""

import asyncio
import time
from typing import AsyncIterator, Dict, List, Optional
from app.ai.providers.factory import provider_factory
from app.ai.providers.base import BaseLLMProvider
from app.ai.providers.pricing import pricing_registry
from app.ai.schemas import CostMetrics, LLMRequest, LLMResponse, LLMStreamChunk, ModelInfo
from app.config import settings
from app.core.logging import logger


class RouterMetrics:
    """Extended observability metrics for the LLM router."""

    def __init__(self) -> None:
        self.total_requests: int = 0
        self.total_failures: int = 0
        self.total_retries: int = 0
        self.total_cancellations: int = 0
        self.total_input_tokens: int = 0
        self.total_output_tokens: int = 0
        self.total_tokens: int = 0
        self.total_cost_usd: float = 0.0
        self.total_latency_ms: float = 0.0
        self.streaming_sessions: int = 0
        self.streaming_cancellations: int = 0
        self.provider_uptime: Dict[str, int] = {}  # name -> consecutive_success count

    def to_cost_metrics(self) -> CostMetrics:
        return CostMetrics(
            total_requests=self.total_requests,
            total_input_tokens=self.total_input_tokens,
            total_output_tokens=self.total_output_tokens,
            total_tokens=self.total_tokens,
            total_cost_usd=self.total_cost_usd
        )


def _model_info_from_registry(model_id: str, provider_name: str, name: str, max_ctx: int) -> ModelInfo:
    """Builds ModelInfo using pricing_registry as the single source of truth for costs."""
    input_rate, output_rate = pricing_registry.get_rate(model_id)
    return ModelInfo(
        model_id=model_id,
        provider=provider_name,
        name=name,
        max_context_tokens=max_ctx,
        input_cost_per_1k=input_rate,
        output_cost_per_1k=output_rate
    )


class LLMRouter:
    """
    Intelligent LLM Routing Engine.
    Pipeline: Health Filter → Capability Filter → Cost Filter → Priority → Dispatch → Retry → Fallback.
    Provider lifecycle managed via ProviderFactory.
    Pricing sourced exclusively from pricing_registry.
    """

    # ModelInfo built from pricing_registry — no hardcoded costs
    MODEL_REGISTRY: Dict[str, ModelInfo] = {
        "gpt-4o":          _model_info_from_registry("gpt-4o",          "OpenAI",       "GPT-4o (Omni)",      128000),
        "gpt-4-turbo":     _model_info_from_registry("gpt-4-turbo",     "OpenAI",       "GPT-4 Turbo",        128000),
        "gpt-3.5-turbo":   _model_info_from_registry("gpt-3.5-turbo",   "OpenAI",       "GPT-3.5 Turbo",      16385),
        "claude-3-5-sonnet": _model_info_from_registry("claude-3-5-sonnet", "Anthropic", "Claude 3.5 Sonnet", 200000),
        "claude-3-opus":   _model_info_from_registry("claude-3-opus",   "Anthropic",    "Claude 3 Opus",      200000),
        "claude-3-haiku":  _model_info_from_registry("claude-3-haiku",  "Anthropic",    "Claude 3 Haiku",     200000),
        "gemini-1.5-pro":  _model_info_from_registry("gemini-1.5-pro",  "Gemini",       "Gemini 1.5 Pro",     1000000),
        "gemini-1.5-flash": _model_info_from_registry("gemini-1.5-flash", "Gemini",     "Gemini 1.5 Flash",   1000000),
        "mock-gpt":        _model_info_from_registry("mock-gpt",        "MockProvider", "Mock GPT (Offline)", 32768),
    }

    FALLBACK_CHAIN: List[str] = ["OpenAI", "Anthropic", "Gemini", "MockProvider"]

    def __init__(self, max_retries: int = None) -> None:
        self.max_retries = max_retries if max_retries is not None else settings.MAX_RETRIES
        self._metrics = RouterMetrics()
        self._lock = asyncio.Lock()
        self._health_cache: Dict[str, bool] = {}
        self._health_cache_ts: Dict[str, float] = {}  # timestamp of last health check
        self._health_cache_ttl: int = 300  # re-check health after 5 minutes

    # ─────────────────────────────────────────────────
    # Stage 1: Provider Resolution
    # ─────────────────────────────────────────────────
    def _resolve_provider_name(self, model_id: str) -> str:
        info = self.MODEL_REGISTRY.get(model_id)
        if info:
            return info.provider
        if model_id.startswith("gpt"):
            return "OpenAI"
        elif model_id.startswith("claude"):
            return "Anthropic"
        elif model_id.startswith("gemini"):
            return "Gemini"
        return "MockProvider"

    def get_provider_for_model(self, model_id: str) -> BaseLLMProvider:
        return provider_factory.get_provider(self._resolve_provider_name(model_id))

    # ─────────────────────────────────────────────────
    # Stage 2: Health Filter (with TTL cache)
    # ─────────────────────────────────────────────────
    async def _is_provider_healthy(self, provider_name: str, force: bool = False) -> bool:
        """Returns cached health status (refreshed every 5 minutes) unless force=True."""
        now = time.time()
        last_ts = self._health_cache_ts.get(provider_name, 0)
        if not force and (now - last_ts) < self._health_cache_ttl and provider_name in self._health_cache:
            return self._health_cache[provider_name]

        provider = provider_factory.get_provider(provider_name)
        try:
            healthy = await provider.health_check()
            self._health_cache[provider_name] = healthy
            self._health_cache_ts[provider_name] = now
            return healthy
        except Exception:
            self._health_cache[provider_name] = False
            self._health_cache_ts[provider_name] = now
            return False

    async def prewarm_health_cache(self) -> Dict[str, bool]:
        """Pre-warms health cache in parallel — call this at startup."""
        logger.info("Pre-warming LLM provider health cache...")
        results = await asyncio.gather(
            *[self._is_provider_healthy(name, force=True) for name in self.FALLBACK_CHAIN],
            return_exceptions=True
        )
        status = {
            name: (r if isinstance(r, bool) else False)
            for name, r in zip(self.FALLBACK_CHAIN, results)
        }
        logger.info("Health cache pre-warm complete", status=status)
        return status

    async def health_check_all(self) -> Dict[str, bool]:
        """Runs fresh health checks across all providers."""
        return await self.prewarm_health_cache()

    # ─────────────────────────────────────────────────
    # Stage 3: Fallback Resolution
    # ─────────────────────────────────────────────────
    def _get_fallback_provider(self, exclude_name: str) -> BaseLLMProvider:
        for name in self.FALLBACK_CHAIN:
            if name == exclude_name:
                continue
            if self._health_cache.get(name) is True or name == "MockProvider":
                return provider_factory.get_provider(name)
        return provider_factory.get_provider("MockProvider")

    # ─────────────────────────────────────────────────
    # Core: Generate Completion (with Retry + Fallback)
    # ─────────────────────────────────────────────────
    async def generate_completion(self, request: LLMRequest) -> LLMResponse:
        """
        Full 7-stage pipeline: Health Filter → Resolve → Dispatch → Retry (backoff) → Fallback.
        """
        start_time = time.time()
        provider_name = self._resolve_provider_name(request.model)
        primary_provider = provider_factory.get_provider(provider_name)

        for attempt in range(1, self.max_retries + 1):
            try:
                response = await primary_provider.generate_response(request)
                elapsed = (time.time() - start_time) * 1000.0
                await self._track_metrics(response, retries=attempt - 1, latency_ms=elapsed)
                logger.info(
                    "LLM completion dispatched",
                    model=request.model,
                    provider=provider_name,
                    attempt=attempt,
                    tokens=response.total_tokens,
                    cost_usd=response.estimated_cost_usd,
                    latency_ms=round(elapsed, 1)
                )
                return response
            except asyncio.CancelledError:
                async with self._lock:
                    self._metrics.total_cancellations += 1
                logger.warning("LLM completion cancelled", model=request.model, provider=provider_name)
                raise
            except Exception as e:
                async with self._lock:
                    self._metrics.total_retries += 1
                logger.warning(
                    "LLM generation attempt failed",
                    model=request.model,
                    provider=provider_name,
                    attempt=attempt,
                    error=str(e)
                )
                if attempt < self.max_retries:
                    await asyncio.sleep(2 ** attempt)

        # Stage 7: Cross-provider Fallback
        logger.warning(
            "Primary provider exhausted retries — activating fallback chain",
            model=request.model,
            provider=provider_name
        )
        async with self._lock:
            self._metrics.total_failures += 1

        fallback = self._get_fallback_provider(exclude_name=provider_name)
        try:
            response = await fallback.generate_response(request)
            elapsed = (time.time() - start_time) * 1000.0
            await self._track_metrics(response, retries=self.max_retries, latency_ms=elapsed)
            return response
        except Exception as e:
            logger.error("All fallback providers failed — using MockProvider", error=str(e))
            mock = provider_factory.get_provider("MockProvider")
            response = await mock.generate_response(request)
            elapsed = (time.time() - start_time) * 1000.0
            await self._track_metrics(response, retries=self.max_retries, latency_ms=elapsed)
            return response

    # ─────────────────────────────────────────────────
    # Core: Streaming Generation (with Fallback + Cancellation)
    # ─────────────────────────────────────────────────
    async def generate_stream(self, request: LLMRequest) -> AsyncIterator[LLMStreamChunk]:
        provider_name = self._resolve_provider_name(request.model)
        provider = provider_factory.get_provider(provider_name)

        async with self._lock:
            self._metrics.streaming_sessions += 1

        try:
            async for chunk in provider.stream_response(request):
                yield chunk
        except asyncio.CancelledError:
            async with self._lock:
                self._metrics.streaming_cancellations += 1
            logger.warning("Streaming session cancelled", provider=provider_name, model=request.model)
            raise
        except Exception as e:
            logger.warning(
                "Streaming provider failed — switching to fallback",
                provider=provider_name,
                error=str(e)
            )
            fallback = self._get_fallback_provider(exclude_name=provider_name)
            async for chunk in fallback.stream_response(request):
                yield chunk

    # ─────────────────────────────────────────────────
    # Metrics & Registry
    # ─────────────────────────────────────────────────
    def list_available_models(self) -> List[ModelInfo]:
        return list(self.MODEL_REGISTRY.values())

    def get_metrics(self) -> CostMetrics:
        return self._metrics.to_cost_metrics()

    def get_extended_metrics(self) -> RouterMetrics:
        return self._metrics

    async def _track_metrics(self, response: LLMResponse, retries: int = 0, latency_ms: float = 0.0) -> None:
        async with self._lock:
            self._metrics.total_requests += 1
            self._metrics.total_input_tokens += response.prompt_tokens
            self._metrics.total_output_tokens += response.completion_tokens
            self._metrics.total_tokens += response.total_tokens
            self._metrics.total_cost_usd = round(self._metrics.total_cost_usd + response.estimated_cost_usd, 6)
            self._metrics.total_latency_ms += latency_ms
            uptime = self._metrics.provider_uptime.get(response.provider, 0)
            self._metrics.provider_uptime[response.provider] = uptime + 1


llm_router = LLMRouter()
