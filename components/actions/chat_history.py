"""The actions needed to provide the agent with a chat history."""

from typing import override

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult


class SaveMessageToChatHistory(Action):
    """An action that prints a greeting message."""

    def __init__(self) -> None:
        """Initialize the SayHello action."""
        super().__init__(description="Prints a greeting message")

    @override
    def do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action by printing a greeting."""


class GetChatHistory(Action):
    """An action that retrieves the chat history."""

    def __init__(self) -> None:
        """Initialize the GetChatHistory action."""
        super().__init__(description="Retrieves the chat history")

    @override
    def do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action by retrieving the chat history."""
