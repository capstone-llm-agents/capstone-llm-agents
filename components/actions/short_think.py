"""An entry point action that takes the action to the beginning of its short thinking process."""

from typing import override

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult


class ShortThink(Action):
    """An action that represents the entry point for the agent's short thinking process."""

    def __init__(self) -> None:
        """Initialize the Entry action."""
        super().__init__(
            description="The entry point action that starts the agent's short thinking process.",
        )

    @override
    async def _do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Start short thinking process."""
        return ActionResult()
