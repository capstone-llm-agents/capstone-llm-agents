"""ActionContext class for managing action execution context."""

from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.mas.conversation import Conversation


class ActionContext:
    """Context for executing actions in the multi-agent system."""

    def __init__(self, conversation: Conversation, last_result: ActionResult) -> None:
        """Initialize the action context with a conversation and an optional last result."""
        self.conversation = conversation
        self.last_result = last_result
