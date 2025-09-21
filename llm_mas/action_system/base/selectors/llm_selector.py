"""The random selector module provides a base class for random selection of actions in the action system."""

import json
import logging
from collections.abc import Awaitable, Callable
from typing import override

from components.actions.dummy_actions import (
    GET_CURRENT_DATE,
    GET_CURRENT_TIME,
    GET_RANDOM_NUMBER,
    SOLVE_MATH,
)
from components.actions.websearch import WebSearch
from components.actions.website_summary import SummariseURL
from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.action_system.core.action_selector import ActionSelector
from llm_mas.action_system.core.action_space import ActionSpace
from llm_mas.logging.loggers import APP_LOGGER
from llm_mas.mas.conversation import AssistantMessage, UserAssistantExample, UserMessage
from llm_mas.mas.user import User
from llm_mas.model_providers.openai.call_llm import (
    call_llm_with_examples,
)
from llm_mas.utils.json_parser import extract_json_from_response


# random selection policy
class LLMSelector(ActionSelector):
    """A selection policy that randomly selects an action from the narrowed action space."""

    def __init__(self, llm_call: Callable[[str], Awaitable[str]]) -> None:
        """Initialize the LLMSelector with a callable for LLM calls."""
        self.llm_call = llm_call

    @override
    async def select_action(self, action_space: ActionSpace, context: ActionContext) -> Action:
        """Select an action from the action space using an LLM."""
        # if the action space is empty, raise an error
        if not action_space.get_actions():
            msg = "Action space is empty. Cannot select an action."
            raise ValueError(msg)

        # only 1 choice then just quit
        if len(action_space.get_actions()) == 1:
            return action_space.get_actions()[0]

        examples: list[UserAssistantExample] = []

        actions1: list[Action] = [
            GET_RANDOM_NUMBER,
            SOLVE_MATH,
            WebSearch(),
            SummariseURL(),
        ]

        res1 = ActionResult()
        res1.set_param("prompt", "What is the weather like today?")
        context1 = ActionContext.from_action_result(res1, context)

        actions2: list[Action] = [GET_CURRENT_DATE, GET_CURRENT_TIME, WebSearch(), SummariseURL()]

        res2 = ActionResult()
        res2.set_param("prompt", "What is the current date?")
        context2 = ActionContext.from_action_result(res2, context)

        examples.append(self.craft_example(actions1, context1, 2))
        examples.append(self.craft_example(actions2, context2, 0))

        response = await call_llm_with_examples(
            examples,
            UserMessage(
                self.get_select_action_prompt(action_space.get_actions(), context),
                sender=User("Test User", "A test user"),
            ),
        )

        # TODO: use the params  # noqa: TD003
        name, params = self.parse_response(response)

        logging.getLogger("textual_app").info("LLM selected action: %s with params: %s", name, params.to_dict())
        logging.getLogger("textual_app").info("Context: %s", context.last_result.as_json_pretty())
        logging.getLogger("textual_app").debug(
            "Prompt: %s",
            self.get_select_action_prompt(action_space.get_actions(), context),
        )
        logging.getLogger("textual_app").debug("LLM response: %s", response)

        # find action
        for action in action_space.get_actions():
            if action.name == name:
                return action

        msg = f"Action '{name}' not found in the action space."
        raise ValueError(msg)

    def get_select_action_prompt(self, actions: list[Action], context: ActionContext) -> str:
        """Generate a prompt for selecting an action from a list of actions."""
        actions_str = json.dumps([action.as_json() for action in actions], indent=4)

        logging.getLogger("textual_app").debug("Actions: %s", actions_str)

        prompt = ""

        prompt += f"""
        Follow this plan {context.plan}
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

        For example, if you choose the 'WebSearch' action, your response should look like this:
        ```json
        {
            "name": "WebSearch",
            "params": {
                "query": "What is the weather like today?"
            }
        }
        ```
        """
        APP_LOGGER.debug(prompt)
        return prompt.strip()

    def craft_example(self, actions: list[Action], context: ActionContext, chosen_index: int) -> UserAssistantExample:
        """Craft an example from a list of actions."""
        prompt = self.get_select_action_prompt(actions, context)

        user_message = UserMessage(prompt, sender=User("Example User", "An example user"))

        assistant_message = AssistantMessage(
            json.dumps(actions[chosen_index].as_json(), indent=4),
            sender=context.agent,
        )  # type: ignore

        return UserAssistantExample(user_message, assistant_message)

    def parse_response(self, response: str) -> tuple[str, ActionParams]:
        """Parse the LLM response to extract the selected action."""
        choice_str = extract_json_from_response(response)

        logging.getLogger("textual_app").debug(f"LLM response raw: {response}")
        logging.getLogger("textual_app").debug(f"LLM response: {choice_str}")

        choice = json.loads(choice_str)

        params = ActionParams()
        for key, value in choice.get("params", {}).items():
            params.set_param(key, value)

        name = choice.get("name")
        if not name:
            msg = "No action name provided in the choice."
            raise ValueError(msg)

        return name, params
