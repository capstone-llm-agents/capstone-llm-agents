"""The graph-based action narrower that narrows the action space based on a graph of action connections."""

import logging
from typing import override

from components.actions.simple_response import SimpleResponse
from components.actions.travel_context import TRAVEL_CONTEXT
from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_narrower import ActionNarrower, NarrowerContext
from llm_mas.action_system.core.action_space import ActionSpace
from llm_mas.agent.workspace import Workspace
from llm_mas.tools.tool_action_creator import ToolAction


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

    def remove_default_action(self, action: Action) -> None:
        """Remove a default action from the policy."""
        if action in self.default_actions:
            self.default_actions.remove(action)
        else:
            msg = f"Action {action.name} is not a default action."
            raise ValueError(msg)

    def has_default_action(self, action: Action) -> bool:
        """Check if the policy has a default action."""
        return action in self.default_actions

    def add_action_edge(self, action: Action, next_actions: list[Action]) -> None:
        """Add an action edge to the policy."""
        # if it already exists, append to that edge instead
        for edge in self.action_edges:
            if edge.action == action:
                edge.next_actions.extend(next_actions)
                return

        self.action_edges.append(ActionEdge(action, next_actions))

    def remove_action_edge(self, a: Action, b: Action) -> None:
        """Remove an action edge from the policy such that Action A can no longer lead to Action B."""
        for edge in self.action_edges:
            if edge.action == a and b in edge.next_actions:
                edge.next_actions.remove(b)
                return

        msg = f"No action edge found from {a.name} to {b.name}."
        raise ValueError(msg)

    @override
    def narrow(
        self,
        workspace: Workspace,
        action_space: ActionSpace,
        context: ActionContext,
        narrower_context: NarrowerContext | None = None,
    ) -> ActionSpace:
        """Narrow the action space based on the defined action edges."""
        narrowed_actions: list[Action] = []

        # get last action from workspace action history
        last_action_tup = workspace.action_history.get_last_action()

        if last_action_tup is None:
            narrowed_actions = self.default_actions

        else:
            last_action, _, _ = last_action_tup
            # find the action edge corresponding to the last action
            for edge in self.action_edges:
                if edge.action == last_action:
                    narrowed_actions = edge.next_actions
                    break

        new_space = ActionSpace()

        for action in narrowed_actions:
            new_space.add_action(action)

        return new_space

    def action_leads_to(self, action: Action, next_action: Action) -> bool:
        """Check if the action leads to the next action."""
        return any(edge.action == action and next_action in edge.next_actions for edge in self.action_edges)

    def get_action_with_name(self, name: str) -> Action | None:
        """Get an action by its name."""
        for edge in self.action_edges:
            if edge.action.name == name:
                return edge.action
        return None

    @override
    def update_for_new_action(self, action: Action, action_space: ActionSpace) -> None:
        """Update the policy for a new action by adding it to the default actions."""
        # TODO: Implement a more sophisticated update mechanism if needed  # noqa: TD003

        # look at the edges
        logging.getLogger("textual_app").debug(
            "Action edges before adding new action '%s': %s",
            action.name,
            [(edge.action.name, [next_action.name for next_action in edge.next_actions]) for edge in self.action_edges],
        )

        if isinstance(action, ToolAction):
            # add an edge from GetRelevantTools

            get_params = self.get_action_with_name("GetParamsForToolCall")
            if not get_params:
                msg = "Action 'GetParamsForToolCall' not found in the action space."
                raise ValueError(msg)

            if self.action_leads_to(get_params, SimpleResponse()):
                self.remove_action_edge(get_params, SimpleResponse())

            # add the new action to the next actions of GetRelevantTools
            self.add_action_edge(get_params, [action])

        # add an edge for the new action to a response action
        self.add_action_edge(action, [SimpleResponse()])

        # look at the edges
        logging.getLogger("textual_app").debug(
            "Action edges after adding new action '%s': %s",
            action.name,
            [(edge.action.name, [next_action.name for next_action in edge.next_actions]) for edge in self.action_edges],
        )
