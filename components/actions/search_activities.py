"""An action that searches for local activities using an LLM call."""

from typing import override

from components.actions.travel_context import TRAVEL_CONTEXT
from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.model_providers.ollama.call_llm import call_llm


class SearchActivities(Action):
    """An action that finds activities based on a user's request and context."""

    def __init__(self) -> None:
        """Initialize the SearchActivities action."""
        super().__init__(description="Searches for and recommends activities for a given location and user interests.")

    @override
    async def do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action by generating a response from an LLM."""
        chat_history = context.conversation.get_chat_history()
        messages = chat_history.as_dicts()
        last_message = messages[-1] if messages else None

        if not last_message:
            msg = "No chat history available to respond to."
            raise ValueError(msg)

        # Contextualize the prompt with any previous search results
        if not context.last_result.is_empty():
            last_message["content"] = f"""
            Context:
            {context.last_result.as_json_pretty()}

            Prompt:
            {last_message["content"]}
            """

        # We need a clear, direct instruction for the LLM
        prompt_with_instructions = f"""
        You are a senior travel planner specialising in searching for fun and interesting activities.
        Based on the following user request and any provided context, act as a travel planner.
        Generate a list of recommended activities, tours, or points of interest.
        The output should be a structured, easy-to-read list with a brief description for each item.
        User Request: {last_message["content"]}
        """

        # Call the local LLM
        response = await call_llm(prompt_with_instructions)
        res = ActionResult()
        res.set_param("response", response)
        res.set_param("travel_context", str(TRAVEL_CONTEXT))
        return res
