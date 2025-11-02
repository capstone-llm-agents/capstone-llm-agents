"""An action that simulates booking an accommodation."""

import random
import string
from typing import override

from components.actions.travel_context import TRAVEL_CONTEXT, AccommodationBookingDetails
from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult


class BookAccommodation(Action):
    """An action that books a hotel and generates a confirmation."""

    def __init__(self) -> None:
        """Initialize the BookAccommodation action."""
        super().__init__(description="Simulates the booking of an accommodation and provides a confirmation code.")

    @override
    async def _do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action by simulating a booking."""
        # Expect the accommodation ID to be passed as a parameter
        accommodation_id = TRAVEL_CONTEXT.accommodation_id

        if not accommodation_id:
            msg = "Accommodation ID is required to book a room."
            raise ValueError(msg)

        # Spoofing the booking process
        confirmation_code = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))  # noqa: S311

        # In a real application, you would log this to a database or a file
        TRAVEL_CONTEXT.accommodation_details = AccommodationBookingDetails(
            accommodation_id=accommodation_id,
            confirmation_code=confirmation_code,
            status="confirmed",
            booked_at="2025-08-20T10:00:00Z",  # Spoofed timestamp
        )

        res = ActionResult()
        res.set_param("response", str(TRAVEL_CONTEXT.accommodation_details))
        res.set_param("travel_context", str(TRAVEL_CONTEXT))
        return res
