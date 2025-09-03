"""The model provider base class."""


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
        """Get the set of models provided by this provider."""
        return self.provided_models

    def get_suggested_models(self) -> list[str]:
        """Get the set of models suggested by this provider."""
        return self.suggested_models

    def call_llm(self, prompt: str) -> str:
        """Call the LLM with the given prompt. To be implemented by subclasses."""
        msg = "call_llm method not implemented."
        raise NotImplementedError(msg)

    def call_llm_with_chat_history(self, chat_history: list[dict]) -> str:
        """Call the LLM with the given chat history. To be implemented by subclasses."""
        msg = "call_llm_with_chat_history method not implemented."
        raise NotImplementedError(msg)

    def get_embedding(self, text: str) -> list[float]:
        """Get the embedding for the given text. To be implemented by subclasses."""
        msg = "get_embedding method not implemented."
        raise NotImplementedError(msg)

    def _init_provided_models(self) -> list[str]:
        """Initialize the set of provided models. To be implemented by subclasses."""
        msg = "init_provided_models method not implemented."
        raise NotImplementedError(msg)

    def _init_suggested_models(self) -> list[str]:
        """Initialize the set of suggested models. To be implemented by subclasses."""
        msg = "init_suggested_models method not implemented."
        raise NotImplementedError(msg)

    # TODO: Add streaming support  # noqa: TD003
