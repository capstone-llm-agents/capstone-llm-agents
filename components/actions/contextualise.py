"""The actions that contextualise a message based on chat history."""

from typing import override

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.communication.task.agent_task import Task
from llm_mas.model_providers.api import ModelsAPI
from llm_mas.utils.config.models_config import ModelType


class Contextualise(Action):
    """An action that lets the agent contextualise a message based on chat history."""

    def __init__(self) -> None:
        """Initialize the Contextualise action."""
        super().__init__(description="Contextualises a message based on chat history")

    @override
    async def _do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action by retrieving the chat history."""
        chat_history = context.conversation.get_chat_history()

        messages = chat_history.as_dicts()

        last_message = messages[-1] if messages else None

        if not last_message:
            msg = "No chat history available to respond to."
            raise ValueError(msg)

        prompt = f"""
        You are an AI assistant specialising in summarising and contextualising user messages based on prior conversation history into a concise and relevant format.
        The goal is to help the agent understand the user's current needs by providing context from previous interactions.
        For a given prompt you should provide a concise summary that captures the essence of the user's request, incorporating relevant details from the chat history.
        Do not use weird phrases like 'Based on our previous conversation' or 'As we discussed earlier'. Instead, focus on delivering a clear and direct summary that the agent can use to respond effectively.
        Make sure the summary is relevant to the user's current needs and avoids unnecessary repetition of information already present in the prompt.
        Respond only with the contextualised summary without any additional commentary.
        Do not use emojis, special characters, only plain text and punctuation.

        Here is the message to contextualise:
        {last_message["content"]}
        """

        last_message["content"] = prompt

        # cap it to last 10 messages
        messages = messages[-10:]

        response = await ModelsAPI.call_llm_with_chat_history(messages, model=ModelType.DEFAULT)

        res = ActionResult()
        res.set_param("contextualised_message", response)
        return res
