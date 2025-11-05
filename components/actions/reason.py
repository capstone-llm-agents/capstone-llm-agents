"""The reason through action determines what type of user input was received and decides the next steps."""

from typing import override

from components.actions.action_switcher import ActionSwitcher
from components.actions.long_think import LongThink
from components.actions.short_think import ShortThink
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.action_system.core.action_space import ActionSpace
from llm_mas.logging.loggers import APP_LOGGER


class Reason(ActionSwitcher):
    """A simple action that decides how to proceed based on an assessment of user input."""

    def __init__(self) -> None:
        """Initialize the Reason action."""
        super().__init__(description="Decide how to proceed based on an assessment of user input")

    @override
    async def _do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action by retrieving parameters for the assessment of the last response."""
        last_result = context.last_result

        # get assessment
        is_task = last_result.get_param("is_task")  # bool
        requires_real_time_info = last_result.get_param("requires_real_time_info")
        requires_specific_knowledge = last_result.get_param("requires_specific_knowledge")

        # check they exist
        if is_task is None:
            msg = "No is_task found in the last action result."
            raise ValueError(msg)
        if requires_real_time_info is None:
            msg = "No requires_real_time_info found in the last action result."
            raise ValueError(msg)
        if requires_specific_knowledge is None:
            msg = "No requires_specific_knowledge found in the last action result."
            raise ValueError(msg)

        APP_LOGGER.debug("Reasoning through user input assessment:")
        APP_LOGGER.debug(f"User input is task: {is_task}")
        APP_LOGGER.debug(f"User input requires real-time info: {requires_real_time_info}")
        APP_LOGGER.debug(f"User input requires specific knowledge: {requires_specific_knowledge}")

        # if it is a task then we can do it
        decision = "quick"
        if is_task or requires_real_time_info or requires_specific_knowledge:
            decision = "long"

        res = ActionResult()
        res.set_param("decision", decision)
        return res

    @override
    def narrow(
        self,
        workspace,
        action_space,
        context: ActionContext,
        narrower_context=None,
    ) -> ActionSpace:
        """Narrow the action space based on the quality of the last response."""
        last_result = context.last_result

        # get assessment
        decision = last_result.get_param("decision")

        if decision is None:
            msg = "No decision found in the last action result."
            raise ValueError(msg)

        action_space = ActionSpace()

        APP_LOGGER.debug(f"Reason through decision: {decision}")

        if decision == "quick":
            action_space.add_action(ShortThink())
        else:
            action_space.add_action(LongThink())
        return action_space
