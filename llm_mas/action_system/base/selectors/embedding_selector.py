"""The embedding selector module provides a class for selecting actions based on semantic similarity of embeddings."""

import logging
from collections.abc import Awaitable, Callable
from enum import Enum, auto
from typing import override

import numpy as np

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_selector import ActionSelector
from llm_mas.action_system.core.action_space import ActionSpace


class EmbeddingSelectorSelectionStrategy(Enum):
    """Selection strategies for the EmbeddingSelector."""

    ARGMAX = auto()
    """Select the action with the highest score."""
    RANDOM = auto()
    """Select an action randomly from the filtered actions (top-k or top-p)."""


class EmbeddingSelector(ActionSelector):
    """Selects an action using embeddings and configurable selection strategies."""

    def __init__(
        self,
        embedding_model: Callable[[str], Awaitable[list[float]]],
        *,
        top_k: int | None = None,
        top_p: float | None = None,
        selection_strategy: EmbeddingSelectorSelectionStrategy = EmbeddingSelectorSelectionStrategy.ARGMAX,
    ) -> None:
        """Initialize the EmbeddingSelector."""
        self.embedding_model = embedding_model
        self.top_k = top_k
        self.top_p = top_p
        self.selection_strategy = selection_strategy

        if self.top_k is not None and self.top_p is not None:
            logging.getLogger("textual_app").warning(
                "Both top_k and top_p are set. This can lead to unexpected behavior.",
            )

    @override
    async def select_action(self, action_space: ActionSpace, context: ActionContext) -> Action:
        """Select an action from the action space using embedding similarity."""
        actions = action_space.get_actions()
        if not actions:
            msg = "Action space is empty. Cannot select an action."
            raise ValueError(msg)

        if len(actions) == 1:
            return actions[0]

        # Get user input (last message)
        messages = context.conversation.chat_history.messages
        if not messages:
            msg = "Conversation has no messages. Cannot select an action."
            raise ValueError(msg)
        user_input = messages[-1].content

        # Compute embeddings
        user_embedding = np.array(await self.embedding_model(user_input))
        action_embeddings: list[tuple[Action, np.ndarray]] = [
            (action, np.array(await self.embedding_model(action.description))) for action in actions
        ]

        # Select action based on configured strategy
        action, _ = self._select_by_similarity(user_embedding, action_embeddings)
        return action

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity between two vectors."""
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    def _select_by_similarity(
        self,
        user_vector: np.ndarray,
        action_embeddings: list[tuple[Action, np.ndarray]],
    ) -> tuple[Action, float]:
        """Select an action given user embedding and action embeddings."""
        similarities = [
            (action, self._cosine_similarity(user_vector, embedding)) for action, embedding in action_embeddings
        ]

        logger = logging.getLogger("textual_app")
        logger.info("Embedding similarities:")
        for action, similarity in similarities:
            logger.info("Action: %s, Similarity: %.4f", action.name, similarity)

        similarities.sort(key=lambda x: x[1], reverse=True)

        if self.top_k is not None and self.top_k < len(similarities):
            similarities = similarities[: self.top_k]

        if self.top_p is not None and 0.0 < self.top_p < 1.0:
            total_score = sum(similarity for _, similarity in similarities)
            cumulative, filtered = 0.0, []
            for action, similarity in similarities:
                cumulative += similarity / total_score if total_score > 0 else 0
                filtered.append((action, similarity))
                if cumulative >= self.top_p:
                    break
            similarities = filtered

        if self.selection_strategy == EmbeddingSelectorSelectionStrategy.ARGMAX:
            return similarities[0]
        if self.selection_strategy == EmbeddingSelectorSelectionStrategy.RANDOM:
            return similarities[np.random.randint(len(similarities))]  # noqa: NPY002

        msg = f"Unknown selection strategy: {self.selection_strategy}"
        raise ValueError(msg)
