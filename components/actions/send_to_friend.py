"""The agent sends a message to an assistant of the user's friend."""

import logging
from typing import override

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.fragment.fragment import Fragment
from llm_mas.fragment.kinds.base import TextFragmentKind
from llm_mas.fragment.raws.base import TextRaw
from llm_mas.fragment.source import FragmentSource
from llm_mas.model_providers.api import ModelsAPI
from llm_mas.utils.config.models_config import ModelType


class SendToFriend(Action):
    """The action that sends a message to an assistant of the user's friend."""

    def __init__(self) -> None:
        """Initialize the SendToFriend action."""
        super().__init__(
            description="Sends a message to an assistant of the user's friend.",
        )

    @override
    async def do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action by generating a response from an LLM."""
        # steps:
        # 1. grab user friends
        # 2. grab the last message
        # 3. choose the correct friend (based on embedding)
        # 4. send the message to the friend's assistant
        # 5. get the response and return it
