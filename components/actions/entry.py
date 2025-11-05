"""An entry point action that takes the action to the beginning of its process."""

from typing import override

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult


class Entry(Action):
    """An action that represents the entry point for the agent's process."""

    def __init__(self) -> None:
        """Initialize the Entry action."""
        super().__init__(
            description="The entry point action that starts the agent's process.",
        )

    @override
    async def _do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action by generating a response from an LLM."""
        return ActionResult()
