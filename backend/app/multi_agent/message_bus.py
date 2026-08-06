"""
Inter-Agent Messaging Bus Engine.
Provides asynchronous message passing between specialized agents.
"""

from typing import Dict, List, Optional
from app.multi_agent.schemas import AgentMessage, AgentRole


class InterAgentMessageBus:
    """Async event bus for inter-agent communication."""

    def __init__(self) -> None:
        self._messages: List[AgentMessage] = []

    def send_message(
        self,
        sender_role: AgentRole,
        recipient_role: AgentRole,
        content: str,
        payload: Optional[Dict] = None,
        task_id: Optional[str] = None
    ) -> AgentMessage:
        """Publishes message to the inter-agent bus."""
        msg = AgentMessage(
            sender_role=sender_role,
            recipient_role=recipient_role,
            content=content,
            payload=payload or {},
            task_id=task_id
        )
        self._messages.append(msg)
        return msg

    def get_messages_for_agent(self, agent_role: AgentRole) -> List[AgentMessage]:
        """Retrieves all messages sent to a specific agent role."""
        return [m for m in self._messages if m.recipient_role == agent_role or m.recipient_role == AgentRole.COORDINATOR]

    def list_all_messages(self) -> List[AgentMessage]:
        """Returns complete inter-agent message audit log."""
        return list(self._messages)


message_bus = InterAgentMessageBus()
