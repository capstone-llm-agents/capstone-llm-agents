"""The graph-based action narrower that narrows the action space based on a graph of action connections."""

from typing import override

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_narrower import ActionNarrower
from llm_mas.action_system.core.action_space import ActionSpace
from llm_mas.agent.workspace import Workspace


class DynamicEdge(ActionNarrower):
    """Uses a callback to determine the next actions dynamically."""

    def __init__(self, action: Action) -> None:
        """Initialize the dynamic edge with an action and a callback for next actions."""
        self.action = action

    @override
    def narrow(self, workspace: Workspace, action_space: ActionSpace, context: ActionContext) -> ActionSpace:
        """Return the next actions based on the context."""
        msg = "This method should be overridden by subclasses."
        raise NotImplementedError(msg)


class IndividualConditionNarrower(DynamicEdge):
    """A dynamic edge that selects each action if its condition is met."""

    def __init__(self, action: Action, next_action: Action) -> None:
        """Initialize the dynamic edge with an action and a list of next actions."""
        super().__init__(action)
        self.next_action = next_action

    def select(self, context: ActionContext) -> bool:
        """Check if the action's condition is met."""
        msg = "This method should be overridden by subclasses."
        raise NotImplementedError(msg)

    @override
    def narrow(self, workspace: Workspace, action_space: ActionSpace, context: ActionContext) -> ActionSpace:
        """Return the next actions based on the context."""
        new_space = ActionSpace()
        if self.select(context):
            new_space.add_action(self.next_action)
        return new_space


class CumulativeMultiNarrower(ActionNarrower):
    """A narrower that contains multiple narrowers and returns their combined actions."""

    def __init__(self) -> None:
        """Initialize the multi narrower with an empty list of narrowers."""
        self.narrowers: list[ActionNarrower] = []

    def add_narrower(self, narrower: ActionNarrower) -> None:
        """Add a narrower to the multi narrower."""
        self.narrowers.append(narrower)

    @override
    def narrow(self, workspace: Workspace, action_space: ActionSpace, context: ActionContext) -> ActionSpace:
        """Narrow the action space by combining the actions from all narrowers."""
        new_space = ActionSpace()
        for narrower in self.narrowers:
            narrowed_space = narrower.narrow(workspace, action_space, context)
            for action in narrowed_space.get_actions():
                new_space.add_action(action)
        return new_space


class ReductiveMultiNarrower(ActionNarrower):
    """A narrower that contains multiple narrowers and returns the intersection of their actions."""

    def __init__(self) -> None:
        """Initialize the multi narrower with an empty list of narrowers."""
        self.narrowers: list[ActionNarrower] = []

    def add_narrower(self, narrower: ActionNarrower) -> None:
        """Add a narrower to the multi narrower."""
        self.narrowers.append(narrower)

    @override
    def narrow(self, workspace: Workspace, action_space: ActionSpace, context: ActionContext) -> ActionSpace:
        """Narrow the action space by intersecting the actions from all narrowers."""
        if not self.narrowers:
            return ActionSpace()

        new_space = action_space
        for narrower in self.narrowers:
            narrowed_space = narrower.narrow(workspace, action_space, context)
            new_space.actions = [action for action in new_space.actions if action in narrowed_space.get_actions()]
        return new_space


class AlwaysNarrower(DynamicEdge):
    """A dynamic edge that always returns the same actions."""

    def __init__(self, action: Action) -> None:
        """Initialize the dynamic edge with an action and a list of next actions."""
        super().__init__(action)
        self.next_actions = []

    @override
    def narrow(self, workspace: Workspace, action_space: ActionSpace, context: ActionContext) -> ActionSpace:
        """Return the next actions."""
        new_space = ActionSpace()
        for action in self.next_actions:
            new_space.add_action(action)
        return new_space

    def add_action(self, action: Action) -> None:
        """Add an action to the next actions."""
        self.next_actions.append(action)


class DynamicNarrower(ActionNarrower):
    """A policy that narrows the action space based on a graph of actions."""

    def __init__(self) -> None:
        """Initialize the policy with a list of action edges."""
        self.dynamic_narrowers: list[DynamicEdge] = []
        self.default_actions: list[Action] = []

    def add_default_action(self, action: Action) -> None:
        """Add a default action to the policy."""
        self.default_actions.append(action)

    @override
    def narrow(self, workspace: Workspace, action_space: ActionSpace, context: ActionContext) -> ActionSpace:
        """Narrow the action space based on the defined action edges."""
        new_space = ActionSpace()
        next_actions: list[Action] = []

        # get last action from workspace action history
        last_action_tup = workspace.action_history.get_last_action()

        if last_action_tup is None:
            next_actions = self.default_actions
        else:
            # narrow based on its dynamic narrower
            narrower = next((n for n in self.dynamic_narrowers if n.action == last_action_tup[0]), None)
            if narrower is None:
                msg = f"No dynamic narrower found for action {last_action_tup[0].name}."
                raise ValueError(msg)

            next_actions = narrower.narrow(workspace, action_space, context).get_actions()

        for action in next_actions:
            new_space.add_action(action)

        return new_space

    @override
    def update_for_new_action(self, action: Action, action_space: ActionSpace) -> None:
        """Update the policy for a new action by adding it to the default actions."""
        msg = "This method should be overridden by subclasses."
        raise NotImplementedError(msg)
