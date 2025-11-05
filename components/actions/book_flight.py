"""An action that books a flight."""

import random
import string
from typing import override

from components.actions.travel_context import TRAVEL_CONTEXT, FlightBookingDetails
from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.fragment.fragment import Fragment
from llm_mas.fragment.kinds.base import JSONFragmentKind, TextFragmentKind
from llm_mas.fragment.raws.base import JSONRaw, TextRaw
from llm_mas.fragment.source import FragmentSource


class BookFlight(Action):
    """An action that books a flight and generates a confirmation."""

    def __init__(self) -> None:
        """Initialize the BookFlight action."""
        super().__init__(description="Books a flight based on the selected flight number.")

    @override
    async def _do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action by booking the flight."""
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

        res.add_fragment(
            Fragment(
                name="Flight Booking Confirmation",
                description="Confirmation of the booked flight.",
                source=FragmentSource.AGENT,
                kind=JSONFragmentKind(
                    name="flight_booking_confirmation",
                    description="Details of the booked flight.",
                    raw=JSONRaw(
                        {
                            "flight_number": TRAVEL_CONTEXT.flight_details.flight_number,
                            "confirmation_code": TRAVEL_CONTEXT.flight_details.confirmation_code,
                            "status": TRAVEL_CONTEXT.flight_details.status,
                        },
                    ),
                ),
            ),
        )

        return res
