"""The random selector module provides a base class for random selection of actions in the action system."""

import logging
from collections.abc import Awaitable, Callable
from typing import override

import numpy as np

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_selector import ActionSelector
from llm_mas.action_system.core.action_space import ActionSpace


class EmbeddingSelector(ActionSelector):
    """A selection policy that randomly selects an action from the narrowed action space."""

    def __init__(self, embedding_model: Callable[[str], Awaitable[list[float]]]) -> None:
        """Initialize the EmbeddingSelector with a callable for embedding model calls."""
        self.embedding_model = embedding_model

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

        # get last message
        history = context.conversation

        messages = history.chat_history.messages

        if not messages:
            msg = "No messages in the conversation history."
            raise ValueError(msg)

        last_message = messages[-1]

        user_input = last_message.content

        # get embedding for the user input
        user_input_embedding = await self.embedding_model(user_input)

        # action embeddings
        action_embeddings: list[tuple[Action, list[float]]] = []

        for action in action_space.get_actions():
            embedding = await self.embedding_model(action.description)
            action_embeddings.append((action, embedding))

        # pick the action with the closest embedding
        action, _ = self.find_closest_embedding(user_input_embedding, action_embeddings)

        return action

    def find_closest_embedding(
        self,
        user_embedding: list[float],
        action_embeddings: list[tuple[Action, list[float]]],
    ) -> tuple[Action, float]:
        """Find the action with the closest embedding to the user input embedding."""
        best_action: Action | None = None
        best_similarity = -1.0

        user_vec = np.array(user_embedding)

        for action, embedding in action_embeddings:
            action_vec = np.array(embedding)
            similarity = np.dot(user_vec, action_vec) / (np.linalg.norm(user_vec) * np.linalg.norm(action_vec))
            if similarity > best_similarity:
                best_similarity = similarity
                best_action = action

        if best_action is None:
            msg = "No action found with closest embedding."
            raise ValueError(msg)

        # log all the scores
        logging.getLogger("textual_app").info("Embedding similarities:")
        for action, embedding in action_embeddings:
            action_vec = np.array(embedding)
            similarity = np.dot(user_vec, action_vec) / (np.linalg.norm(user_vec) * np.linalg.norm(action_vec))
            logging.getLogger("textual_app").info("Action: %s, Similarity: %.4f", action.name, similarity)

        return best_action, best_similarity
