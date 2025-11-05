"""An entry point action that takes the action to the beginning of its long thinking process."""

from typing import override

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult


class LongThink(Action):
    """An action that represents the entry point for the agent's long thinking process."""

    def __init__(self) -> None:
        """Initialize the Entry action."""
        super().__init__(
            description="The entry point action that starts the agent's long thinking process.",
        )

    @override
    async def _do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Start long thinking process."""
        return ActionResult()
