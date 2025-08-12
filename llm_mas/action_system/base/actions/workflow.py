"""The workflow module contains the core actions and strategies for managing workflows in the multi-agent system."""

from typing import override

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult


class Workflow(Action):
    """A workflow is a special action that can contain other actions."""

    def __init__(self, name: str) -> None:
        """Initialize the workflow with a name."""
        super().__init__()
        self.name = name
        self.actions: list[Action] = []

    def add_action(self, action: Action) -> None:
        """Add an action to the workflow."""
        self.actions.append(action)

    # TODO: Extend ActionParams to WorkflowActionParams for Workflow actions # noqa: TD003
    @override
    def do(self, params: ActionParams, context: ActionResult) -> ActionResult:
        """Execute all actions in the workflow."""
        for action in self.actions:
            res = action.do(params, context)
            context = res

        # TODO: return actual result gg
        return ActionResult()
