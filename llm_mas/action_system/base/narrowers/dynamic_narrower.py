"""The graph-based action narrower that narrows the action space based on a graph of action connections."""

from collections.abc import Callable
from typing import override

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_narrower import ActionNarrower, NarrowerContext
from llm_mas.action_system.core.action_space import ActionSpace
from llm_mas.agent.workspace import Workspace


class DynamicEdge(ActionNarrower):
    """Uses a callback to determine the next actions dynamically."""

    def __init__(self, action: Action, narrower: ActionNarrower) -> None:
        """Initialize the dynamic edge with an action and a callback for next actions."""
        self.action = action
        self.narrower = narrower

    @override
    def narrow(
        self,
        workspace: Workspace,
        action_space: ActionSpace,
        context: ActionContext,
        narrower_context: NarrowerContext | None = None,
    ) -> ActionSpace:
        """Return the next actions based on the context."""
        return self.narrower.narrow(workspace, action_space, context, narrower_context)


class IndividualConditionNarrower(ActionNarrower):
    """An action narrower that selects each action if its condition is met."""

    def __init__(
        self,
        next_action: Action,
        select_condition: Callable[[Workspace, ActionSpace, ActionContext, NarrowerContext | None], bool],
    ) -> None:
        """Initialize the dynamic edge with an action and a list of next actions."""
        self.next_action = next_action
        self.select_condition = select_condition

    @override
    def narrow(
        self,
        workspace: Workspace,
        action_space: ActionSpace,
        context: ActionContext,
        narrower_context: NarrowerContext | None = None,
    ) -> ActionSpace:
        """Return the next actions based on the context."""
        new_space = ActionSpace()
        if self.select_condition(workspace, action_space, context, narrower_context):
            new_space.add_action(self.next_action)
        return new_space


class SwitchNarrower(ActionNarrower):
    """A narrower that selects one or more of the next actions based on a condition."""

    def __init__(
        self,
        select_condition: Callable[[Workspace, ActionSpace, ActionContext, NarrowerContext | None], list[Action]],
    ) -> None:
        """Initialize the switch narrower with a list of next actions and a selection condition."""
        self.select_condition = select_condition

    @override
    def narrow(
        self,
        workspace: Workspace,
        action_space: ActionSpace,
        context: ActionContext,
        narrower_context: NarrowerContext | None = None,
    ) -> ActionSpace:
        """Return the next action based on the selection condition."""
        new_space = ActionSpace()
        selected_actions = self.select_condition(workspace, action_space, context, narrower_context)
        for action in selected_actions:
            new_space.add_action(action)
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
    def narrow(
        self,
        workspace: Workspace,
        action_space: ActionSpace,
        context: ActionContext,
        narrower_context: NarrowerContext | None = None,
    ) -> ActionSpace:
        """Narrow the action space by combining the actions from all narrowers."""
        new_space = ActionSpace()
        for narrower in self.narrowers:
            narrowed_space = narrower.narrow(workspace, action_space, context, narrower_context)
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
    def narrow(
        self,
        workspace: Workspace,
        action_space: ActionSpace,
        context: ActionContext,
        narrower_context: NarrowerContext | None = None,
    ) -> ActionSpace:
        """Narrow the action space by intersecting the actions from all narrowers."""
        if not self.narrowers:
            return ActionSpace()

        new_space = action_space
        for narrower in self.narrowers:
            narrowed_space = narrower.narrow(workspace, action_space, context, narrower_context)
            new_space.actions = [action for action in new_space.actions if action in narrowed_space.get_actions()]
        return new_space


class AlwaysNarrower(ActionNarrower):
    """A narrower that always returns the same actions."""

    def __init__(self, actions: list[Action]) -> None:
        """Initialize the always narrower with a list of actions."""
        self.actions = actions

    @override
    def narrow(
        self,
        workspace: Workspace,
        action_space: ActionSpace,
        context: ActionContext,
        narrower_context: NarrowerContext | None = None,
    ) -> ActionSpace:
        """Return the actions defined in this narrower."""
        new_space = ActionSpace()
        for action in self.actions:
            new_space.add_action(action)
        return new_space


class DynamicNarrower(ActionNarrower):
    """A policy that narrows the action space based on a graph of actions."""

    def __init__(self) -> None:
        """Initialize the policy with a list of action edges."""
        self.dynamic_narrowers: list[DynamicEdge] = []
        self.default_actions: list[Action] = []

    def add_default_action(self, action: Action) -> None:
        """Add a default action to the policy."""
        if action in self.default_actions:
            msg = f"Action {action.name} is already a default action."
            raise ValueError(msg)

        self.default_actions.append(action)

    @override
    def narrow(
        self,
        workspace: Workspace,
        action_space: ActionSpace,
        context: ActionContext,
        narrower_context: NarrowerContext | None = None,
    ) -> ActionSpace:
        """Narrow the action space based on the defined action edges."""
        new_space = ActionSpace()
        next_actions: list[Action] = []

        # get last action from workspace action history
        last_action_tup = workspace.action_history.get_last_action()

        if last_action_tup is None:
            next_actions = self.default_actions
        else:
            action = last_action_tup[0]

            # narrow based on its dynamic narrower
            narrower = next((n for n in self.dynamic_narrowers if n.action == action), None)
            if narrower is None:
                msg = f"No dynamic narrower found for action {action.name}."
                raise ValueError(msg)

            next_actions = narrower.narrow(workspace, action_space, context, narrower_context).get_actions()

        for action in next_actions:
            new_space.add_action(action)

        return new_space

    @override
    def update_for_new_action(self, action: Action, action_space: ActionSpace) -> None:
        """Update the policy for a new action by adding it to the default actions."""
        msg = "This method should be overridden by subclasses."
        raise NotImplementedError(msg)

    def add_dynamic_edge(self, action: Action, narrower: ActionNarrower) -> None:
        """Add a dynamic edge to the policy."""
        if any(edge.action == action for edge in self.dynamic_narrowers):
            msg = f"Dynamic edge for action {action.name} already exists."
            raise ValueError(msg)

        self.dynamic_narrowers.append(DynamicEdge(action, narrower))
