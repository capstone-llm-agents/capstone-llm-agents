"""The stop module defines a StopAction class that stops the agent's execution."""

from datetime import datetime
from typing import override

from mem0 import AsyncMemory

from components.actions.memory import MemorySaveLong
from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.logging.loggers import APP_LOGGER
from llm_mas.utils.config.general_config import GENERAL_CONFIG


class StopAction(Action):
    """An action that stops the agent's execution."""

    def __init__(self) -> None:
        """Initialize the StopAction."""
        super().__init__(description="Stops the agent's execution")

    @override
    async def _do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action by stopping the agent."""
        # don't save memory if disabled, just stop immediately
        if not GENERAL_CONFIG.app.memory_enabled():
            return ActionResult()
        try:
            memory = MemorySaveLong()
            await memory._do(params=params, context=context)
        except Exception as e:
            APP_LOGGER.error(e)
        finally:
            return ActionResult()
