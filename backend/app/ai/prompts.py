"""
Prompt Management Engine and Template System.
"""

import re
from typing import Dict, Optional
from pydantic import BaseModel, Field


class PromptTemplate(BaseModel):
    """Prompt template model."""
    name: str
    description: str
    template: str
    default_system_prompt: Optional[str] = None

    def render(self, **kwargs) -> str:
        """Renders prompt string by substituting {{variable}} placeholders."""
        result = self.template
        for key, val in kwargs.items():
            pattern = r"\{\{\s*" + str(key) + r"\s*\}\}"
            result = re.sub(pattern, str(val), result)
        return result


class PromptManager:
    """Prompt template engine and system persona manager."""

    TEMPLATES: Dict[str, PromptTemplate] = {
        "system_assistant": PromptTemplate(
            name="system_assistant",
            description="General Autonomous AI Assistant Persona",
            template="{{user_input}}",
            default_system_prompt="You are JARVIS, an enterprise-grade autonomous AI assistant. Provide concise, expert, and precise responses."
        ),
        "code_generator": PromptTemplate(
            name="code_generator",
            description="Software Engineering Code Generator",
            template="Language: {{language}}\nTask: {{task}}\nContext: {{context}}",
            default_system_prompt="You are a Principal Software Architect. Write production-grade, clean, fully typed code adhering to SOLID principles."
        ),
        "summarizer": PromptTemplate(
            name="summarizer",
            description="Text Summarization Engine",
            template="Please summarize the following document in {{bullet_points}} bullet points:\n\n{{text}}",
            default_system_prompt="You are an expert technical editor. Summarize key takeaways accurately."
        )
    }

    @classmethod
    def get_template(cls, name: str) -> Optional[PromptTemplate]:
        """Fetches prompt template by name."""
        return cls.TEMPLATES.get(name)

    @classmethod
    def render_prompt(cls, template_name: str, **kwargs) -> tuple[str, str]:
        """Renders user prompt and system prompt for a template name."""
        tpl = cls.get_template(template_name)
        if not tpl:
            return (kwargs.get("user_input", ""), "You are JARVIS AI OS Assistant.")

        user_prompt = tpl.render(**kwargs)
        system_prompt = tpl.default_system_prompt or "You are JARVIS AI OS Assistant."
        return (user_prompt, system_prompt)


prompt_manager = PromptManager()
