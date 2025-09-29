"""Models configuration manager using pydantic and YAML."""

from enum import Enum, auto

from pydantic import BaseModel

from llm_mas.utils.config.base_config import BaseConfigManager, ConfigBaseModel


class ModelConfig(BaseModel):
    """Model configuration settings."""

    provider: str
    model: str


class ModelsConfig(ConfigBaseModel):
    """Configuration schema for models."""

    version: str
    models: list[ModelConfig]
    embedding_models: list[ModelConfig]
    default_model: int
    default_local_model: int
    default_model_with_native_tools: int
    default_quick_model: int
    default_powerful_model: int
    default_embedding_model: int


class ModelType(Enum):
    """Enumeration of model types."""

    DEFAULT = auto()
    QUICK = auto()
    POWERFUL = auto()
    LOCAL = auto()
    EMBEDDING = auto()
    NATIVE_TOOLS = auto()


class ModelsConfigManager(BaseConfigManager[ModelsConfig]):
    """Manager for models configuration."""

    def __init__(self, file_path: str) -> None:
        """Initialize the models configuration manager."""
        super().__init__(file_path, ModelsConfig)

    def get_models(self) -> list[ModelConfig]:
        """Return all model configurations."""
        return self.config.models

    def get_embedding_models(self) -> list[ModelConfig]:
        """Return all embedding model configurations."""
        return self.config.embedding_models

    def get_default_model(self) -> ModelConfig:
        """Return the default model configuration."""
        return self.config.models[self.config.default_model]

    def get_default_model_with_native_tools(self) -> ModelConfig:
        """Return the default model with native tools."""
        return self.config.models[self.config.default_model_with_native_tools]

    def get_default_quick_model(self) -> ModelConfig:
        """Return the default quick model configuration."""
        return self.config.models[self.config.default_quick_model]

    def get_default_powerful_model(self) -> ModelConfig:
        """Return the default powerful model configuration."""
        return self.config.models[self.config.default_powerful_model]

    def get_default_embedding_model(self) -> ModelConfig:
        """Return the default embedding model configuration."""
        return self.config.embedding_models[self.config.default_embedding_model]

    def get_default_local_model(self) -> ModelConfig:
        """Return the default local model configuration."""
        return self.config.models[self.config.default_local_model]

    def get_model(self, model_name: str) -> ModelConfig:
        """Return a model configuration by name."""
        for model in self.config.models:
            if model.model == model_name:
                return model
        msg = f"Model '{model_name}' not found."
        raise ValueError(msg)

    def get_embedding_model(self, model_name: str) -> ModelConfig:
        """Return an embedding model configuration by name."""
        for model in self.config.embedding_models:
            if model.model == model_name:
                return model
        msg = f"Embedding model '{model_name}' not found."
        raise ValueError(msg)

    def get_model_by_type(self, model_type: ModelType = ModelType.DEFAULT) -> ModelConfig:
        """Return a model configuration based on the specified type."""
        if model_type == ModelType.DEFAULT:
            return self.get_default_model()
        if model_type == ModelType.QUICK:
            return self.get_default_quick_model()
        if model_type == ModelType.POWERFUL:
            return self.get_default_powerful_model()
        if model_type == ModelType.LOCAL:
            return self.get_default_local_model()
        if model_type == ModelType.EMBEDDING:
            return self.get_default_embedding_model()
        if model_type == ModelType.NATIVE_TOOLS:
            return self.get_default_model_with_native_tools()
        msg = f"Model type '{model_type}' is not recognized."
        raise ValueError(msg)
