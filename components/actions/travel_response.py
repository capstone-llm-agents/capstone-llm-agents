"""The agent responds to a simple prompt using an LLM."""

import logging
from typing import override

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.model_providers.api import ModelsAPI
from llm_mas.utils.config.models_config import ModelType


class TravelResponse(Action):
    """The action that generates a simple response using an LLM."""

    def __init__(self) -> None:
        """Initialize the SimpleResponse action."""
        super().__init__(
            description="Responds to simple requests that can be answered with a simple response.",
        )

    @override
    async def do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action by generating a response from an LLM."""
        chat_history = context.conversation.get_chat_history()

        messages = chat_history.as_dicts()

        last_message = messages[-1] if messages else None

        if not last_message:
            msg = "No chat history available to respond to."
            raise ValueError(msg)

        if not context.last_result.is_empty():
            # override content
            last_message["content"] = f"""

            You are an expert travel agent. Your task is to provide a detailed and helpful response to the user's request.
            
            Please consider the following context:
            {context.last_result.as_json_pretty()}
            
            Based on the provided user request and context, please generate a detailed response that addresses the user's needs and provides relevant information.
            
            user_request:
            {last_message["content"]}
            """

        # TODO: Move to a different logger  # noqa: TD003
        logging.getLogger("textual_app").info("Calling LLM with message: %s", last_message)
        logging.getLogger("textual_app").info("Context: %s", context.last_result.as_json_pretty())

        response = await ModelsAPI.call_llm_with_chat_history(messages, ModelType.DEFAULT)

        res = ActionResult()
        res.set_param("response", response)

        return res
