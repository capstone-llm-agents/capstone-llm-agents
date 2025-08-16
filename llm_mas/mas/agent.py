"""An agent is an entity that can perform actions to complete tasks."""

from llm_mas.action_system.base.actions.stop import StopAction
from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_narrower import ActionNarrower
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.action_system.core.action_selector import ActionSelector
from llm_mas.action_system.core.action_space import ActionSpace
from llm_mas.agent.workspace import Workspace
from llm_mas.mas.entity import Entity


class Agent(Entity):
    """Base class for all agents in the system."""

    def __init__(
        self,
        name: str,
        action_space: ActionSpace,
        narrower: ActionNarrower,
        selector: ActionSelector,
        workspace: Workspace | None = None,
    ) -> None:
        """Initialize the agent with a name, action space, narrowing policy, and action selection strategy."""
        super().__init__(name, role="assistant")

        # full action space for the agent
        self.action_space = action_space

        # space narrowing policy for the agent
        self.narrower = narrower

        # action selection strategy for the agent
        self.selector = selector

        # workspace
        self.workspace = workspace if workspace is not None else Workspace()

    def act(self, context: ActionContext, params: ActionParams | None = None) -> ActionResult:
        """Perform an action in the workspace using the agent's action selection strategy."""
        action = self.select_action(context)
        return self.do_selected_action(action, context, params)

    def select_action(self, context: ActionContext) -> Action:
        """Select an action to perform."""
        narrowed_action_space = self.narrower.narrow(self.workspace, self.action_space)
        return self.selector.select_action(narrowed_action_space, context)

    def do_selected_action(
        self,
        action: Action,
        context: ActionContext,
        params: ActionParams | None = None,
    ) -> ActionResult:
        """Perform the selected action."""
        # TODO: Get parameters from some source like ParamProvider  # noqa: TD003
        params = params if params is not None else ActionParams()

        res = action.do(params, context)
        self.workspace.action_history.add_action(action, res)
        return res

    def add_action(self, action: Action) -> None:
        """Add an action to the agent's action space."""
        self.action_space.add_action(action)

    def work(self, context: ActionContext) -> None:
        """Perform work by executing actions in the agent's action space."""
        if not self.action_space.has_action(StopAction()):
            msg = "StopAction must be in the action space to stop the agent."
            raise ValueError(msg)

        while not self.finished_working():
            res = self.act(context)
            # TODO: Wrap the context properly
            context = ActionContext(context.conversation, res)

    def finished_working(self) -> bool:
        """Check if the agent has finished working."""
        return self.workspace.action_history.has_action(StopAction())
