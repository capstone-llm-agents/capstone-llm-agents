"""The hello action simply prints a greeting message."""

from typing import override

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult


class SayHello(Action):
    """An action that prints a greeting message."""

    def __init__(self) -> None:
        """Initialize the SayHello action."""
        super().__init__(description="Prints a greeting message")

    @override
    async def _do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action by printing a greeting."""
        res = ActionResult()
        res.set_param("greeting", "Hello, world!")
        return res
