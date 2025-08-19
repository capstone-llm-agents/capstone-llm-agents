"""An action that searches for accommodations using the Amadeus API."""

import os
import urllib.parse
from typing import override

import aiohttp

from components.actions.demo import get_city_iata
from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult


class SearchAccommodations(Action):
    """An action that searches for hotels based on a city and dates."""

    def __init__(self) -> None:
        """Initialize the SearchAccommodations action."""
        super().__init__(description="Finds hotel options in a city for specified dates.")
        self.api_key = os.getenv("AMADEUS_API_KEY") # This is your Client ID
        self.api_secret = os.getenv("AMADEUS_API_SECRET") # This is your Client Secret
        self.base_url = "https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city"

    async def get_access_token(self) -> str:
        """Helper function to get the access token from Amadeus."""
        token_url = "https://test.api.amadeus.com/v1/security/oauth2/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.api_secret,
        }
        async with aiohttp.ClientSession() as session:  # noqa: SIM117
            async with session.post(token_url, headers=headers, data=data) as response:
                response.raise_for_status()
                token_data = await response.json()
                return token_data["access_token"]

    @override
    async def do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action by searching for accommodations."""
        if not self.api_key or not self.api_secret:
            msg = "Amadeus API key or secret not found. Please set environment variables."
            raise ValueError(msg)

        city_code = get_city_iata(params.get_param("city"))

        if not city_code:
            msg = "Missing required parameter: city."
            raise ValueError(msg)

        try:
            # Get the access token
            token = await self.get_access_token()
            headers = {"Authorization": f"Bearer {token}"}

            async with aiohttp.ClientSession() as session:
                query_params = {"cityCode": city_code}
                url = f"{self.base_url}?{urllib.parse.urlencode(query_params)}"

                async with session.get(url, headers=headers) as response:
                    response.raise_for_status()
                    data = await response.json()

                    if not data or not data.get("data"):
                        msg = f"No accommodations found in {city_code}."
                        raise ValueError(msg)

                    accommodations = []
                    for hotel in data["data"]:
                        # Extract and format the data we need
                        accommodations.append({
                            "name": hotel["name"],
                            "hotel_id": hotel["hotelId"],
                            "address": hotel["address"].get("lines", ["N/A"])[0],
                        })

                    # We only return a limited number of results to not overload the LLM
                    res = ActionResult()
                    res.set_param("accommodations", accommodations[:5])
                    return res

        except aiohttp.ClientError as e:
            msg = f"API request failed: {e}"
            raise ValueError(msg)
        except Exception as e:
            msg = f"An unexpected error occurred: {e}"
            raise ValueError(msg)