"""The random selector module provides a base class for random selection of actions in the action system."""

import json
import re
from collections.abc import Callable

from components.actions.retrieve_knowledge import RetrieveKnowledge
from components.actions.say_hello import SayHello
from components.actions.simple_response import SimpleResponse
from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_selector import ActionSelector
from llm_mas.action_system.core.action_space import ActionSpace
from llm_mas.model_providers.ollama.call_llm import AssistantMessage, Example, UserMessage, call_llm_with_examples


# random selection policy
class LLMSelector(ActionSelector):
    """A selection policy that randomly selects an action from the narrowed action space."""

    def __init__(self, llm_call: Callable[[str], str]) -> None:
        """Initialize the LLMSelector with a callable for LLM calls."""
        self.llm_call = llm_call

    def select_action(self, action_space: ActionSpace) -> Action:
        """Select an action from the action space using an LLM."""

        examples: list[Example] = []

        # example action list
        actions1: list[Action] = [
            SayHello(),
            RetrieveKnowledge(),
            SimpleResponse(),
        ]

        examples.append(self.craft_example(actions1, 0))

        response = call_llm_with_examples(
            examples,
            UserMessage(self.get_select_action_prompt(action_space.get_actions())),
        )

        print(response)

        name, params = self.parse_response(response)

        print(name)

        # find action
        for action in action_space.get_actions():
            if action.name == name:
                return action

        msg = f"Action '{name}' not found in the action space."
        raise ValueError(msg)

    def get_select_action_prompt(self, actions: list[Action]) -> str:
        """Generate a prompt for selecting an action from a list of actions."""
        actions_str = json.dumps([action.as_json() for action in actions], indent=4)

        return f"""
        Choose an action from the following list of actions:
        {actions_str}

        Respond ONLY with the action name and parameters in JSON format, like this:
        ```json
        {{
            "name": "ActionName",
            "params": {{
                "param1": "value1",
                "param2": "value2"
            }}
        }}`
        """

    def craft_example(self, actions: list[Action], chosen_index: int | None) -> Example:
        """Craft an example from a list of actions."""
        prompt = self.get_select_action_prompt(actions)

        user_message = UserMessage(prompt)

        chosen_index = chosen_index if chosen_index is not None else 0

        assistant_message = AssistantMessage(json.dumps(actions[chosen_index].as_json(), indent=4))

        return Example(user_message, assistant_message)

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
