"""
Sprint 2.1 — AI Provider Layer Hardened Test Suite.
Covers: Pricing Registry, Provider Factory, All Providers, Conversation Manager (TTL/eviction),
LLM Router pipeline (health cache, retry, fallback, cancellation), streaming, request validation.
"""

import asyncio
import time
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock

from app.ai.providers.pricing import PricingRegistry, pricing_registry
from app.ai.providers.factory import ProviderFactory
from app.ai.providers.mock_provider import MockProvider
from app.ai.providers.openai_provider import OpenAIProvider
from app.ai.providers.claude_provider import AnthropicClaudeProvider
from app.ai.providers.gemini_provider import GeminiProvider
from app.ai.conversation import ConversationManager, ConversationSession
from app.ai.router import LLMRouter
from app.ai.schemas import LLMMessage, LLMRequest, LLMStreamChunk, MessageRole, ProviderInfo


# ──────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────

def make_request(model: str = "mock-gpt", content: str = "Hello JARVIS", stream: bool = False) -> LLMRequest:
    return LLMRequest(
        model=model,
        messages=[LLMMessage(role=MessageRole.USER, content=content)],
        stream=stream
    )


# ══════════════════════════════════════════════════════════════
# 1. Pricing Registry
# ══════════════════════════════════════════════════════════════

class TestPricingRegistry:

    def test_known_model_rates_gpt4o(self):
        input_rate, output_rate = PricingRegistry.get_rate("gpt-4o")
        assert input_rate == 0.005
        assert output_rate == 0.015

    def test_known_model_rates_claude_haiku(self):
        input_rate, output_rate = PricingRegistry.get_rate("claude-3-haiku")
        assert input_rate == 0.00025
        assert output_rate == 0.00125

    def test_known_model_rates_gemini_flash(self):
        input_rate, output_rate = PricingRegistry.get_rate("gemini-1.5-flash")
        assert input_rate > 0
        assert output_rate > 0

    def test_unknown_model_fallback_rate(self):
        input_rate, output_rate = PricingRegistry.get_rate("unknown-model-xyz")
        assert input_rate > 0
        assert output_rate > 0

    def test_calculate_cost_zero_for_mock(self):
        cost = PricingRegistry.calculate_cost("mock-gpt", 1000, 1000)
        assert cost == 0.0

    def test_calculate_cost_positive_for_gpt4o(self):
        cost = PricingRegistry.calculate_cost("gpt-4o", 1000, 500)
        expected = (1000 * 0.005 + 500 * 0.015) / 1000.0
        assert abs(cost - expected) < 0.000001

    def test_all_major_models_in_registry(self):
        models = ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo",
                  "claude-3-5-sonnet", "claude-3-opus", "claude-3-haiku",
                  "gemini-1.5-pro", "gemini-1.5-flash"]
        for model in models:
            rate = PricingRegistry.get_rate(model)
            assert len(rate) == 2, f"Missing rate entry for {model}"

    def test_singleton_instance(self):
        from app.ai.providers.pricing import pricing_registry as r1
        from app.ai.providers.pricing import pricing_registry as r2
        assert r1 is r2

    def test_cost_rounded_to_6_decimals(self):
        cost = PricingRegistry.calculate_cost("gpt-4o", 1, 1)
        assert isinstance(cost, float)
        assert len(str(cost).split(".")[-1]) <= 6


# ══════════════════════════════════════════════════════════════
# 2. Provider Factory
# ══════════════════════════════════════════════════════════════

class TestProviderFactory:

    def test_get_openai_provider(self):
        factory = ProviderFactory()
        provider = factory.get_provider("OpenAI")
        assert isinstance(provider, OpenAIProvider)

    def test_get_anthropic_provider(self):
        factory = ProviderFactory()
        provider = factory.get_provider("Anthropic")
        assert isinstance(provider, AnthropicClaudeProvider)

    def test_get_gemini_provider(self):
        factory = ProviderFactory()
        provider = factory.get_provider("Gemini")
        assert isinstance(provider, GeminiProvider)

    def test_get_mock_provider_for_unknown(self):
        factory = ProviderFactory()
        provider = factory.get_provider("SomeUnknownProvider")
        assert isinstance(provider, MockProvider)

    def test_singleton_caching(self):
        factory = ProviderFactory()
        p1 = factory.get_provider("OpenAI")
        p2 = factory.get_provider("OpenAI")
        assert p1 is p2

    def test_claude_alias(self):
        factory = ProviderFactory()
        p = factory.get_provider("Claude")
        assert isinstance(p, AnthropicClaudeProvider)

    async def test_shutdown_all_clears_instances(self):
        factory = ProviderFactory()
        factory.get_provider("OpenAI")
        factory.get_provider("Anthropic")
        await factory.shutdown_all()
        assert factory._instances == {}

    async def test_initialize_all_returns_dict(self):
        factory = ProviderFactory()
        with patch.object(OpenAIProvider, "initialize", new_callable=AsyncMock, return_value=False):
            with patch.object(AnthropicClaudeProvider, "initialize", new_callable=AsyncMock, return_value=False):
                with patch.object(GeminiProvider, "initialize", new_callable=AsyncMock, return_value=False):
                    status = await factory.initialize_all()
        assert isinstance(status, dict)
        assert "MockProvider" in status


# ══════════════════════════════════════════════════════════════
# 3. Mock Provider
# ══════════════════════════════════════════════════════════════

class TestMockProvider:

    async def test_initialize_returns_true(self):
        p = MockProvider()
        assert await p.initialize() is True

    async def test_health_check_returns_true(self):
        p = MockProvider()
        assert await p.health_check() is True

    async def test_generate_response_structure(self):
        p = MockProvider()
        req = make_request()
        resp = await p.generate_response(req)
        assert resp.content
        assert resp.provider == "MockProvider"
        assert resp.prompt_tokens > 0
        assert resp.completion_tokens > 0
        assert resp.execution_time_ms > 0

    async def test_stream_response_yields_chunks(self):
        p = MockProvider()
        req = make_request(stream=True)
        chunks = []
        async for chunk in p.stream_response(req):
            chunks.append(chunk)
        assert len(chunks) > 0
        assert all(isinstance(c, LLMStreamChunk) for c in chunks)
        assert chunks[-1].finish_reason == "stop"

    async def test_get_provider_info(self):
        p = MockProvider()
        info = await p.get_provider_info()
        assert isinstance(info, ProviderInfo)
        assert info.provider_name == "MockProvider"
        assert info.is_healthy is True
        assert len(info.supported_models) > 0

    def test_count_tokens_returns_positive(self):
        p = MockProvider()
        assert p.count_tokens("Hello world this is a test") > 0

    def test_estimate_cost_zero_for_mock_model(self):
        p = MockProvider()
        assert p.estimate_cost(500, 500, "mock-gpt") == 0.0

    async def test_generate_alias_works(self):
        p = MockProvider()
        req = make_request()
        resp = await p.generate(req)
        assert resp is not None

    async def test_generate_stream_alias_works(self):
        p = MockProvider()
        req = make_request(stream=True)
        chunks = [c async for c in p.generate_stream(req)]
        assert len(chunks) > 0


# ══════════════════════════════════════════════════════════════
# 4. OpenAI Provider (Offline — No SDK Key)
# ══════════════════════════════════════════════════════════════

class TestOpenAIProvider:

    async def test_health_check_returns_false_without_key(self):
        with patch("app.ai.providers.openai_provider.settings") as mock_settings:
            mock_settings.OPENAI_API_KEY = None
            p = OpenAIProvider()
            assert await p.health_check() is False

    async def test_generate_falls_back_to_mock_without_key(self):
        with patch("app.ai.providers.openai_provider.settings") as mock_settings:
            mock_settings.OPENAI_API_KEY = None
            mock_settings.REQUEST_TIMEOUT = 60
            p = OpenAIProvider()
            req = make_request(model="gpt-4o")
            resp = await p.generate(req)
            assert resp.content
            assert resp.total_tokens > 0

    async def test_get_provider_info_not_initialized_without_key(self):
        with patch("app.ai.providers.openai_provider.settings") as mock_settings:
            mock_settings.OPENAI_API_KEY = None
            p = OpenAIProvider()
            info = await p.get_provider_info()
            assert info.initialized is False

    def test_count_tokens_estimation(self):
        p = OpenAIProvider()
        count = p.count_tokens("The quick brown fox jumps over the lazy dog")
        assert count > 5

    def test_estimate_cost_uses_registry(self):
        p = OpenAIProvider()
        cost = p.estimate_cost(1000, 500, "gpt-4o")
        assert cost > 0.0

    async def test_stream_falls_back_to_mock_without_key(self):
        with patch("app.ai.providers.openai_provider.settings") as mock_settings:
            mock_settings.OPENAI_API_KEY = None
            mock_settings.REQUEST_TIMEOUT = 60
            p = OpenAIProvider()
            req = make_request(model="gpt-4o", stream=True)
            chunks = [c async for c in p.stream_response(req)]
            assert len(chunks) > 0

    async def test_cancellation_reraises(self):
        """Ensure CancelledError propagates from generate_response."""
        p = OpenAIProvider()
        req = make_request(model="gpt-4o")

        with patch("app.ai.providers.openai_provider._get_openai_client") as mock_client_fn:
            mock_client = MagicMock()
            mock_completions = MagicMock()
            mock_completions.create = AsyncMock(side_effect=asyncio.CancelledError())
            mock_client.chat = MagicMock()
            mock_client.chat.completions = mock_completions
            mock_client_fn.return_value = mock_client

            with patch("app.ai.providers.openai_provider.settings") as mock_settings:
                mock_settings.OPENAI_API_KEY = "fake-key"
                mock_settings.REQUEST_TIMEOUT = 60

                with pytest.raises(asyncio.CancelledError):
                    await p.generate_response(req)


# ══════════════════════════════════════════════════════════════
# 5. Anthropic Provider (Offline — No SDK Key)
# ══════════════════════════════════════════════════════════════

class TestAnthropicProvider:

    async def test_health_check_returns_false_without_key(self):
        with patch("app.ai.providers.claude_provider.settings") as mock_settings:
            mock_settings.ANTHROPIC_API_KEY = None
            p = AnthropicClaudeProvider()
            assert await p.health_check() is False

    async def test_generate_falls_back_to_mock_without_key(self):
        with patch("app.ai.providers.claude_provider.settings") as mock_settings:
            mock_settings.ANTHROPIC_API_KEY = None
            mock_settings.REQUEST_TIMEOUT = 60
            p = AnthropicClaudeProvider()
            req = make_request(model="claude-3-5-sonnet")
            resp = await p.generate(req)
            assert resp.content
            assert resp.total_tokens > 0

    async def test_get_provider_info_structure(self):
        with patch("app.ai.providers.claude_provider.settings") as mock_settings:
            mock_settings.ANTHROPIC_API_KEY = None
            p = AnthropicClaudeProvider()
            info = await p.get_provider_info()
            assert info.provider_name == "Anthropic"
            assert "claude-3-5-sonnet" in info.supported_models

    def test_estimate_cost_for_claude_haiku(self):
        p = AnthropicClaudeProvider()
        cost = p.estimate_cost(1000, 500, "claude-3-haiku")
        assert cost > 0.0

    async def test_stream_falls_back_to_mock_without_key(self):
        with patch("app.ai.providers.claude_provider.settings") as mock_settings:
            mock_settings.ANTHROPIC_API_KEY = None
            mock_settings.REQUEST_TIMEOUT = 60
            p = AnthropicClaudeProvider()
            req = make_request(model="claude-3-5-sonnet", stream=True)
            chunks = [c async for c in p.stream_response(req)]
            assert len(chunks) > 0

    async def test_health_check_does_not_accept_400(self):
        """Health check must only return True on real success, not HTTP 400/404."""
        with patch("app.ai.providers.claude_provider.settings") as mock_settings:
            mock_settings.ANTHROPIC_API_KEY = "fake-key"
            mock_settings.REQUEST_TIMEOUT = 60
        with patch("app.ai.providers.claude_provider._get_anthropic_client") as mock_fn:
            mock_client = MagicMock()
            mock_client.messages = MagicMock()
            # Simulate API error (which means unhealthy)
            mock_client.messages.create = AsyncMock(side_effect=Exception("bad_request"))
            mock_fn.return_value = mock_client

            p = AnthropicClaudeProvider()
            # Should return False on exception, not True
            with patch("app.ai.providers.claude_provider.settings") as s:
                s.ANTHROPIC_API_KEY = "fake-key"
                result = await p.health_check()
            assert result is False


# ══════════════════════════════════════════════════════════════
# 6. Gemini Provider (Offline — No SDK Key)
# ══════════════════════════════════════════════════════════════

class TestGeminiProvider:

    async def test_health_check_returns_false_without_key(self):
        with patch("app.ai.providers.gemini_provider.settings") as mock_settings:
            mock_settings.GEMINI_API_KEY = None
            p = GeminiProvider()
            assert await p.health_check() is False

    async def test_generate_falls_back_to_mock_without_key(self):
        with patch("app.ai.providers.gemini_provider.settings") as mock_settings:
            mock_settings.GEMINI_API_KEY = None
            p = GeminiProvider()
            req = make_request(model="gemini-1.5-flash")
            resp = await p.generate(req)
            assert resp.content
            assert resp.total_tokens > 0

    async def test_get_provider_info_structure(self):
        with patch("app.ai.providers.gemini_provider.settings") as mock_settings:
            mock_settings.GEMINI_API_KEY = None
            p = GeminiProvider()
            info = await p.get_provider_info()
            assert info.provider_name == "Gemini"
            assert "gemini-1.5-pro" in info.supported_models

    def test_estimate_cost_for_gemini_flash(self):
        p = GeminiProvider()
        cost = p.estimate_cost(1000, 500, "gemini-1.5-flash")
        assert cost > 0.0

    async def test_stream_falls_back_to_mock_without_key(self):
        with patch("app.ai.providers.gemini_provider.settings") as mock_settings:
            mock_settings.GEMINI_API_KEY = None
            p = GeminiProvider()
            req = make_request(model="gemini-1.5-flash", stream=True)
            chunks = [c async for c in p.stream_response(req)]
            assert len(chunks) > 0


# ══════════════════════════════════════════════════════════════
# 7. Conversation Manager (TTL, Eviction, Cleanup)
# ══════════════════════════════════════════════════════════════

class TestConversationManager:

    async def test_create_new_session(self):
        mgr = ConversationManager()
        session = await mgr.get_or_create_session(system_prompt="You are JARVIS.")
        assert session.session_id is not None
        assert len(session.messages) == 1  # system prompt

    async def test_get_existing_session(self):
        mgr = ConversationManager()
        s1 = await mgr.get_or_create_session(session_id="test-123")
        s2 = await mgr.get_or_create_session(session_id="test-123")
        assert s1 is s2

    async def test_add_messages(self):
        mgr = ConversationManager()
        session = await mgr.get_or_create_session(session_id="msg-test")
        session.add_user_message("What is the capital of France?")
        session.add_assistant_message("Paris.")
        assert len(session.messages) == 2

    async def test_clear_session(self):
        mgr = ConversationManager()
        await mgr.get_or_create_session(session_id="to-clear")
        result = await mgr.clear_session("to-clear")
        assert result is True
        assert "to-clear" not in mgr.sessions

    def test_session_is_expired(self):
        session = ConversationSession()
        session._last_accessed = time.time() - 7200  # 2 hours ago
        assert session.is_expired(ttl_seconds=3600) is True

    def test_session_is_not_expired(self):
        session = ConversationSession()
        session._last_accessed = time.time() - 60  # 1 minute ago
        assert session.is_expired(ttl_seconds=3600) is False

    def test_touch_resets_expiry(self):
        session = ConversationSession()
        session._last_accessed = time.time() - 7200
        session.touch()
        assert session.is_expired(ttl_seconds=3600) is False

    async def test_evict_expired_sessions(self):
        mgr = ConversationManager()
        s1 = await mgr.get_or_create_session(session_id="old-session")
        s1._last_accessed = time.time() - 7200  # expired

        with patch("app.ai.providers.gemini_provider.settings"):
            pass
        with patch("app.config.settings") as mock_settings:
            mock_settings.SESSION_TTL_SECONDS = 3600
            evicted = await mgr._evict_expired_sessions()
        assert evicted >= 1
        assert "old-session" not in mgr.sessions

    async def test_max_sessions_eviction(self):
        """When exceeding MAX_CONCURRENT_SESSIONS, oldest session is evicted."""
        mgr = ConversationManager()
        with patch("app.ai.conversation.settings") as mock_settings:
            mock_settings.MAX_CONCURRENT_SESSIONS = 3
            mock_settings.SESSION_TTL_SECONDS = 3600
            for i in range(4):
                await asyncio.sleep(0.01)  # ensure distinct timestamps
                await mgr.get_or_create_session(session_id=f"session-{i}")
        assert len(mgr.sessions) <= 3

    def test_token_estimation(self):
        session = ConversationSession(system_prompt="You are JARVIS AI.")
        session.add_user_message("Explain quantum computing in detail." * 50)
        assert session.estimate_total_tokens() > 0

    def test_context_window_truncation_preserves_system(self):
        session = ConversationSession(system_prompt="You are JARVIS.")
        for i in range(50):
            session.add_user_message(f"User message number {i} with padding text here.")
            session.add_assistant_message(f"Assistant response number {i} with additional text.")

        truncated = session.truncate_context_window(max_context_tokens=512)
        system_msgs = [m for m in truncated if m.role == MessageRole.SYSTEM]
        assert len(system_msgs) == 1
        assert system_msgs[0].content == "You are JARVIS."

    def test_context_window_no_truncation_within_limit(self):
        session = ConversationSession()
        session.add_user_message("Hi")
        session.add_assistant_message("Hello")
        original_count = len(session.messages)
        truncated = session.truncate_context_window(max_context_tokens=4096)
        assert len(truncated) == original_count

    def test_session_count(self):
        mgr = ConversationManager()
        assert mgr.session_count() == 0

    async def test_cleanup_task_lifecycle(self):
        mgr = ConversationManager()
        mgr.start_cleanup_task()
        assert mgr._cleanup_task is not None
        assert not mgr._cleanup_task.done()
        await mgr.stop_cleanup_task()
        assert mgr._cleanup_task.done()


# ══════════════════════════════════════════════════════════════
# 8. LLM Router Pipeline
# ══════════════════════════════════════════════════════════════

class TestLLMRouter:

    async def test_generate_completion_mock_model(self):
        router = LLMRouter()
        req = make_request(model="mock-gpt")
        resp = await router.generate_completion(req)
        assert resp.content
        assert resp.total_tokens > 0

    async def test_metrics_updated_after_completion(self):
        router = LLMRouter()
        req = make_request(model="mock-gpt")
        await router.generate_completion(req)
        metrics = router.get_metrics()
        assert metrics.total_requests >= 1
        assert metrics.total_tokens > 0

    async def test_extended_metrics_latency_tracked(self):
        router = LLMRouter()
        req = make_request(model="mock-gpt")
        await router.generate_completion(req)
        ext = router.get_extended_metrics()
        assert ext.total_latency_ms > 0

    async def test_streaming_yields_chunks(self):
        router = LLMRouter()
        req = make_request(model="mock-gpt", stream=True)
        chunks = [c async for c in router.generate_stream(req)]
        assert len(chunks) > 0
        assert all(isinstance(c, LLMStreamChunk) for c in chunks)

    def test_list_available_models(self):
        router = LLMRouter()
        models = router.list_available_models()
        assert len(models) > 0
        model_ids = {m.model_id for m in models}
        assert "gpt-4o" in model_ids
        assert "claude-3-5-sonnet" in model_ids
        assert "gemini-1.5-pro" in model_ids

    def test_model_costs_from_pricing_registry(self):
        """Verify MODEL_REGISTRY costs match pricing_registry — no duplication."""
        router = LLMRouter()
        for model_id, info in router.MODEL_REGISTRY.items():
            expected_input, expected_output = pricing_registry.get_rate(model_id)
            assert info.input_cost_per_1k == expected_input, f"Cost mismatch for {model_id}"
            assert info.output_cost_per_1k == expected_output, f"Cost mismatch for {model_id}"

    def test_resolve_provider_by_prefix(self):
        router = LLMRouter()
        assert router._resolve_provider_name("gpt-unknown") == "OpenAI"
        assert router._resolve_provider_name("claude-unknown") == "Anthropic"
        assert router._resolve_provider_name("gemini-unknown") == "Gemini"
        assert router._resolve_provider_name("totally-unknown") == "MockProvider"

    async def test_health_check_all_returns_dict(self):
        router = LLMRouter()
        health = await router.health_check_all()
        assert isinstance(health, dict)
        assert "MockProvider" in health

    async def test_health_cache_populated_after_prewarm(self):
        router = LLMRouter()
        assert len(router._health_cache) == 0
        await router.prewarm_health_cache()
        assert len(router._health_cache) > 0

    async def test_health_cache_ttl_not_requeried(self):
        """Health should not re-query provider if within TTL window."""
        router = LLMRouter()
        router._health_cache["MockProvider"] = True
        router._health_cache_ts["MockProvider"] = time.time()

        call_count = 0
        original = MockProvider.health_check
        async def counted_health_check(self):
            nonlocal call_count
            call_count += 1
            return True

        with patch.object(MockProvider, "health_check", counted_health_check):
            await router._is_provider_healthy("MockProvider")
        assert call_count == 0  # Served from cache

    async def test_fallback_activates_on_primary_failure(self):
        router = LLMRouter()
        req = make_request(model="gpt-4o")

        mock_openai = AsyncMock()
        mock_openai.generate_response = AsyncMock(side_effect=RuntimeError("API down"))

        with patch.object(router, "get_provider_for_model", return_value=mock_openai):
            resp = await router.generate_completion(req)
        assert resp is not None
        assert resp.content

    async def test_cancellation_tracked_in_metrics(self):
        router = LLMRouter()
        req = make_request(model="mock-gpt")

        mock_provider = AsyncMock()
        mock_provider.generate_response = AsyncMock(side_effect=asyncio.CancelledError())

        with patch("app.ai.router.provider_factory") as mock_factory:
            mock_factory.get_provider.return_value = mock_provider
            with pytest.raises(asyncio.CancelledError):
                await router.generate_completion(req)

        assert router.get_extended_metrics().total_cancellations == 1

    async def test_retry_count_tracked(self):
        router = LLMRouter(max_retries=2)
        req = make_request(model="mock-gpt")

        fail_count = 0
        original_generate = MockProvider.generate_response

        async def fail_twice(self, req):
            nonlocal fail_count
            fail_count += 1
            if fail_count <= 1:
                raise RuntimeError("Transient error")
            return await original_generate(self, req)

        with patch.object(MockProvider, "generate_response", fail_twice):
            resp = await router.generate_completion(req)
        assert resp is not None
        assert router.get_extended_metrics().total_retries >= 1

    async def test_concurrent_completions_thread_safe(self):
        router = LLMRouter()
        req = make_request(model="mock-gpt")
        results = await asyncio.gather(*[router.generate_completion(req) for _ in range(10)])
        assert len(results) == 10
        assert router.get_metrics().total_requests == 10

    async def test_streaming_cancellation_tracked(self):
        router = LLMRouter()
        req = make_request(model="mock-gpt", stream=True)

        async def cancelled_stream(req):
            raise asyncio.CancelledError()
            yield  # Make it a generator

        mock_provider = MagicMock()
        mock_provider.stream_response = cancelled_stream

        with patch("app.ai.router.provider_factory") as mock_factory:
            mock_factory.get_provider.return_value = mock_provider
            with pytest.raises(asyncio.CancelledError):
                async for _ in router.generate_stream(req):
                    pass

        assert router.get_extended_metrics().streaming_cancellations == 1
