"""The agent responds to a simple prompt using an LLM."""

import json
import logging
from typing import override

from components.actions.travel_context import TRAVEL_CONTEXT
from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.model_providers.ollama.call_llm import call_llm, call_llm_with_messages
from llm_mas.utils.json_parser import extract_json_from_response


class GetTripDetails(Action):
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

        if context.last_result.is_empty():
            context.last_result.set_param("travel_context", str(TRAVEL_CONTEXT))

        # override content
        last_message["content"] = f"""
        Context:
        {context.last_result.as_json_pretty()}

        You are an expert travel agent. Your task is to provide a detailed and helpful response to the user's request.
        Please consider the following context:
        {context.last_result.as_json_pretty()}

        User Message:
        {last_message["content"]}

        If the user has provided any trip details, please summarize them in a clear and concise manner.
        Put the trip details in a JSON format like so:
        ```json
        {{
            "origin": "<starting city>",
            "destination": "<destination city>",
            "budget": "<low/mid/high>",
            "duration_days": "<number of days>",
        }}
        ```

        If they don't provide any trip details, ask them kindly to provide the details that are missing.
        """

        # TODO: Move to a different logger  # noqa: TD003
        logging.getLogger("textual_app").info("Calling LLM with message: %s", last_message)
        logging.getLogger("textual_app").info("Context: %s", context.last_result.as_json_pretty())

        messages.pop()
        messages.append(last_message)

        # log messages
        logging.getLogger("textual_app").info("Messages: %s", messages)

        response = await call_llm_with_messages(messages)

        content = extract_json_from_response(response)

        try:
            loaded_json = json.loads(content)

            # lets try to extract trip details
            trip_details = {
                "origin": loaded_json.get("origin", None),
                "destination": loaded_json.get("destination", None),
                "travel_style": loaded_json.get("budget", None),
                "duration_days": loaded_json.get("duration_days", None),
            }

            # update TRAVEL_CONTEXT with trip details
            TRAVEL_CONTEXT.origin = trip_details["origin"]
            TRAVEL_CONTEXT.city = trip_details["destination"]
            TRAVEL_CONTEXT.travel_style = trip_details["travel_style"]
            TRAVEL_CONTEXT.duration_days = trip_details["duration_days"]

        except json.JSONDecodeError as e:
            """This is fine"""

        res = ActionResult()
        res.set_param("response", response)
        res.set_param("travel_context", str(TRAVEL_CONTEXT))

        return res
