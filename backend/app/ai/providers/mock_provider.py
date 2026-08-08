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

    def _generate_smart_mock_content(self, request: LLMRequest) -> str:
        """Generates realistic contextual mock content based on prompt inspection."""
        last_user_msg = request.messages[-1].content if request.messages else ""
        sys_prompt = (request.system_prompt or "").lower()
        msg_lower = last_user_msg.lower()

        if "plan" in sys_prompt or "plan" in msg_lower or "dag" in msg_lower or "decompose" in msg_lower:
            return (
                "1. Analyze target system requirements\n"
                "2. Decompose architecture into parallel subcomponents\n"
                "3. Execute implementation & validation pipeline\n"
                "4. Verify quality criteria and consensus voting"
            )
        elif "code" in sys_prompt or "code" in msg_lower or "python" in msg_lower or "typescript" in msg_lower:
            return (
                "```python\n"
                "# Autonomous Code Synthesis Output\n"
                "def execute_task(task_input: str) -> dict:\n"
                "    \"\"\"Synthesized production logic.\"\"\"\n"
                "    return {'status': 'SUCCESS', 'result': f'Processed {task_input}'}\n"
                "```"
            )
        elif "summarize" in sys_prompt or "research" in msg_lower or "doc" in msg_lower:
            return (
                "• Executive Summary: Autonomous platform operating normally.\n"
                "• Core Subsystems: AI Router, Multi-Agent Swarm, Vector Memory, Tools verified.\n"
                "• Next Steps: Proceeding with target workflow execution."
            )

        return f"JARVIS Kernel processed query: '{last_user_msg[:80]}'. All subsystems operational."

    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        start_time = time.time()
        await asyncio.sleep(0.02)

        content = self._generate_smart_mock_content(request)
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
        full_text = self._generate_smart_mock_content(request)

        words = full_text.split(" ")
        for idx, word in enumerate(words):
            await asyncio.sleep(0.01)
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
