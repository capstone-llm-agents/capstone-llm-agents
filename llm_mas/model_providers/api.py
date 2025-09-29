"""Models API layer."""

from llm_mas.model_providers.ollama.call_llm import OllamaProvider
from llm_mas.model_providers.provider import ModelProvider
from llm_mas.utils.config.general_config import GeneralConfig
from llm_mas.utils.config.models_config import ModelConfig, ModelType


class ModelsAPI:
    """Models API layer."""

    @staticmethod
    def _get_model_config(
        config: GeneralConfig,
        model_type: ModelType | str = ModelType.DEFAULT,
    ) -> ModelConfig:
        """Get the model configuration based on the model type or name."""
        return (
            config.models.get_model_by_type(model_type)
            if isinstance(model_type, ModelType)
            else config.models.get_model(model_type)
        )

    @staticmethod
    def _get_config_and_providers() -> tuple[GeneralConfig, dict[str, ModelProvider]]:
        """Get the general configuration and model providers."""
        config = GeneralConfig("config/models.yaml", "config/vector.yaml")
        providers: dict[str, ModelProvider] = {
            "ollama": OllamaProvider(),
        }
        return config, providers

    @staticmethod
    async def call_llm(
        prompt: str,
        model: ModelType | str = ModelType.DEFAULT,
    ) -> str:
        """Call the LLM with the given prompt and model type."""
        config, providers = ModelsAPI._get_config_and_providers()
        model_config = ModelsAPI._get_model_config(config, model)
        provider_name = model_config.provider
        if provider_name not in providers:
            msg = f"Model provider '{provider_name}' not found."
            raise ValueError(msg)
        provider = providers[provider_name]
        return await provider.call_llm(prompt, model_config.model)

    @staticmethod
    async def call_llm_with_chat_history(
        chat_history: list[dict],
        model: ModelType | str = ModelType.DEFAULT,
    ) -> str:
        """Call the LLM with the given chat history and model type."""
        config, providers = ModelsAPI._get_config_and_providers()
        model_config = ModelsAPI._get_model_config(config, model)
        provider_name = model_config.provider
        if provider_name not in providers:
            msg = f"Model provider '{provider_name}' not found."
            raise ValueError(msg)
        provider = providers[provider_name]
        return await provider.call_llm_with_chat_history(chat_history, model_config.model)

    @staticmethod
    async def get_embedding(text: str, model: ModelType | str = ModelType.EMBEDDING) -> list[float]:
        """Get the embedding for the given text and model type."""
        config, providers = ModelsAPI._get_config_and_providers()
        model_config = ModelsAPI._get_model_config(config, model)
        provider_name = model_config.provider
        if provider_name not in providers:
            msg = f"Model provider '{provider_name}' not found."
            raise ValueError(msg)
        provider = providers[provider_name]
        return await provider.get_embedding(text, model_config.model)
