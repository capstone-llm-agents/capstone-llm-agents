import os
import asyncio
from google import genai
from llm_mas.mas.conversation import UserAssistantExample, UserMessage

async def call_llm(prompt: str) -> str:
    client = genai.Client()
    model = "gemini-2.5-flash"
    chat = client.chats.create(model=model)
    response = chat.send_message(
      prompt,
    )
    content =  response.text
    if not content:
        msg = f"No content returned from {model}."
        raise ValueError(msg)
    return content


async def call_llm_with_messages(messages: list[dict]) -> str:
    client = genai.Client()
    model = "gemini-2.5-flash"
    response = client.models.generate_content(
        model=model,
        contents=messages,
    )
    content = response.text
    if not content:
        msg = f"No content returned from {model}."
        raise ValueError(msg)
    return content


async def call_llm_with_examples(
    examples: list[UserAssistantExample],
    message: UserMessage,
) -> str:
    messages = [example.user_message.as_dict() for example in examples]
    messages.append(message.as_dict())
    client = genai.Client()
    model = "gemini-2.5-flash"
    response = client.models.generate_content(
        model=model,
        contents=messages,
    )
    content = response.text
    if not content:
        msg = f"No content returned from {model} with examples."
        raise ValueError(msg)
    return content

async def get_embedding(text: str) -> list[float]:
    """Get the embedding for the given text using Google."""
    model = "text-embedding-005"
    client = genai.Client()
    response = client.models.embed_content(
        model=model,
        contents=text,
    )

    # as vector
    embeddings = response['embeddings']
    if not embeddings or len(embeddings) == 0:
        msg = "No embeddings returned from Ollama."
        raise ValueError(msg)

    return list(embeddings[0])
