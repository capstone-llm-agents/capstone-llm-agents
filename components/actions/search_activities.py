"""An action that searches for local activities using an LLM call."""

from typing import override

from components.actions.travel_context import TRAVEL_CONTEXT
from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.model_providers.api import ModelsAPI
from llm_mas.utils.config.models_config import ModelType


class SearchActivities(Action):
    """An action that finds activities based on a user's request and context."""

    def __init__(self) -> None:
        """Initialize the SearchActivities action."""
        super().__init__(description="Searches for and recommends activities for a given location and user interests.")

    @override
    async def do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action by generating a response from an LLM."""
        last_message = self.get_last_message_content(context)

        # Contextualize the prompt with any previous search results
        if not context.last_result.is_empty():
            last_message = f"""
            Context:
            {context.last_result.as_json_pretty()}

            Prompt:
            {last_message}
            """

        # We need a clear, direct instruction for the LLM
        prompt_with_instructions = f"""
        You are a senior travel planner specialising in searching for fun and interesting activities.
        Based on the following user request and any provided context, act as a travel planner.
        Generate a list of recommended activities, tours, or points of interest.
        The output should be a structured, easy-to-read list with a brief description for each item.
        User Request: {last_message}
        """

        # Call the local LLM
        response = await ModelsAPI.call_llm(prompt_with_instructions, model=ModelType.DEFAULT)
        res = ActionResult()
        res.set_param("response", response)
        res.set_param("travel_context", str(TRAVEL_CONTEXT))
        return res
