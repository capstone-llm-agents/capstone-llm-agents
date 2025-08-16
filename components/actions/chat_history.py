"""The actions needed to provide the agent with a chat history."""

from typing import override

from llm_mas.action_system.base.actions.stateful_action import StatefulAction
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.agent.workspace import WorkspaceState
from llm_mas.mas.conversation import ChatHistory, Message


class SaveMessageToChatHistory(StatefulAction):
    """An action that prints a greeting message."""

    def __init__(self, workspace_state: WorkspaceState) -> None:
        """Initialize the SayHello action."""
        super().__init__(description="Prints a greeting message", workspace_state=workspace_state)

    @override
    def do(self, params: ActionParams, context: ActionResult) -> ActionResult:
        """Perform the action by printing a greeting."""
        content = params.get_param("content")
        role = params.get_param("role")

        if not isinstance(content, str) or not isinstance(role, str):
            msg = "Content and role must be strings."
            raise TypeError(msg)

        message = Message(content=content, role=role)

        chat_history: ChatHistory = self.get_state("chat_history") or ChatHistory()

        chat_history.add_message(message)

        self.save_state("chat_history", chat_history)

        return ActionResult()


class GetChatHistory(StatefulAction):
    """An action that retrieves the chat history."""

    def __init__(self, workspace_state: WorkspaceState) -> None:
        """Initialize the GetChatHistory action."""
        super().__init__(description="Retrieves the chat history", workspace_state=workspace_state)

    @override
    def do(self, params: ActionParams, context: ActionResult) -> ActionResult:
        """Perform the action by retrieving the chat history."""
        chat_history = self.get_state("chat_history") or ChatHistory()
        res = ActionResult()
        res.set_param("chat_history", chat_history)
        return res
