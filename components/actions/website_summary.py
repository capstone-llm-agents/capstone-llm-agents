"""An action that fetches a link and summarizes its content using OpenAI."""

import os
from typing import override

import requests
from dotenv import load_dotenv
from openai import OpenAI

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class SummariseURL(Action):
    """An action that summarises the content of a given site URL."""

    def __init__(self) -> None:
        """Initialize the SummariseURL action."""
        super().__init__(description="Fetch and summarise content from a given URL.")

    @override
    async def _do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        # expect a "url" parameter from the request
        url = params.get_param("url")
        if not url:
            msg = "Missing required parameter: 'url'"
            raise ValueError(msg)

        # Fetch content from the URL
        try:
            resp = requests.get(url, timeout=10)  # noqa: ASYNC210 (function is async because of the base class)
            resp.raise_for_status()
            text = resp.text
        except requests.RequestException as e:
            msg = f"Failed to fetch URL: {url}. Error: {e!s}"
            raise ValueError(msg) from e

        # summarize with OpenAI
        response = client.responses.create(
            model="gpt-4o-mini",
            input=f"Summarize the following webpage content in a concise way:\n\n{text[:8000]}",
            # char limit
        )

        res = ActionResult()
        res.set_param("url", url)
        res.set_param("summary", response.output_text)

        return res
