"""An action that fetches a link and summarizes its content using OpenAI."""

from typing import override

import requests
from openai import OpenAI

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult


# remove key before commit!
client = OpenAI()


class SummariseURL(Action):
    """An action that summarises the content of a given site URL."""

    def __init__(self) -> None:
        """Initialize the SummariseURL action."""
        super().__init__(description="Fetch and summarise content from a given URL.")

    @override
    async def do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        # Expect a "url" parameter from the request
        url = params.get("url")
        if not url:
            raise ValueError("Missing required parameter: 'url'")

        # Fetch content from the URL
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            text = resp.text
        except Exception as e:
            raise ValueError(f"Failed to fetch URL: {e}")

        # Summarize with OpenAI
        response = client.responses.create(
            model="gpt-4o-mini",
            input=f"Summarize the following webpage content in a concise way:\n\n{text[:8000]}",  
            # char limit
        )

        res = ActionResult()
        res.set_param("url", url)
        res.set_param("summary", response.output_text)

        return res
