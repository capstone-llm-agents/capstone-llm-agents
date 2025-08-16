"""Ollama call LLM model."""

import ollama
from llm_mas.mas.conversation import UserAssistantExample, UserMessage


def call_llm(prompt: str) -> str:
    """Call the Ollama LLM with the given model and prompt."""
    model = "gemma3"
    response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    content = response.message.content

    if not content:
        msg = "No content returned from Ollama LLM."
        raise ValueError(msg)
    return content


def call_llm_with_messages(messages: list[dict]) -> str:
    """Call the Ollama LLM with a list of messages."""
    model = "gemma3"
    response = ollama.chat(model=model, messages=messages)
    content = response.message.content

    if not content:
        msg = "No content returned from Ollama LLM."
        raise ValueError(msg)
    return content


def call_llm_with_examples(examples: list[UserAssistantExample], user_message: UserMessage) -> str:
    """Call the Ollama LLM with examples and a user message."""
    model = "gemma3"
    messages = [example.user_message.as_dict() for example in examples]
    messages.append(user_message.as_dict())

    response = ollama.chat(model=model, messages=messages)
    content = response.message.content

    if not content:
        msg = "No content returned from Ollama LLM."
        raise ValueError(msg)
    return content
