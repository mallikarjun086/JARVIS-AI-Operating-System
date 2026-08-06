"""
Integration Tests for Multi-Provider LLM Gateway.
"""

import pytest
from jarvis.infrastructure.llm.llm_gateway import LLMGateway


@pytest.mark.asyncio
async def test_llm_gateway_fallback_generation():
    """Tests offline generation fallback mode."""
    gateway = LLMGateway(fallback_mode=True)

    result = await gateway.generate(
        prompt="Write a file named output.txt",
        system_prompt="You are an autonomous agent."
    )

    assert "content" in result
    assert result["content"] is not None


@pytest.mark.asyncio
async def test_llm_gateway_embedding_generation():
    """Tests generating normalized float vector embedding."""
    gateway = LLMGateway(fallback_mode=True)
    embedding = await gateway.generate_embedding("Test embedding vector string")

    assert isinstance(embedding, list)
    assert len(embedding) == 384
    assert all(isinstance(x, float) for x in embedding)
