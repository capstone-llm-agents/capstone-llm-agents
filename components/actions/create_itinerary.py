"""An action that creates a day-by-day travel itinerary using an LLM."""

from typing import override

from components.actions.travel_context import TRAVEL_CONTEXT
from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.model_providers.api import ModelsAPI
from llm_mas.utils.config.models_config import ModelType


class CreateItinerary(Action):
    """An action that creates a detailed day-by-day itinerary."""

    def __init__(self) -> None:
        """Initialize the CreateItinerary action."""
        super().__init__(description="Generates a day-by-day itinerary based on search results and user preferences.")

        self.use_fragments_for_context()

    @override
    async def _do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action by generating an itinerary with an LLM."""
        last_message = self.get_last_message_content(context)

        # The core of this action is feeding the LLM with all relevant information
        # The `last_result` context will contain the output from previous actions
        # like SearchFlights, SearchAccommodations, etc.
        relevant_data = self.get_context_from_last_result(context)

        # Construct a detailed prompt to guide the LLM's output
        prompt_with_instructions = f"""
        You are a senior travel planner specialised in creating day by day itineraries.
        Based on the following user request and all provided travel data, create a comprehensive day-by-day travel itinerary.
        Structure the itinerary clearly, with a title for each day and a list of activities.
        Include details like suggested times, brief descriptions, and any relevant travel info (e.g., "Take a train").
        Make it sound engaging and helpful.

        User Request: {last_message}

        Relevant Travel Data:
        {relevant_data}
        """

        try:
            response = await ModelsAPI.call_llm(prompt_with_instructions, model=ModelType.DEFAULT)
            res = ActionResult()
            res.set_param("response", response)
            res.set_param("travel_context", str(TRAVEL_CONTEXT))
            return res
        except Exception as e:
            msg = f"An error occurred while calling the LLM to create the itinerary: {e}"
            raise ValueError(msg) from e
