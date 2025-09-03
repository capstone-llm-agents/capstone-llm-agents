"""Manages the config for models, vector database provider etc."""

from pathlib import Path

import pydantic
import yaml
from pydantic import BaseModel


class ModelConfig(BaseModel):
    """Model configuration settings."""

    provider: str
    model: str


class Config(BaseModel):
    """Configuration class to manage settings for models and vector database providers."""

    version: str
    models: list[ModelConfig]
    embedding_models: list[ModelConfig]
    default_model: int
    default_local_model: int
    default_model_with_native_tools: int
    default_quick_model: int
    default_powerful_model: int
    default_embedding_model: int


class ConfigManager:
    """Configuration class to manage settings for models and vector database providers."""

    def __init__(self, file_path: str) -> None:
        """Initialize the Config class with a file name."""
        self.file_path = file_path

        # model
        self.config = self.load_config()

    def load_config(self) -> Config:
        """Load configuration from a YAML file."""
        try:
            with Path(self.file_path).open("r") as file:
                config_data = yaml.safe_load(file)

                if not config_data:
                    msg = f"Configuration file '{self.file_path}' is empty or invalid."
                    raise ValueError(msg)

                return Config(**config_data)

        except FileNotFoundError as e:
            msg = f"Configuration file '{self.file_path}' not found."
            raise FileNotFoundError(msg) from e
        except yaml.YAMLError as e:
            msg = f"Error parsing YAML file. {e}"
            raise ValueError(msg) from e
        except TypeError as e:
            msg = f"Error in configuration data. {e}"
            raise ValueError(msg) from e
        except pydantic.ValidationError as e:
            msg = f"The structure of the configuration file is not correct. {e}"
            raise ValueError(msg) from e

    def save_config(self, config: Config) -> None:
        """Save configuration to a YAML file."""
        try:
            with Path(self.file_path).open("w") as file:
                yaml.safe_dump(config.model_dump_json(), file)
        except Exception as e:
            msg = f"Error saving configuration to file: {e}"
            raise OSError(msg) from e

    # config getters
    def get_models(self) -> list[ModelConfig]:
        """Get the list of model configurations."""
        return self.config.models

    def get_embedding_models(self) -> list[ModelConfig]:
        """Get the list of embedding model configurations."""
        return self.config.embedding_models

    def get_default_model(self) -> ModelConfig:
        """Get the default model configuration."""
        return self.config.models[self.config.default_model]

    def get_default_model_with_native_tools(self) -> ModelConfig:
        """Get the default model configuration for models with native tools."""
        return self.config.models[self.config.default_model_with_native_tools]

    def get_default_quick_model(self) -> ModelConfig:
        """Get the default quick model configuration."""
        return self.config.models[self.config.default_quick_model]

    def get_default_powerful_model(self) -> ModelConfig:
        """Get the default powerful model configuration."""
        return self.config.models[self.config.default_powerful_model]

    def get_default_embedding_model(self) -> ModelConfig:
        """Get the default embedding model configuration."""
        return self.config.embedding_models[self.config.default_embedding_model]

    def get_default_local_model(self) -> ModelConfig:
        """Get the default local model configuration."""
        return self.config.models[self.config.default_local_model]

    def get_model(self, model_name: str) -> ModelConfig:
        """Get a model configuration by its name."""
        for model in self.config.models:
            if model.model == model_name:
                return model
        msg = f"Model '{model_name}' not found in configuration."
        raise ValueError(msg)

    def get_embedding_model(self, model_name: str) -> ModelConfig:
        """Get an embedding model configuration by its name."""
        for model in self.config.embedding_models:
            if model.model == model_name:
                return model
        msg = f"Embedding model '{model_name}' not found in configuration."
        raise ValueError(msg)
