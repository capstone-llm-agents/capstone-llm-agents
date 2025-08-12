"""The agent responds to a simple prompt using an LLM."""

from typing import override

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.model_providers.ollama.call_llm import call_llm


class SimpleResponse(Action):
    """The action that generates a simple response using an LLM."""

    @override
    def do(self, params: ActionParams) -> ActionResult:
        """Perform the action by generating a response from an LLM."""
        prompt = params.get_param("prompt")

        if not isinstance(prompt, str):
            msg = "Prompt must be a string."
            raise TypeError(msg)

        response = call_llm(prompt)

        res = ActionResult()
        res.set_param("response", response)
        return res
