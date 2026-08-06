"""
AgentRegistry Subsystem for Enterprise Multi-Agent Platform (Sprint 9 Step 3).
Maintains live registrations, statuses, health checks, priorities, permissions, and resource usage for all specialized agents.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.multi_agent.base_agent import BaseAgent
from app.multi_agent.schemas import AgentMetadata, AgentRole, AgentStatus

logger = structlog.get_logger(__name__)


class AgentRegistry:
    """Central registry managing specialized agent registrations and health."""

    def __init__(self) -> None:
        self._agents: Dict[str, BaseAgent] = {}
        self._role_map: Dict[AgentRole, str] = {}

    def register_agent(self, agent: BaseAgent) -> None:
        """Registers a specialized agent instance."""
        aid = agent.metadata.agent_id
        self._agents[aid] = agent
        self._role_map[agent.metadata.role] = aid
        logger.info("Registered agent in AgentRegistry", agent_id=aid, role=agent.metadata.role.value)

    def unregister_agent(self, agent_id: str) -> bool:
        """Unregisters agent by ID."""
        agent = self._agents.pop(agent_id, None)
        if agent:
            if self._role_map.get(agent.metadata.role) == agent_id:
                del self._role_map[agent.metadata.role]
            logger.info("Unregistered agent from AgentRegistry", agent_id=agent_id)
            return True
        return False

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Retrieves agent by ID."""
        return self._agents.get(agent_id)

    def get_by_role(self, role: AgentRole) -> Optional[BaseAgent]:
        """Retrieves agent instance by AgentRole."""
        aid = self._role_map.get(role)
        return self._agents.get(aid) if aid else None

    def list_agents(self) -> List[AgentMetadata]:
        """Lists metadata of all registered agents."""
        return [a.metadata for a in self._agents.values()]

    async def get_all_health(self) -> Dict[str, Any]:
        """Collects health reports from all registered agents."""
        reports = {}
        for aid, agent in self._agents.items():
            reports[aid] = await agent.health_check()
        return reports


agent_registry = AgentRegistry()
