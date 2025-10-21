"""The embedding selector module provides a class for selecting actions based on semantic similarity of embeddings."""

import logging
from typing import override

import numpy as np

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_selector import ActionSelector
from llm_mas.action_system.core.action_space import ActionSpace
from llm_mas.utils.config.models_config import ModelType
from llm_mas.utils.embeddings import EmbeddingFunction, VectorSelector


class EmbeddingSelector(ActionSelector):
    """Selects an action using embeddings and configurable selection strategies."""

    def __init__(
        self,
        embedding_model: EmbeddingFunction,
        vector_selector: VectorSelector | None = None,
    ) -> None:
        """Initialize the EmbeddingSelector."""
        self.embedding_model = embedding_model
        self.vector_selector = vector_selector or VectorSelector()

    @override
    async def select_action(self, action_space: ActionSpace, context: ActionContext) -> Action:
        actions = action_space.get_actions()
        if not actions:
            last_action = context.agent.workspace.action_history.get_last_action()
            last_action_name = last_action[0].name if last_action else "None"
            msg = f"Action space is empty after narrowing from '{last_action_name}'. This indicates a graph configuration issue."
            logging.getLogger("textual_app").error(msg)
            raise ValueError(msg)

        if len(actions) == 1:
            selected = actions[0]
            logging.getLogger("textual_app").debug(
                "Only one action available, selecting: %s",
                selected.name,
            )
            return selected

        messages = context.conversation.chat_history.messages
        if not messages:
            msg = "No messages in chat history. Cannot select an action."
            raise ValueError(msg)
        user_input = messages[-1].content

        prompt = f"{user_input} - {context.last_result.as_json_pretty()}"

        logging.getLogger("textual_app").info("Selecting action using prompt: %s", prompt)

        user_embedding = np.array(await self.embedding_model(prompt, ModelType.EMBEDDING))
        action_embeddings: list[tuple[Action, np.ndarray]] = [
            (action, np.array(await self.embedding_model(f"{action.name} - {action.description}", ModelType.EMBEDDING)))
            for action in actions
        ]

        action, similarity = self.vector_selector.select(user_embedding, action_embeddings)
        
        logging.getLogger("textual_app").debug(
            "Selected action '%s' with similarity %.3f from candidates: %s",
            action.name,
            similarity,
            [a.name for a in actions],
        )
        
        return action
