"""The hello action simply prints a greeting message."""

from typing import override

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_params import ActionParams


class SayHello(Action):
    """An action that prints a greeting message."""

    @override
    def do(self, params: ActionParams) -> None:
        """Perform the action by printing a greeting."""
        print("Hello world!")  # noqa: T201
