"""The get_secret action simply returns a secret message."""

from typing import override

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult


class GetSecret(Action):
    """An action that returns a secret message."""

    def __init__(self) -> None:
        """Initialize the GetSecret action."""
        super().__init__(description="Returns a secret message")

    @override
    async def do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action by returning a secret message."""
        res = ActionResult()
        res.set_param("response", "AMOGUS")
        return res
