"""ActionContext class for managing action execution context."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from llm_mas.action_system.core.action_result import ActionResult
    from llm_mas.mas.agent import Agent
    from llm_mas.mas.conversation import Conversation, ConversationManager
    from llm_mas.mas.user import User
    from llm_mas.mcp_client.client import MCPClient


class ActionContext:
    """Context for executing actions in the multi-agent system."""

    def __init__(  # noqa: PLR0913
        self,
        conversation: Conversation,
        last_result: ActionResult,
        mcp_client: MCPClient,
        agent: Agent,
        user: User,
        conversation_manager: ConversationManager,
    ) -> None:
        """Initialize the action context with a conversation and an optional last result."""
        self.conversation = conversation
        self.last_result = last_result
        self.mcp_client = mcp_client
        self.agent = agent
        self.user = user
        self.conversation_manager = conversation_manager

    @classmethod
    def from_action_result(
        cls,
        action_result: ActionResult,
        context: ActionContext,
    ) -> ActionContext:
        """Create a new ActionContext from an ActionResult and an existing context."""
        return cls(
            conversation=context.conversation,
            last_result=action_result,
            mcp_client=context.mcp_client,
            agent=context.agent,
            user=context.user,
            conversation_manager=context.conversation_manager,
        )
