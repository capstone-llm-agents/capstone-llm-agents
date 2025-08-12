"""The stop module defines a StopAction class that stops the agent's execution."""

from typing import override

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult


class StopAction(Action):
    """An action that stops the agent's execution."""

    @override
    def do(self, params: ActionParams, context: ActionResult) -> None:
        """Perform the action by stopping the agent."""
