"""The agent tries to OTK the user query."""

from typing import override

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.model_providers.ollama.call_llm import call_llm


class OTK(Action):
    """The OTK (One Turn Kill) action class."""

    def __init__(self) -> None:
        """Initialize the OTK action."""
        super().__init__(name="OTK")

    @override
    def do(self, params: ActionParams) -> ActionResult:
        """Perform the OTK action."""
        prompt = params.get_param("prompt")

        if not isinstance(prompt, str):
            msg = "Prompt must be a string."
            raise TypeError(msg)

        response = call_llm(prompt)

        res = ActionResult()
        res.set_param("response", response)
        return res
