"""Gemini call LLM model."""

import os

from google import genai

from llm_mas.model_providers.provider import ModelProvider


class GeminiProvider(ModelProvider):
    """Gemini model provider."""

    def __init__(self) -> None:
        """Initialize the ModelsAPI."""
        super().__init__("google")

    @staticmethod
    def _init_provided_models() -> list[str]:
        """Initialize the list of provided models."""
        return ["gemini-2.5-flash", "gemini-2.5-pro"]

    @staticmethod
    def _init_suggested_models() -> list[str]:
        """Initialize the list of suggested models."""
        return ["gemini-2.5-flash"]

    @staticmethod
    def _init_client() -> genai.Client:
        """Initialize the Gemini client."""
        api_key = os.environ.get("GEMINI_KEY")
        if not api_key:
            msg = "GEMINI_KEY environment variable not set."
            raise ValueError(msg)
        return genai.Client(api_key=api_key)

    @staticmethod
    async def call_llm(prompt: str, model: str) -> str:
        """Call the LLM with the given prompt."""
        client = GeminiProvider._init_client()

        response = await client.aio.models.generate_content(model=model, contents=prompt)

        if not response.text:
            msg = f"No content returned from {model}."
            raise ValueError(msg)

        return response.text

    @staticmethod
    def _convert_openai_messages_to_gemini(messages: list[dict]) -> list[dict]:
        """Convert OpenAI message format to Gemini format."""
        # google has structure of role": "model/user", and then parts: [{"text": "content"s}]
        # whereas openai is "role": "user/assistant", "content": "content"
        gemini_messages: list[dict] = []
        for message in messages:
            role = message["role"]
            if role == "user":
                gemini_role = "user"
            elif role == "assistant":
                gemini_role = "model"
            else:
                msg = f"Unknown role: {role}"
                raise ValueError(msg)
            gemini_messages.append(
                {
                    "role": gemini_role,
                    "parts": [{"text": message["content"]}],
                },
            )
        return gemini_messages

    @staticmethod
    async def call_llm_with_messages(messages: list[dict], model: str) -> str:
        """Call the LLM with the given chat history."""
        client = GeminiProvider._init_client()

        response = await client.aio.models.generate_content(model=model, contents=messages)

        if not response.text:
            msg = f"No content returned from {model}."
            raise ValueError(msg)

        return response.text

    @staticmethod
    async def get_embedding(text: str, model: str) -> list[float]:
        """Get the embedding for the given text using Gemini."""
        msg = "Gemini embeddings have not been implemented yet."
        raise NotImplementedError(msg)
