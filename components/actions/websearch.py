"""An action that performs a web search using OpenAI."""

import os
from typing import override

from dotenv import load_dotenv
from openai import AsyncOpenAI

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult

# remove key when commit please
load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class WebSearch(Action):
    """An action that does a basic websearch."""

    def __init__(self) -> None:
        """Initialise the WebSearch action."""
        super().__init__(description="Get web result.")

    @override
    async def do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        chat_history = context.conversation.get_chat_history()
        messages = chat_history.as_dicts()

        last_message = messages[-1] if messages else None
        if not last_message:
            msg = "No chat history available for web search."
            raise ValueError(msg)

        query = last_message["content"]

        # do the search asynchronously
        response = await client.responses.create(
            model="gpt-4o-mini",
            tools=[
                {
                    "type": "web_search_preview",
                    "search_context_size": "low",
                },
            ],
            input=query,
        )

        res = ActionResult()
        res.set_param("query", query)
        res.set_param("response", response.output_text)

        return res
