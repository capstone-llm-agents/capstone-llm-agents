"""The actions needed to provide the agent with a chat history."""

from typing import override

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.model_providers.api import ModelsAPI
from llm_mas.utils.config.models_config import ModelType


class RespondWithChatHistory(Action):
    """An action that let's the agent respond with consideration of the chat history."""

    def __init__(self) -> None:
        """Initialize the RespondWithChatHistory action."""
        super().__init__(description="Retrieves the chat history")

    @override
    async def do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action by retrieving the chat history."""
        chat_history = context.conversation.get_chat_history()

        messages = chat_history.as_dicts()

        last_message = messages[-1] if messages else None

        if not last_message:
            msg = "No chat history available to respond to."
            raise ValueError(msg)

        if not context.last_result.is_empty():
            # override content
            last_message["content"] = f"""
            Context:
            {context.last_result.as_json_pretty()}

            Prompt:
            {last_message["content"]}
            """

        # cap it to last 10 messages
        messages = messages[-10:]

        response = await ModelsAPI.call_llm_with_chat_history(messages, model=ModelType.DEFAULT)

        res = ActionResult()
        res.set_param("response", response)
        return res
