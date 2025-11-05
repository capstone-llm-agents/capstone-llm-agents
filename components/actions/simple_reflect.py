"""The simple reflect action takes an assessment of a response and decides what to do next."""

from typing import override

from components.actions.action_switcher import ActionSwitcher
from components.actions.communicate import Communicate
from components.actions.long_think import LongThink
from components.actions.short_think import ShortThink
from llm_mas.action_system.base.actions.stop import StopAction
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.action_system.core.action_space import ActionSpace
from llm_mas.logging.loggers import APP_LOGGER
from llm_mas.model_providers.api import ModelsAPI


class SimpleReflect(ActionSwitcher):
    """A simple action that decides how to proceed based on an assessment of a response."""

    MAX_QUALITY_SCORE = 10
    MIN_QUALITY_SCORE = 1
    QUALITY_THRESHOLD = 7

    def __init__(self) -> None:
        """Initialize the SimpleReflect action."""
        super().__init__(description="Decide how to proceed based on an assessment of a response")

    @override
    async def _do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action by retrieving parameters for the assessment of the last response."""
        last_result = context.last_result

        # get assessment
        response = last_result.get_param("response")
        quality = last_result.get_param("quality")

        # check they exist
        if response is None:
            msg = "No response found in the last action result."
            raise ValueError(msg)

        if quality is None:
            msg = "No quality score found in the last action result."
            raise ValueError(msg)

        if not isinstance(quality, int):
            msg = f"Quality score is not an integer: {quality}"
            raise TypeError(msg)

        if quality < self.MIN_QUALITY_SCORE or quality > self.MAX_QUALITY_SCORE:
            msg = f"Quality score is out of range (1-10): {quality}"
            raise ValueError(msg)

        APP_LOGGER.debug(f"Response quality: {quality}")

        decision = "proceed" if quality >= self.QUALITY_THRESHOLD else "revise"

        res = ActionResult()
        res.set_param("decision", decision)
        res.set_param("response", response)
        res.set_param("quality", quality)
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

        APP_LOGGER.debug(f"Reflect decision: {decision}")

        if decision == "proceed":
            # only allow StopAction
            action_space.add_action(StopAction())
        else:
            # TODO: actually do a smart retry system  # noqa: TD003
            # check if we did ShortThink or LongThink
            action_history = workspace.action_history

            for action_record in reversed(action_history.history):
                action = action_record[0]
                if isinstance(action, ShortThink):
                    action_space.add_action(LongThink())
                    break
                if isinstance(action, LongThink):
                    action_space.add_action(ShortThink())
                    break

        return action_space
