"""The random selector module provides a base class for random selection of actions in the action system."""

import json
import re
from collections.abc import Awaitable, Callable
from typing import override

from components.actions.dummy_actions import (
    GET_CURRENT_DATE,
    GET_CURRENT_TIME,
    GET_RANDOM_NUMBER,
    GET_WEATHER,
    SOLVE_MATH,
)
from components.actions.tools import GetTools
from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.action_system.core.action_selector import ActionSelector
from llm_mas.action_system.core.action_space import ActionSpace
from llm_mas.mas.conversation import AssistantMessage, UserAssistantExample, UserMessage
from llm_mas.model_providers.ollama.call_llm import (
    call_llm_with_examples,
)


# random selection policy
class LLMSelector(ActionSelector):
    """A selection policy that randomly selects an action from the narrowed action space."""

    def __init__(self, llm_call: Callable[[str], Awaitable[str]]) -> None:
        """Initialize the LLMSelector with a callable for LLM calls."""
        self.llm_call = llm_call

    @override
    async def select_action(self, action_space: ActionSpace, context: ActionContext) -> Action:
        """Select an action from the action space using an LLM."""
        # only 1 choice then just quit
        if len(action_space.get_actions()) == 1:
            return action_space.get_actions()[0]

        examples: list[UserAssistantExample] = []

        actions1: list[Action] = [
            GET_RANDOM_NUMBER,
            SOLVE_MATH,
            GET_WEATHER,
        ]

        res1 = ActionResult()
        res1.set_param("prompt", "What is the weather like today?")
        context1 = ActionContext(context.conversation, res1, context.mcp_client)

        examples.append(self.craft_example(actions1, context1, 2))

        actions2: list[Action] = [GET_CURRENT_DATE, GET_CURRENT_TIME, GET_WEATHER, GET_RANDOM_NUMBER]

        res2 = ActionResult()
        res2.set_param("prompt", "What is the current date?")
        context2 = ActionContext(context.conversation, res2, context.mcp_client)

        actions3: list[Action] = [GET_CURRENT_DATE, GET_CURRENT_TIME, GetTools(), GET_WEATHER, GET_RANDOM_NUMBER]

        res3 = ActionResult()
        res3.set_param("prompt", "What tools do you have?")
        context3 = ActionContext(context.conversation, res3, context.mcp_client)

        examples.append(self.craft_example(actions3, context3, 2))
        examples.append(self.craft_example(actions2, context2, 0))

        response = await call_llm_with_examples(
            examples,
            UserMessage(self.get_select_action_prompt(action_space.get_actions(), context)),
        )

        # TODO: use the params  # noqa: TD003
        name, params = self.parse_response(response)

        # find action
        for action in action_space.get_actions():
            if action.name == name:
                return action

        msg = f"Action '{name}' not found in the action space."
        raise ValueError(msg)

    def get_select_action_prompt(self, actions: list[Action], context: ActionContext) -> str:
        """Generate a prompt for selecting an action from a list of actions."""
        actions_str = json.dumps([action.as_json() for action in actions], indent=4)

        prompt = ""

        prompt += f"""
        Choose an action from the following list of actions:
        {actions_str}
        """

        prompt += "\n\n"
        if not context.last_result.is_empty():
            prompt += f"Context: {context.last_result.as_json_pretty()}\n\n"

        prompt += """Respond ONLY with the action name and parameters in JSON format, like this:
        ```json
        {{
            "name": "ActionName",
            "params": {{
                "param1": "value1",
                "param2": "value2"
            }}
        }}`
        """

        return prompt.strip()

    def craft_example(self, actions: list[Action], context: ActionContext, chosen_index: int) -> UserAssistantExample:
        """Craft an example from a list of actions."""
        prompt = self.get_select_action_prompt(actions, context)

        user_message = UserMessage(prompt)

        assistant_message = AssistantMessage(json.dumps(actions[chosen_index].as_json(), indent=4))

        return UserAssistantExample(user_message, assistant_message)

    def parse_response(self, response: str) -> tuple[str, ActionParams]:
        """Parse the LLM response to extract the selected action."""
        choice_str = self.extract_json_from_response(response)

        choice = json.loads(choice_str)

        params = ActionParams()
        for key, value in choice.get("params", {}).items():
            params.set_param(key, value)

        name = choice.get("name")
        if not name:
            msg = "No action name provided in the choice."
            raise ValueError(msg)

        return name, params

    def extract_json_from_response(self, response: str) -> str:
        """Extract and parse JSON from a string, removing markdown formatting if needed."""
        # Remove ```json ... ``` or ``` ... ``` blocks
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response, re.DOTALL)
        json_str = match.group(1) if match else response.strip()
        return json_str.strip()
