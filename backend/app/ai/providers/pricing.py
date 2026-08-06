"""
Centralized Model Pricing Registry for LLM Cost Estimations.
Defines input and output cost rates per 1,000 tokens for all supported providers and models.
"""

from typing import Dict, Tuple


class PricingRegistry:
    """Centralized Model Token Pricing Registry."""

    # Model ID -> (Input Cost Per 1k Tokens, Output Cost Per 1k Tokens)
    RATES: Dict[str, Tuple[float, float]] = {
        # OpenAI Models
        "gpt-4o": (0.005, 0.015),
        "gpt-4-turbo": (0.01, 0.03),
        "gpt-3.5-turbo": (0.0005, 0.0015),

        # Anthropic Claude Models
        "claude-3-5-sonnet": (0.003, 0.015),
        "claude-3-opus": (0.015, 0.075),
        "claude-3-haiku": (0.00025, 0.00125),

        # Google Gemini Models
        "gemini-1.5-pro": (0.0035, 0.0105),
        "gemini-1.5-flash": (0.00035, 0.00105),

        # Mock / Offline Models
        "mock-gpt": (0.0, 0.0),
        "mock-claude": (0.0, 0.0),
        "mock-gemini": (0.0, 0.0),
    }

    @classmethod
    def get_rate(cls, model_id: str) -> Tuple[float, float]:
        """Returns (input_cost_per_1k, output_cost_per_1k) for a given model ID."""
        return cls.RATES.get(model_id, (0.001, 0.002))

    @classmethod
    def calculate_cost(cls, model_id: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculates total financial USD cost for prompt and completion token usage."""
        input_rate, output_rate = cls.get_rate(model_id)
        cost = (prompt_tokens * input_rate + completion_tokens * output_rate) / 1000.0
        return round(cost, 6)


pricing_registry = PricingRegistry()
