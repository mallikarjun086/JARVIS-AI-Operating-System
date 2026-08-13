"""
10 Specialized Executable Agents Package for JARVIS AI OS Multi-Agent Swarm.
"""

from app.multi_agent.agent_pool import (
    planner_agent,
    research_agent,
    browser_agent,
    desktop_agent,
    coding_agent,
    memory_agent,
    vision_agent,
    voice_agent,
    coordinator_agent,
    verifier_agent,
    agent_pool
)

__all__ = [
    "planner_agent",
    "research_agent",
    "browser_agent",
    "desktop_agent",
    "coding_agent",
    "memory_agent",
    "vision_agent",
    "voice_agent",
    "coordinator_agent",
    "verifier_agent",
    "agent_pool"
]
