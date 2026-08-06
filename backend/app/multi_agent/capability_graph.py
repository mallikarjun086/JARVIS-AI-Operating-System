"""
CapabilityGraph Engine for Dynamic Agent Selection (Sprint 9 Step 4).
Maps required capabilities to candidate agents with dynamic ranking, versioning, and fallbacks.
The Planner never selects agents directly; it queries CapabilityGraph: 'What capability is required?'
"""

from typing import Dict, List, Optional
import structlog

from app.multi_agent.base_agent import BaseAgent
from app.multi_agent.registry import agent_registry
from app.multi_agent.schemas import AgentRole, CapabilityQuery

logger = structlog.get_logger(__name__)


class CapabilityGraph:
    """Dynamic Capability Graph for agent capability routing and ranking."""

    @classmethod
    def select_agent_for_capability(
        cls,
        capability: str,
        query: Optional[CapabilityQuery] = None
    ) -> Optional[BaseAgent]:
        """Selects the highest ranked available agent exposing the required capability."""
        candidates = cls.find_candidates_for_capability(capability)
        if not candidates:
            logger.warning("No candidate agent found for capability", capability=capability)
            # Fallback to Coordinator or Coding Agent if available
            return agent_registry.get_by_role(AgentRole.COORDINATOR) or agent_registry.get_by_role(AgentRole.CODING)

        # Rank candidates by priority and availability
        candidates.sort(key=lambda a: (a.metadata.priority, a.metadata.estimated_latency_ms), reverse=True)
        selected = candidates[0]
        logger.info("CapabilityGraph selected agent", capability=capability, selected_agent=selected.metadata.agent_id)
        return selected

    @classmethod
    def find_candidates_for_capability(cls, capability: str) -> List[BaseAgent]:
        """Lists all registered agents supporting target capability."""
        all_agents = [agent_registry.get_agent(meta.agent_id) for meta in agent_registry.list_agents()]
        exact_candidates = []
        fallback_candidates = []

        for agent in all_agents:
            if not agent or not agent.metadata.availability:
                continue
            caps = [c.lower() for c in agent.get_capabilities()]
            if capability.lower() in caps:
                exact_candidates.append(agent)
            elif "general_processing" in caps or capability == "*":
                fallback_candidates.append(agent)

        return exact_candidates or fallback_candidates


    @classmethod
    def get_capability_mapping(cls) -> Dict[str, List[str]]:
        """Returns dictionary mapping capabilities to supporting agent IDs."""
        mapping: Dict[str, List[str]] = {}
        for meta in agent_registry.list_agents():
            for cap in meta.capabilities:
                if cap not in mapping:
                    mapping[cap] = []
                mapping[cap].append(meta.agent_id)
        return mapping


capability_graph = CapabilityGraph()
