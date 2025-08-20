"""Hack to make sure that the travel planner has relative info always."""

from llm_mas.action_system.core.action_context import ActionContext


class AccommodationBookingDetails:
    """Class to hold booking details."""

    def __init__(self, accommodation_id: str, confirmation_code: str, status: str, booked_at: str) -> None:
        """Initialize booking details."""
        self.accommodation_id = accommodation_id
        self.confirmation_code = confirmation_code
        self.status = status
        self.booked_at = booked_at

    def __str__(self) -> str:
        """Return a string representation of the booking details."""
        return (
            f"Accommodation ID: {self.accommodation_id}, "
            f"Confirmation Code: {self.confirmation_code}, "
            f"Status: {self.status}, "
            f"Booked At: {self.booked_at}"
        )


class Accommodation:
    """Class to hold accommodation details."""

    def __init__(self, name: str, hotel_id: str, address: str) -> None:
        """Initialize accommodation details."""
        self.name = name
        self.hotel_id = hotel_id
        self.address = address

    def __str__(self) -> str:
        """Return a string representation of the accommodation."""
        return f"Name: {self.name}, Hotel ID: {self.hotel_id}, Address: {self.address}"


class FlightBookingDetails:
    """Class to hold flight booking details."""

    def __init__(self, flight_number: str, confirmation_code: str, status: str) -> None:
        """Initialize flight booking details."""
        self.flight_number = flight_number
        self.confirmation_code = confirmation_code
        self.status = status

    def __str__(self) -> str:
        """Return a string representation of the flight booking details."""
        return (
            f"Flight Number: {self.flight_number}, Confirmation Code: {self.confirmation_code}, Status: {self.status}"
        )


class BudgetDetails:
    """Class to hold budget details."""

    def __init__(
        self,
        daily_cost: float,
        total_estimate_without_buffer: float,
        final_estimate: float,
        currency: str,
        details: str,
    ) -> None:
        """Initialize budget details."""
        self.daily_cost = daily_cost
        self.total_estimate_without_buffer = total_estimate_without_buffer
        self.final_estimate = final_estimate
        self.currency = currency
        self.details = details

    def __str__(self) -> str:
        """Return a string representation of the budget details."""
        return (
            f"Daily Cost: {self.daily_cost}, "
            f"Total Estimate (without buffer): {self.total_estimate_without_buffer}, "
            f"Final Estimate: {self.final_estimate}, "
            f"Currency: {self.currency}, "
            f"Details: {self.details}"
        )


class TravelContext:
    """Context for travel-related actions."""

    def __init__(self) -> None:
        """Initialize the travel context."""
        # Base daily costs for a 'mid-range' trip. These will be adjusted by the heuristic.
        self.base_daily_costs = {
            "low": 100,
            "mid": 180,
            "high": 350,
        }
        self.city: str | None = None
        self.duration_days: int | None = None
        self.travel_style: str | None = None
        self.flight_number: str | None = None
        self.itinerary: str | None = None
        self.accommodation_id: str | None = None
        self.accommodation_details: AccommodationBookingDetails | None = None
        self.flight_details: FlightBookingDetails | None = None
        self.budget_details: BudgetDetails | None = None
        self.accommodations: list[Accommodation] = []
        self.origin: str | None = None

    def __str__(self) -> str:
        """Return a string representation of the travel context."""
        return (
            f"City: {self.city}, Duration Days: {self.duration_days}, "
            f"Travel Style: {self.travel_style}, Flight Number: {self.flight_number}, "
            f"Itinerary: {self.itinerary}, Accommodation ID: {self.accommodation_id}, "
            f"Accommodation Details: {self.accommodation_details}, "
            f"Flight Details: {self.flight_details}, Budget Details: {self.budget_details}"
        )


TRAVEL_CONTEXT = TravelContext()
