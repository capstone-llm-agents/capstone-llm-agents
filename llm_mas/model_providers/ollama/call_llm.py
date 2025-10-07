"""Ollama call LLM model."""

import asyncio

import ollama

from llm_mas.logging.loggers import APP_LOGGER
from llm_mas.model_providers.provider import ModelProvider


class OllamaProvider(ModelProvider):
    """Ollama model provider."""

    def __init__(self) -> None:
        """Initialize the ModelsAPI."""
        super().__init__("ollama")

    @staticmethod
    def _init_provided_models() -> list[str]:
        """Initialize the list of provided models."""
        return ["gemma3", "gemma3:1b"]

    @staticmethod
    def _init_suggested_models() -> list[str]:
        """Initialize the list of suggested models."""
        return ["gemma3"]

    @staticmethod
    async def call_llm(prompt: str, model: str) -> str:
        """Call the LLM with the given prompt."""
        response = await asyncio.to_thread(
            ollama.chat,
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        content = response.message.content
        if not content:
            msg = "No content returned from Ollama LLM."
            raise ValueError(msg)
        return content

    @staticmethod
    async def call_llm_with_chat_history(chat_history: list[dict], model: str) -> str:
        """Call the LLM with the given chat history."""
        response = await asyncio.to_thread(
            ollama.chat,
            model=model,
            messages=chat_history,
        )
        content = response.message.content
        if not content:
            msg = "No content returned from Ollama LLM."
            raise ValueError(msg)
        return content

    @staticmethod
    async def get_embedding(text: str, model: str) -> list[float]:
        """Get the embedding for the given text using Ollama."""
        APP_LOGGER.info("Getting embedding for text using Ollama model: %s", model)
        response = await asyncio.to_thread(
            ollama.embed,
            model=model,
            input=text,
        )

        # as vector
        embeddings = response.embeddings
        if not embeddings or len(embeddings) == 0:
            msg = "No embeddings returned from Ollama."
            raise ValueError(msg)

        return list(embeddings[0])
