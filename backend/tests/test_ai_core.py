"""
Pytest Test Suite for AI Core Components.
"""

from httpx import AsyncClient
import pytest
from app.ai.conversation import ConversationSession, conversation_manager
from app.ai.prompts import prompt_manager
from app.ai.providers.mock_provider import MockProvider
from app.ai.router import llm_router
from app.ai.schemas import LLMMessage, LLMRequest, MessageRole


@pytest.mark.asyncio
async def test_mock_provider_generation():
    """Verifies mock provider non-streaming and streaming generation."""
    provider = MockProvider()
    req = LLMRequest(
        model="mock-gpt",
        messages=[LLMMessage(role=MessageRole.USER, content="Hello Mock Provider")]
    )

    resp = await provider.generate(req)
    assert resp.provider == "MockProvider"
    assert resp.total_tokens > 0
    assert "Mock AI Core Response" in resp.content

    chunks = []
    async for chunk in provider.generate_stream(req):
        chunks.append(chunk.delta_content)
    assert len(chunks) > 0


@pytest.mark.asyncio
async def test_llm_router_model_resolution():
    """Verifies LLM router model mapping and fallback provider resolution."""
    openai_prov = llm_router.get_provider_for_model("gpt-4o")
    assert openai_prov.provider_name == "OpenAI"

    claude_prov = llm_router.get_provider_for_model("claude-3-5-sonnet")
    assert claude_prov.provider_name == "Anthropic"

    gemini_prov = llm_router.get_provider_for_model("gemini-1.5-pro")
    assert gemini_prov.provider_name == "Gemini"

    mock_prov = llm_router.get_provider_for_model("unknown-model")
    assert mock_prov.provider_name == "MockProvider"


@pytest.mark.asyncio
async def test_prompt_manager_rendering():
    """Verifies prompt template variable substitution."""
    user_p, sys_p = prompt_manager.render_prompt("code_generator", language="Python", task="Sort array", context="Fast sorting")
    assert "Language: Python" in user_p
    assert "Task: Sort array" in user_p
    assert "Principal Software Architect" in sys_p


@pytest.mark.asyncio
async def test_conversation_context_truncation():
    """Verifies context window token budget truncation preserves system prompt."""
    session = ConversationSession(system_prompt="System instructions")
    for i in range(20):
        session.add_user_message(f"User long text message turn #{i} with extra words to consume tokens.")
        session.add_assistant_message(f"Assistant response turn #{i} with extra content text.")

    # Truncate context window to small budget
    pruned = session.truncate_context_window(max_context_tokens=100)
    assert len(pruned) < 41
    assert pruned[0].role == MessageRole.SYSTEM
    assert pruned[0].content == "System instructions"


@pytest.mark.asyncio
async def test_ai_api_endpoints(client: AsyncClient):
    """Tests /api/v1/ai/models and /api/v1/ai/chat/completions endpoints."""
    # 1. Register & login test user
    reg_payload = {"email": "aiuser@jarvis.ai", "password": "Password123!", "full_name": "AI User"}
    await client.post("/api/v1/auth/register", json=reg_payload)

    login_resp = await client.post("/api/v1/auth/login", data={"username": "aiuser@jarvis.ai", "password": "Password123!"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get Models
    models_resp = await client.get("/api/v1/ai/models", headers=headers)
    assert models_resp.status_code == 200
    models = models_resp.json()
    assert len(models) >= 4

    # 3. Create Chat Completion
    chat_payload = {
        "model": "mock-gpt",
        "messages": [{"role": "user", "content": "What is clean architecture?"}],
        "temperature": 0.2
    }
    chat_resp = await client.post("/api/v1/ai/chat/completions", json=chat_payload, headers=headers)
    assert chat_resp.status_code == 200
    res_data = chat_resp.json()
    assert "content" in res_data
    assert res_data["provider"] == "MockProvider"

    # 4. Get Cost & Token Metrics
    metrics_resp = await client.get("/api/v1/ai/metrics", headers=headers)
    assert metrics_resp.status_code == 200
    assert metrics_resp.json()["total_requests"] >= 1
