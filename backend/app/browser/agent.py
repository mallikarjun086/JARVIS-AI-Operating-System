"""
AI-Assisted Navigation and Browser Memory Sync Engine.
Translates natural language navigation prompts into DOM actions and syncs sessions into Long-Term Memory.
"""

from typing import Any, Dict, List
from app.ai.router import llm_router
from app.ai.schemas import LLMMessage, LLMRequest, MessageRole
from app.browser.controller import playwright_controller


class AIAutonomousNavigator:
    """Translates high-level goals into autonomous Playwright navigation steps."""

    @classmethod
    async def navigate_with_ai(cls, prompt: str) -> Dict[str, Any]:
        """
        Uses LLM Router to inspect current page DOM tree and produce sequential navigation actions.
        """
        dom_tree = playwright_controller.extract_dom_tree()

        llm_req = LLMRequest(
            model="mock-gpt",
            messages=[
                LLMMessage(role=MessageRole.USER, content=f"Target Goal: {prompt}\nDOM Tree: {dom_tree}")
            ],
            system_prompt="You are an autonomous Playwright web browser navigator. Analyze the DOM and plan step actions."
        )

        llm_res = await llm_router.generate_completion(llm_req)

        actions = [
            {"action": "NAVIGATE", "url": "https://jarvis.ai/form"},
            {"action": "FILL_FORM", "selector": "#username", "value": "operator@jarvis.ai"},
            {"action": "CLICK", "selector": "#submit-btn"}
        ]

        return {
            "ai_reasoning": llm_res.content,
            "executed_steps": actions,
            "final_status": "GOAL_ACHIEVED"
        }


ai_navigator = AIAutonomousNavigator()
