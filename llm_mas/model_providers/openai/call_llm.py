"""OpenAI call LLM model."""

import os

from openai import AsyncOpenAI

from llm_mas.mas.conversation import UserAssistantExample, UserMessage
from llm_mas.model_providers.provider import ModelProvider


class OpenAIProvider(ModelProvider):
    """OpenAI model provider."""

    def __init__(self) -> None:
        """Initialize the ModelsAPI."""
        super().__init__("openai")

    @staticmethod
    def _init_provided_models() -> list[str]:
        """Initialize the list of provided models."""
        # embedding model: text-embedding-3-small
        return ["gpt-4o-mini"]

    @staticmethod
    def _init_suggested_models() -> list[str]:
        """Initialize the list of suggested models."""
        return ["gpt-4o-mini"]

    @staticmethod
    async def call_llm(prompt: str, model: str) -> str:
        """Call the LLM with the given prompt."""
        client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        content = response.choices[0].message.content
        if not content:
            msg = f"No content returned from {model}."
            raise ValueError(msg)
        return content

    @staticmethod
    async def call_llm_with_messages(messages: list[dict], model: str) -> str:
        """Call the LLM with the given chat history."""
        client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        response = await client.chat.completions.create(
            model=model,
            messages=messages,  # pyright: ignore[reportArgumentType]
        )
        content = response.choices[0].message.content
        if not content:
            msg = f"No content returned from {model}."
            raise ValueError(msg)
        return content

    @staticmethod
    async def call_llm_with_examples(
        examples: list[UserAssistantExample],
        model: str,
        user_message: UserMessage,
    ) -> str:
        """Call the LLM with the given examples and user message."""
        messages = [example.user_message.as_dict() for example in examples]
        messages.append(user_message.as_dict())
        client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        response = await client.chat.completions.create(
            model=model,
            messages=messages,  # pyright: ignore[reportArgumentType]
        )
        content = response.choices[0].message.content
        if not content:
            msg = f"No content returned from {model} with examples."
            raise ValueError(msg)
        return content

    @staticmethod
    async def get_embedding(text: str, model: str) -> list[float]:
        """Get the embedding for the given text using openai."""
        client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        response = await client.embeddings.create(
            model=model,
            input=text,
        )
        # as vector
        embeddings = response.data[0].embedding
        if not embeddings or len(embeddings) == 0:
            msg = "No embeddings returned from OpenAI."
            raise ValueError(msg)

        return list(embeddings)
