"""The agent responds to a simple prompt using an LLM."""

from typing import override

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.model_providers.ollama.call_llm import call_llm


class SimpleResponse(Action):
    """The action that generates a simple response using an LLM."""

    def __init__(self) -> None:
        """Initialize the SimpleResponse action."""
        super().__init__(
            description="Responds to simple requests that can be answered with a simple response.",
        )

    @override
    async def do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action by generating a response from an LLM."""
        chat_history = context.conversation.get_chat_history()

        messages = chat_history.as_dicts()

        last_message = messages[-1] if messages else None

        if not last_message:
            msg = "No chat history available to respond to."
            raise ValueError(msg)

        if not context.last_result.is_empty():
            # override content
            last_message["content"] = f"""
            Context:
            {context.last_result.as_json_pretty()}

            Prompt:
            {last_message["content"]}
            """

        response = await call_llm(last_message["content"])

        res = ActionResult()
        res.set_param("response", response)

        return res
