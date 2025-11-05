"""The workflow module contains the core actions and strategies for managing workflows in the multi-agent system."""

from typing import override

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult


class Workflow(Action):
    """A workflow is a special action that can contain other actions."""

    def __init__(self, name: str) -> None:
        """Initialize the workflow with a name."""
        super().__init__(description="A workflow that contains multiple actions", name=name)
        self.actions: list[Action] = []

    def add_action(self, action: Action) -> None:
        """Add an action to the workflow."""
        self.actions.append(action)

    # TODO: Extend ActionParams to WorkflowActionParams for Workflow actions # noqa: TD003
    @override
    async def _do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Execute all actions in the workflow."""
        for action in self.actions:
            res = await action._do(params, context)
            # TODO: wrap the context properly  # noqa: TD003
            context = ActionContext.from_action_result(res, context)

        # TODO: return actual result gg  # noqa: TD003
        return ActionResult()
