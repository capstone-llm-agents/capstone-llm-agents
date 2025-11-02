"""An action that searches for flights using the Aviationstack API."""

import os
import urllib.parse
from typing import override

import aiohttp

from components.actions.demo import get_city_iata
from components.actions.travel_context import TRAVEL_CONTEXT
from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.logging.loggers import APP_LOGGER


class SearchFlights(Action):
    """An action that searches for flights based on origin, destination, and dates."""

    def __init__(self) -> None:
        """Initialize the SearchFlights action."""
        super().__init__(
            description="Searches for real-time flights using an external API based on origin, destination, and dates."
        )
        self.api_key = os.getenv("AVIATIONSTACK_API_KEY")
        self.base_url = "http://api.aviationstack.com/v1/flights"

    @override
    async def _do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action by searching for flights using the Aviationstack API."""
        if not self.api_key:
            msg = "Aviationstack API key not found. Please set the AVIATIONSTACK_API_KEY environment variable."
            raise ValueError(msg)

        # In a real-world scenario, you would parse the user's intent to extract
        # origin, destination, and dates. For this example, we'll extract them
        # from the action parameters which are assumed to be provided by the LLM
        # after it has processed the user's request.

        # log the current travel context
        APP_LOGGER.debug(f"Current travel context: {TRAVEL_CONTEXT}")

        origin = get_city_iata(TRAVEL_CONTEXT.origin or "Melbourne")
        destination = get_city_iata(TRAVEL_CONTEXT.city or "Tokyo")

        if not all([origin, destination]):
            msg = "Missing required parameters: origin, destination."
            raise ValueError(msg)

        try:
            # We'll use a session for async requests
            async with aiohttp.ClientSession() as session:
                origin_code = origin["iata_code"]
                destination_code = destination["iata_code"]

                query_params = {
                    "access_key": self.api_key,
                    "dep_iata": origin_code.upper(),
                    "arr_iata": destination_code.upper(),
                }

                # Build the URL with encoded parameters
                url = f"{self.base_url}?{urllib.parse.urlencode(query_params)}"

                async with session.get(url) as response:
                    response.raise_for_status()  # Raise an exception for HTTP errors
                    data = await response.json()

                    if not data or not data.get("data"):
                        msg = f"No flights found for the route {origin} to {destination}."
                        raise ValueError(msg)

                    # Process the data to extract key details
                    flights = []
                    for flight_data in data["data"]:
                        flights.append(
                            {
                                "flight_number": flight_data["flight"]["iata"],
                                "airline": flight_data["airline"]["name"],
                                "departure_time": flight_data["departure"]["scheduled"],
                                "arrival_time": flight_data["arrival"]["scheduled"],
                                "status": flight_data["flight_status"],
                            }
                        )

                    TRAVEL_CONTEXT.flight_number = flights[0]["flight_number"] if flights else None

                    res = ActionResult()
                    res.set_param("response", str(flights[:10]))  # Limit to first 10 flights
                    res.set_param("travel_context", str(TRAVEL_CONTEXT))
                    return res

        except aiohttp.ClientError as e:
            msg = f"API request failed: {e}"
            raise ValueError(msg)
        except Exception as e:
            msg = f"An unexpected error occurred: {e}"
            raise ValueError(msg)
