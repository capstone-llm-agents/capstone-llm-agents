"""An action that books a flight."""

import random
import string
from typing import override

from components.actions.travel_context import TRAVEL_CONTEXT, FlightBookingDetails
from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult


class BookFlight(Action):
    """An action that books a flight and generates a confirmation."""

    def __init__(self) -> None:
        """Initialize the BookFlight action."""
        super().__init__(description="Books a flight based on the selected flight number.")

    @override
    async def do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action by booking the flight."""
        chat_history = context.conversation.get_chat_history()

        messages = chat_history.as_dicts()

        last_message = messages[-1] if messages else None

        if not last_message:
            msg = "No chat history available to respond to."
            raise ValueError(msg)

        # Expect the flight number to be passed as a parameter
        flight_number = TRAVEL_CONTEXT.flight_number

        if not flight_number:
            msg = "Flight number is required to book a flight."
            raise ValueError(msg)

        # Spoofing the booking process
        confirmation_code = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))  # noqa: S311

        # In a real application, you would log this to a database or a file
        TRAVEL_CONTEXT.flight_details = FlightBookingDetails(
            flight_number=flight_number,
            confirmation_code=confirmation_code,
            status="confirmed",
        )

        res = ActionResult()
        res.set_param("response", str(TRAVEL_CONTEXT.flight_details))
        res.set_param("travel_context", str(TRAVEL_CONTEXT))

        return res
