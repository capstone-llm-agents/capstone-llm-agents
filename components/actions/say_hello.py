"""The hello action simply prints a greeting message."""

from typing import override

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult


class SayHello(Action):
    """An action that prints a greeting message."""

    def __init__(self) -> None:
        """Initialize the SayHello action."""
        super().__init__(description="Prints a greeting message")

    @override
    def do(self, params: ActionParams, context: ActionResult) -> ActionResult:
        """Perform the action by printing a greeting."""
        print("Hello world!")  # noqa: T201
        return ActionResult()
