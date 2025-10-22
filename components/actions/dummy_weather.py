"""The dummy weather action says its sunny and a temperature."""

from typing import override

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult


class GetWeather(Action):
    """An action that returns the weather."""

    def __init__(self) -> None:
        """Initialize the GetWeather action."""
        super().__init__(description="Returns the current weather")

    @override
    async def do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action by returning the weather."""
        res = ActionResult()
        res.set_param("response", "The weather is sunny with a temperature of 25.3 degrees Celsius.")
        return res
