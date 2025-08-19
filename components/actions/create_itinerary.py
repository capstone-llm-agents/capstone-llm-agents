"""An action that creates a day-by-day travel itinerary using an LLM."""

from typing import override

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.model_providers.ollama.call_llm import call_llm


class CreateItinerary(Action):
    """An action that creates a detailed day-by-day itinerary."""

    def __init__(self) -> None:
        """Initialize the CreateItinerary action."""
        super().__init__(description="Generates a day-by-day itinerary based on search results and user preferences.")

    @override
    async def do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action by generating an itinerary with an LLM."""
        chat_history = context.conversation.get_chat_history()
        messages = chat_history.as_dicts()
        last_message = messages[-1] if messages else None

        if not last_message:
            msg = "No chat history available to respond to."
            raise ValueError(msg)

        # The core of this action is feeding the LLM with all relevant information
        # The `last_result` context will contain the output from previous actions
        # like SearchFlights, SearchAccommodations, etc.
        relevant_data = context.last_result.as_json_pretty()

        # Construct a detailed prompt to guide the LLM's output
        prompt_with_instructions = f"""
        You are a senior travel planner specialised in creating day by day itineraries.
        Based on the following user request and all provided travel data, create a comprehensive day-by-day travel itinerary.
        Structure the itinerary clearly, with a title for each day and a list of activities.
        Include details like suggested times, brief descriptions, and any relevant travel info (e.g., "Take a train").
        Make it sound engaging and helpful.

        User Request: {last_message['content']}

        Relevant Travel Data:
        {relevant_data}
        """

        try:
            response = await call_llm(prompt_with_instructions)
            res = ActionResult()
            res.set_param("itinerary", response)
            return res
        except Exception as e:
            msg = f"An error occurred while calling the LLM to create the itinerary: {e}"
            raise ValueError(msg)