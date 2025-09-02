"""Ollama call LLM model."""

import asyncio

import ollama
from llm_mas.mas.conversation import UserAssistantExample, UserMessage


async def call_llm(prompt: str) -> str:
    """Async wrapper: Call the Ollama LLM with the given model and prompt."""
    model = "gemma3"
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


async def call_llm_with_messages(messages: list[dict]) -> str:
    """Async wrapper: Call the Ollama LLM with a list of messages."""
    model = "gemma3"
    response = await asyncio.to_thread(
        ollama.chat,
        model=model,
        messages=messages,
    )
    content = response.message.content
    if not content:
        msg = "No content returned from Ollama LLM."
        raise ValueError(msg)
    return content


async def call_llm_with_examples(
    examples: list[UserAssistantExample],
    user_message: UserMessage,
) -> str:
    """Async wrapper: Call the Ollama LLM with examples and a user message."""
    model = "gemma3"
    messages = [example.user_message.as_dict() for example in examples]
    messages.append(user_message.as_dict())

    response = await asyncio.to_thread(
        ollama.chat,
        model=model,
        messages=messages,
    )
    content = response.message.content
    if not content:
        msg = "No content returned from Ollama LLM with examples."
        raise ValueError(msg)
    return content


# embedding model
async def get_embedding(text: str) -> list[float]:
    """Get the embedding for the given text using Ollama."""
    model = "mxbai-embed-large"
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
