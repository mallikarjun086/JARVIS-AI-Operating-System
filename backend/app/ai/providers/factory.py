"""
Provider Factory Pattern Engine.
Manages provider singletons, caching, and lifecycle initialization/shutdown.
"""

from typing import Dict, Optional
from app.ai.providers.base import BaseLLMProvider
from app.ai.providers.claude_provider import AnthropicClaudeProvider
from app.ai.providers.gemini_provider import GeminiProvider
from app.ai.providers.mock_provider import MockProvider
from app.ai.providers.openai_provider import OpenAIProvider
from app.core.logging import logger


class ProviderFactory:
    """Factory responsible for instantiating and caching singleton LLM Providers."""

    def __init__(self) -> None:
        self._instances: Dict[str, BaseLLMProvider] = {}

    def get_provider(self, provider_name: str) -> BaseLLMProvider:
        """Returns cached singleton provider instance or instantiates new provider."""
        name_clean = provider_name.strip()
        if name_clean in self._instances:
            return self._instances[name_clean]

        if name_clean == "OpenAI":
            provider = OpenAIProvider()
        elif name_clean in ("Anthropic", "Claude"):
            provider = AnthropicClaudeProvider()
        elif name_clean == "Gemini":
            provider = GeminiProvider()
        else:
            provider = MockProvider()

        self._instances[name_clean] = provider
        logger.info("Instantiated LLM provider via Factory", provider=name_clean)
        return provider

    async def initialize_all(self) -> Dict[str, bool]:
        """Initializes all registered provider instances."""
        status = {}
        for name in ["OpenAI", "Anthropic", "Gemini", "MockProvider"]:
            p = self.get_provider(name)
            status[name] = await p.initialize()
        return status

    async def shutdown_all(self) -> None:
        """Gracefully shuts down all provider instances."""
        for p in self._instances.values():
            await p.shutdown()
        self._instances.clear()


provider_factory = ProviderFactory()
