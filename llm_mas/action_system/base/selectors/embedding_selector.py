"""The embedding selector module provides a class for selecting actions based on semantic similarity of embeddings."""

from collections.abc import Awaitable, Callable
from typing import override

import numpy as np

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_selector import ActionSelector
from llm_mas.action_system.core.action_space import ActionSpace
from llm_mas.utils.embeddings import VectorSelector


class EmbeddingSelector(ActionSelector):
    """Selects an action using embeddings and configurable selection strategies."""

    def __init__(
        self,
        embedding_model: Callable[[str], Awaitable[list[float]]],
        vector_selector: VectorSelector | None = None,
    ) -> None:
        """Initialize the EmbeddingSelector."""
        self.embedding_model = embedding_model
        self.vector_selector = vector_selector or VectorSelector()

    @override
    async def select_action(self, action_space: ActionSpace, context: ActionContext) -> Action:
        actions = action_space.get_actions()
        if not actions:
            msg = "Action space is empty. Cannot select an action."
            raise ValueError(msg)

        if len(actions) == 1:
            return actions[0]

        messages = context.conversation.chat_history.messages
        if not messages:
            msg = "No messages in chat history. Cannot select an action."
            raise ValueError(msg)
        user_input = messages[-1].content

        user_embedding = np.array(await self.embedding_model(user_input))
        action_embeddings: list[tuple[Action, np.ndarray]] = [
            (action, np.array(await self.embedding_model(action.description))) for action in actions
        ]

        action, _ = self.vector_selector.select(user_embedding, action_embeddings)
        return action
