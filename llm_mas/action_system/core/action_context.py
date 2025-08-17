"""ActionContext class for managing action execution context."""

from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.mas.conversation import Conversation
from llm_mas.mcp_client.client import MCPClient


class ActionContext:
    """Context for executing actions in the multi-agent system."""

    def __init__(self, conversation: Conversation, last_result: ActionResult, mcp_client: MCPClient) -> None:
        """Initialize the action context with a conversation and an optional last result."""
        self.conversation = conversation
        self.last_result = last_result
        self.mcp_client = mcp_client
