"""Ollama call LLM model."""

import ollama


def call_llm(prompt: str) -> str:
    """Call the Ollama LLM with the given model and prompt."""
    model = "gemma3"
    response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    content = response.message.content

    if not content:
        msg = "No content returned from Ollama LLM."
        raise ValueError(msg)
    return content
