"""The simple reflection action module defines an action that reflects on the quality of its response."""

import json
from typing import override

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.model_providers.api import ModelsAPI
from llm_mas.utils.config.models_config import ModelType
from llm_mas.utils.json_parser import extract_json_from_response


class AssessResponse(Action):
    """A simple action that assesses the quality of a response."""

    def __init__(self) -> None:
        """Initialize the AssessResponse action."""
        super().__init__(description="Assess the quality of a response")

    @override
    async def _do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action by assessing the quality of the last response."""
        # get response
        agent_res = context.last_result.get_param("response")

        if agent_res is None:
            msg = "No response found in the last action result."
            raise ValueError(msg)

        # user message
        last_message = self.get_last_message_content(context)

        prompt = f"""You are an expert assistant that reviews the quality of responses from other AI assistants.
        The goal is to ensure high-quality, helpful, and relevant responses.
        You are to rate the quality of the response on a scale from 1 to 10, where 10 is the highest quality.
        Quality is determined by relevance, accuracy, helpfulness, and clarity.
        If the response is factually incorrect, irrelevant, or unhelpful, it should receive a low score.
        If the response is accurate, relevant, and helpful, it should receive a high score.
        Responses that claim that the task could not be completed should receive a low score.
        For example, "As an AI language model, I do not have access to real-time data." or "Sorry, I cannot help with that." should receive a low score.
        ANY RESPONSE THAT DOES NOT DIRECTLY ANSWER THE USER'S QUESTION SHOULD RECEIVE A LOW SCORE.

        Here is the user message:
        {last_message}

        Here is the response to review:
        {agent_res}

        Please provide a JSON object with the following fields:
        - quality: A rating from 1 to 10 of the quality of the response.
        - issues: A list of any issues found in the response, or an empty list if none.
        - suggestions: A list of suggestions for improvement, or an empty list if none."""
        response = await ModelsAPI.call_llm(prompt, model=ModelType.DEFAULT)

        content = extract_json_from_response(response)

        try:
            params_dict = json.loads(content)
        except json.JSONDecodeError as e:
            msg = f"Failed to parse JSON from response: {content}"
            raise ValueError(msg) from e

        # check if params dict matches expected format
        if not isinstance(params_dict, dict):
            msg = f"Expected a JSON object but got: {params_dict}"
            raise TypeError(msg)

        expected_keys = {"quality", "issues", "suggestions"}
        if not expected_keys.issubset(params_dict.keys()):
            msg = f"Missing expected keys in response. Expected at least {expected_keys}, but got {params_dict.keys()}"
            raise ValueError(msg)

        res = ActionResult()
        for key, value in params_dict.items():
            res.set_param(key, value)

        res.set_param("response", agent_res)

        return res
