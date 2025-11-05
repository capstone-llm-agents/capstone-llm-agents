"""A simple action that assesses a user input."""

import json
from typing import override

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.model_providers.api import ModelsAPI
from llm_mas.utils.config.models_config import ModelType
from llm_mas.utils.json_parser import extract_json_from_response


class AssessInput(Action):
    """A simple action that assesses a user input."""

    def __init__(self) -> None:
        """Initialize the AssessInput action."""
        super().__init__(description="Assess the quality of the last user input.")

    @override
    async def _do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action by assessing the quality of the user input."""
        last_user_message = context.conversation.get_chat_history().get_last_user_message()
        if not last_user_message:
            msg = "No user message found in chat history."
            raise ValueError(msg)

        prompt = f"""
        You are an expert assistant that reviews user inputs to determine if they are clear, specific, and actionable.
        The goal is to ensure that the user input can be effectively addressed by an AI assistant.
        You are to determine if the user input is a clear task that can be acted upon.
        A clear task is one that is specific, unambiguous, and provides enough detail for an AI to respond effectively.

        Here is the user input:
        {last_user_message.content}

        Please provide a JSON object with the following field:
        - is_task: A boolean indicating whether the user input is a clear task that can be acted upon.

        Respond only with the JSON object.
        """

        response = await ModelsAPI.call_llm(prompt, model=ModelType.DEFAULT)
        content = extract_json_from_response(response)
        try:
            params_dict = json.loads(content)
        except json.JSONDecodeError as e:
            msg = f"Failed to parse JSON from LLM response: {content}"
            raise ValueError(msg) from e
        is_task = params_dict.get("is_task")
        if is_task is None:
            msg = "The 'is_task' field is missing from the LLM response."
            raise ValueError(msg)
        res = ActionResult()
        res.set_param("is_task", is_task)
        return res
