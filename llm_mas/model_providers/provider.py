"""The model provider base class."""

from abc import abstractmethod


class ModelProvider:
    """Base class for model providers."""

    def __init__(self, name: str) -> None:
        """Initialize the ModelProvider with a name."""
        self.name = name
        self.provided_models = self._init_provided_models()
        self.suggested_models = self._init_suggested_models()

    def get_name(self) -> str:
        """Get the name of the model provider."""
        return self.name

    def get_provided_models(self) -> list[str]:
        """Get the list of models provided by this provider."""
        return self.provided_models

    def get_suggested_models(self) -> list[str]:
        """Get the list of models suggested by this provider."""
        return self.suggested_models

    @staticmethod
    @abstractmethod
    async def call_llm(prompt: str, model: str) -> str:
        """Call the LLM with the given prompt. To be implemented by subclasses."""
        msg = "call_llm method not implemented."
        raise NotImplementedError(msg)

    @staticmethod
    @abstractmethod
    async def call_llm_with_chat_history(chat_history: list[dict], model: str) -> str:
        """Call the LLM with the given chat history. To be implemented by subclasses."""
        msg = "call_llm_with_chat_history method not implemented."
        raise NotImplementedError(msg)

    @staticmethod
    @abstractmethod
    async def get_embedding(text: str, model: str) -> list[float]:
        """Get the embedding for the given text. To be implemented by subclasses."""
        msg = "get_embedding method not implemented."
        raise NotImplementedError(msg)

    @staticmethod
    @abstractmethod
    def _init_provided_models() -> list[str]:
        """Initialize the list of provided models. To be implemented by subclasses."""
        msg = "init_provided_models method not implemented."
        raise NotImplementedError(msg)

    @staticmethod
    @abstractmethod
    def _init_suggested_models() -> list[str]:
        """Initialize the list of suggested models. To be implemented by subclasses."""
        msg = "init_suggested_models method not implemented."
        raise NotImplementedError(msg)

    # TODO: Add streaming support  # noqa: TD003
