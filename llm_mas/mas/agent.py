"""An agent is an entity that can perform actions to complete tasks."""

import logging

from llm_mas.action_system.base.actions.stop import StopAction
from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_narrower import ActionNarrower
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.action_system.core.action_selector import ActionSelector
from llm_mas.action_system.core.action_space import ActionSpace
from llm_mas.agent.workspace import Workspace
from llm_mas.communication.task.agent_task import Task
from llm_mas.mas.entity import Entity
from llm_mas.tools.tool_manager import ToolManager


class Agent(Entity):
    """Base class for all agents in the system."""

    def __init__(  # noqa: PLR0913
        self,
        name: str,
        description: str,
        action_space: ActionSpace,
        narrower: ActionNarrower,
        selector: ActionSelector,
        tool_manager: ToolManager,
        workspace: Workspace | None = None,
    ) -> None:
        """Initialize the agent with a name, action space, narrowing policy, and action selection strategy."""
        super().__init__(name, role="assistant", description=description)

        # full action space for the agent
        self.action_space = action_space

        # space narrowing policy for the agent
        self.narrower = narrower

        # action selection strategy for the agent
        self.selector = selector

        # workspace
        self.workspace = workspace if workspace is not None else Workspace()

        # tools manager
        self.tool_manager = tool_manager

        # task stack
        self.task_stack: list[Task] = []

    async def act(self, context: ActionContext, params: ActionParams | None = None) -> ActionResult:
        """Perform an action in the workspace using the agent's action selection strategy."""
        action = await self.select_action(context)
        return await self.do_selected_action(action, context, params)

    async def select_action(self, context: ActionContext) -> Action:
        """Select an action to perform."""
        narrowed_action_space = self.narrower.narrow(self.workspace, self.action_space, context)
        return await self.selector.select_action(narrowed_action_space, context)

    async def do_selected_action(
        self,
        action: Action,
        context: ActionContext,
        params: ActionParams | None = None,
    ) -> ActionResult:
        """Perform the selected action."""
        # TODO: Get parameters from some source like ParamProvider  # noqa: TD003
        params = params if params is not None else ActionParams()

        res = await action.do(params, context)
        self.workspace.action_history.add_action(action, res, context)
        return res

    def add_action(self, action: Action) -> None:
        """Add an action to the agent's action space."""
        self.action_space.add_action(action)

    def add_action_during_runtime(self, action: Action) -> None:
        """Add an action to the agent's action space during runtime."""
        logging.getLogger("textual_app").info("Adding action: %s", action.name)
        self.add_action(action)
        self.narrower.update_for_new_action(action, self.action_space)

    async def work(self, context: ActionContext) -> tuple[ActionResult, ActionContext]:
        """Perform work by executing actions in the agent's action space."""
        if not self.action_space.has_action(StopAction()):
            msg = "StopAction must be in the action space to stop the agent."
            raise ValueError(msg)

        res = ActionResult()
        while not self.finished_working():
            res = await self.act(context)
            # TODO: Wrap the context properly  # noqa: TD003
            context = ActionContext.from_action_result(res, context)
        return res, context

    def finished_working(self) -> bool:
        """Check if the agent has finished working."""
        return self.workspace.action_history.has_action(StopAction())

    def add_task(self, task: Task) -> None:
        """Add a task to the agent's task stack."""
        self.task_stack.append(task)

    def get_current_task(self) -> Task | None:
        """Get the current task from the agent's task stack."""
        if not self.task_stack:
            return None
        return self.task_stack[-1]

    def complete_current_task(self) -> Task | None:
        """Complete the current task and remove it from the task stack."""
        if not self.task_stack:
            return None
        return self.task_stack.pop()
