import os
import asyncio
from openai import OpenAI
from llm_mas.mas.conversation import UserAssistantExample, UserMessage

async def call_llm(prompt: str) -> str:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    model = "gpt-4o-mini"
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    content =  response.choices[0].message.content
    if not content:
        msg = f"No content returned from {model}."
        raise ValueError(msg)
    return content


async def call_llm_with_messages(messages: list[dict]) -> str:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    model = "gpt-4o-mini"
    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    content = response.choices[0].message.content
    if not content:
        msg = f"No content returned from {model}."
        raise ValueError(msg)
    return content


async def call_llm_with_examples(
    examples: list[UserAssistantExample],
    user_message: UserMessage,
) -> str:
    messages = [example.user_message.as_dict() for example in examples]
    messages.append(user_message.as_dict())
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    model = "gpt-4o-mini"
    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    content = response.choices[0].message.content
    if not content:
        msg = f"No content returned from {model} with examples."
        raise ValueError(msg)
    return content

async def get_embedding(text: str) -> list[float]:
    """Get the embedding for the given text using OpenAI."""
    model = "text-embedding-3-small"
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    response = client.embeddings.create(
        model=model,
        input=text,
    )

    # as vector
    embeddings = response.data[0].embedding
    if not embeddings or len(embeddings) == 0:
        msg = "No embeddings returned from OpenAI."
        raise ValueError(msg)

    return list(embeddings)
