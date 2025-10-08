"""Message router for directing network messages to agents.

This module bridges the gap between the network layer (NetworkMessage/NetworkFragment)
and the agent communication layer (AssistantMessage/CommunicationInterface).
"""

import logging
from typing import TYPE_CHECKING, Any

from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.communication.comm_extras import Reason
from llm_mas.communication.interface import CommunicationState
from llm_mas.communication.message_types import MessageType
from llm_mas.communication.messages import (
    AcceptanceMessage,
    InformationMessage,
    ProposalMessage,
    QueryMessage,
    RejectionMessage,
    TaskMessage,
    ThanksMessage,
)
from llm_mas.communication.task.agent_task import Task
from llm_mas.mas.conversation import AssistantMessage
from llm_mas.utils.random_id import generate_random_id
from network_server.message import NetworkMessage
from network_server.network_fragment import FragmentKindSerializable, FragmentSource, NetworkFragment

if TYPE_CHECKING:
    from llm_mas.client.account.client import Client
    from llm_mas.mas.agent import Agent
    from llm_mas.mas.conversation import AssistantMessage

logger = logging.getLogger(__name__)


class MessageRouter:
    """Routes incoming NetworkMessages to the appropriate agent's communication interface."""

    def __init__(self, client: "Client") -> None:
        """Initialize the message router with a client.

        Args:
            client: The client instance containing agents and MAS

        """
        self.client = client

    def _extract_text_from_fragments(self, fragments: list[NetworkFragment]) -> str:
        """Extract text content from NetworkFragment list.

        Args:
            fragments: List of NetworkFragment objects

        Returns:
            Combined text content from all fragments

        """
        text_parts = []
        for fragment in fragments:
            if fragment.kind.name == "text" and "text" in fragment.kind.content:
                text_parts.append(fragment.kind.content["text"])
        return " ".join(text_parts)

    def _find_agent_by_name(self, agent_name: str) -> "Agent | None":
        """Find an agent by name in the client's MAS.

        Args:
            agent_name: Name of the agent to find

        Returns:
            Agent instance if found, None otherwise

        """
        # Strip client name prefix if present (e.g., "alice_assistant" -> "assistant")
        if "_" in agent_name:
            agent_name = agent_name.split("_", 1)[1]

        agents = self.client.get_agents()
        for agent in agents:
            if agent.name == agent_name:
                return agent
        return None

    def _convert_network_message_to_assistant_message(
        self,
        network_message: NetworkMessage,
        sender_agent: "Agent",
    ) -> "AssistantMessage | None":
        """Convert a NetworkMessage to an AssistantMessage.

        Args:
            network_message: The NetworkMessage to convert
            sender_agent: The agent who sent the message

        Returns:
            AssistantMessage instance or None if conversion fails

        """
        content = self._extract_text_from_fragments(network_message.fragments)
        message_type = network_message.message_type

        # create new conversation
        conversation = self.client.mas.conversation_manager.start_conversation(
            f"network-conversation-{generate_random_id()}",
        )

        action_context = ActionContext(
            conversation=conversation,
            last_result=ActionResult(),
            mcp_client=self.client.mcp_client,
            agent=sender_agent,
            user=self.client.user,
            conversation_manager=self.client.mas.conversation_manager,
            client=self.client,
        )

        task_description = network_message.context.get("task_description", content)
        task = Task(description=task_description, action_context=action_context)

        # Create the appropriate message type based on MessageType
        if message_type == MessageType.PROPOSAL:
            # Extract task information from context
            return ProposalMessage(content=content, sender=sender_agent, task=task)

        if message_type == MessageType.ACCEPTANCE:
            return AcceptanceMessage(sender=sender_agent, content=content)

        if message_type == MessageType.REJECTION:
            reason_text = network_message.context.get("reason", "Cannot process request")
            reason = Reason(text=reason_text)
            return RejectionMessage(sender=sender_agent, reason=reason, content=content)

        if message_type == MessageType.QUERY:
            # Create minimal action context from network message
            return QueryMessage(content=content, sender=sender_agent, action_context=action_context)

        if message_type == MessageType.TASK:
            return TaskMessage(content=content, sender=sender_agent, task=task)

        if message_type == MessageType.INFORMATION:
            # Create action result from context
            result_data = network_message.context.get("result", content)
            action_result = ActionResult()
            action_result.results = result_data
            return InformationMessage(content=content, sender=sender_agent, action_result=action_result)

        if message_type == MessageType.THANKS:
            return ThanksMessage(sender=sender_agent, content=content)

        # Default: create a generic AssistantMessage
        return AssistantMessage(content=content, sender=sender_agent, message_type=message_type)

    async def handle_incoming_network_message(self, message_data: dict[str, Any]) -> None:
        """Handle an incoming network message and route it to the appropriate agent.

        Args:
            message_data: Dictionary containing the message envelope with:
                - id: message ID
                - from_user_id: sender's user ID
                - timestamp: message timestamp
                - message: serialized NetworkMessage object

        """
        print(f"Client received network message: {message_data}")

        try:
            # Extract the NetworkMessage from the envelope
            network_msg_data = message_data.get("message", {})

            # Reconstruct the NetworkMessage

            fragments = [
                NetworkFragment(
                    name=frag["name"],
                    kind=FragmentKindSerializable(
                        name=frag["kind"]["name"],
                        content=frag["kind"]["content"],
                        description=frag["kind"].get("description"),
                    ),
                    description=frag.get("description"),
                    source=FragmentSource[frag["source"]],
                )
                for frag in network_msg_data.get("fragments", [])
            ]

            network_message = NetworkMessage(
                sender=network_msg_data["sender"],
                sender_client=network_msg_data["sender_client"],
                recipient=network_msg_data["recipient"],
                recipient_client=network_msg_data["recipient_client"],
                fragments=fragments,
                message_type=MessageType[network_msg_data["message_type"]],
                context=network_msg_data.get("context", {}),
            )

            # Find the recipient agent
            recipient_agent = self._find_agent_by_name(network_message.recipient)
            if not recipient_agent:
                logger.warning("Recipient agent not found: %s", network_message.recipient)
                return

            # Find or create a representation of the sender agent
            sender_agent = self._find_agent_by_name(network_message.sender)
            if not sender_agent:
                # Create a proxy agent for the remote sender

                # Use a simple placeholder for remote agents
                sender_agent = self.client.get_assistant_agent()
                if not sender_agent:
                    logger.warning("No assistant agent available to handle message")
                    return

            # Convert NetworkMessage to AssistantMessage
            assistant_message = self._convert_network_message_to_assistant_message(
                network_message,
                sender_agent,
            )

            if not assistant_message:
                logger.warning("Failed to convert network message to assistant message")
                return

            # Create communication state

            comm_state = CommunicationState(agent=recipient_agent, talking_to=sender_agent)

            # Route the message to the agent's communication interface
            response = await recipient_agent.communication_interface.handle_message(
                assistant_message,
                comm_state,
            )

            # TODO: Send response back over the network if needed
            logger.info(
                "Message handled by agent %s, response type: %s",
                recipient_agent.name,
                response.message_type,
            )

        except Exception:
            logger.exception("Error handling incoming network message")
