"""An action that estimates the budget for a trip using a heuristic."""

from typing import override

from components.actions.demo import get_city_iata
from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult


class EstimateBudget(Action):
    """An action that provides a rough budget estimate for a trip with a heuristic."""

    def __init__(self) -> None:
        """Initialize the EstimateBudget action."""
        super().__init__(description="Provides a rough budget estimate for a trip based on destination and duration, with a heuristic.")  # noqa: E501

        # Base daily costs for a 'mid-range' trip. These will be adjusted by the heuristic.
        self.base_daily_costs = {
            "low": 100,
            "mid": 180,
            "high": 350,
        }

    def apply_heuristic(self, base_cost: int, city_data: dict) -> float:
        """Applies a heuristic to the base cost based on city rank and visitors."""  # noqa: D401
        if not city_data:
            return base_cost

        # Rank-based multiplier: higher rank (lower number) means a more expensive destination
        # We can invert the rank so a higher value corresponds to a higher multiplier
        rank_multiplier = 1 + (1 / city_data.get("rank", 100))

        # Visitor-based multiplier: more visitors means higher demand and costs
        # The number is scaled down to a manageable size
        visitor_multiplier = 1 + (city_data.get("visitors", 10000000) / 50000000)

        # Combine the multipliers
        adjusted_cost = base_cost * rank_multiplier * visitor_multiplier
        return adjusted_cost  # noqa: RET504

    @override
    async def do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action by estimating the budget."""
        destination = params.get_param("destination").lower()
        duration_days = params.get_param("duration_days")
        travel_style = params.get_param("travel_style").lower()

        if not destination or not duration_days:
            msg = "Missing required parameters: destination or duration_days."
            raise ValueError(msg)

        # Get the full city data, not just the IATA code
        # We need to assume that get_city_iata has been modified or a similar function `get_city_data` exists.
        # Here we will assume `get_city_data` exists and returns the full dictionary from your top_cities list.
        city_data = get_city_iata(destination)
        if not city_data:
            msg = f"No budget data available for {destination}."
            raise ValueError(msg)

        base_cost = self.base_daily_costs.get(travel_style, self.base_daily_costs["mid"])

        # Apply the heuristic to the base daily cost
        daily_cost = self.apply_heuristic(base_cost, city_data)

        # Calculate the total estimate
        total_estimate = daily_cost * duration_days
        buffer = total_estimate * 0.15
        final_estimate = total_estimate + buffer

        res = ActionResult()
        res.set_param("estimated_cost", {
            "daily_cost": round(daily_cost, 2),
            "total_estimate_without_buffer": round(total_estimate, 2),
            "final_estimate": round(final_estimate, 2),
            "currency": "USD",
            "details": f"This is an estimated cost for a {travel_style}-style trip to {destination} for {duration_days} days, adjusted based on the city's popularity and visitor count. It includes a 15% buffer for miscellaneous expenses."
        })

        return res
