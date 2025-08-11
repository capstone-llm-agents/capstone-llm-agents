"""The graph-based action narrower that narrows the action space based on a graph of action connections."""

from typing import override

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_narrower import ActionNarrower
from llm_mas.action_system.core.action_space import ActionSpace
from llm_mas.agent.workspace import Workspace


class ActionEdge:
    """Represents an edge in the action graph."""

    def __init__(self, action: Action, next_actions: list[Action]) -> None:
        """Initialize the action edge with an action and its possible next actions."""
        self.action = action
        self.next_actions = next_actions


class GraphBasedNarrower(ActionNarrower):
    """A policy that narrows the action space based on a graph of actions."""

    def __init__(self) -> None:
        """Initialize the policy with a list of action edges."""
        self.action_edges: list[ActionEdge] = []

        self.default_actions: list[Action] = []

    def add_default_action(self, action: Action) -> None:
        """Add a default action to the policy."""
        self.default_actions.append(action)

    def add_action_edge(self, action: Action, next_actions: list[Action]) -> None:
        """Add an action edge to the policy."""
        self.action_edges.append(ActionEdge(action, next_actions))

    @override
    def narrow(self, workspace: Workspace, action_space: ActionSpace) -> ActionSpace:
        """Narrow the action space based on the defined action edges."""
        narrowed_actions: list[Action] = []

        # get last action from workspace action history
        last_action = workspace.action_history.get_last_action()

        if last_action is None:
            # If no last action, return the original action space
            narrowed_actions = self.default_actions

        else:
            # find the action edge corresponding to the last action
            for edge in self.action_edges:
                if edge.action == last_action:
                    narrowed_actions = edge.next_actions
                    break

        new_space = ActionSpace()

        for action in narrowed_actions:
            new_space.add_action(action)

        return new_space
