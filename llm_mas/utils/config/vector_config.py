"""Vector database configuration manager using pydantic and YAML."""

from llm_mas.utils.config.base_config import BaseConfigManager, ConfigBaseModel


class VectorDBConfig(ConfigBaseModel):
    """Vector database configuration settings."""

    provider: str
    config: dict


class VectorConfigManager(BaseConfigManager[VectorDBConfig]):
    """Manager for vector database configuration."""

    def __init__(self, file_path: str) -> None:
        """Initialize the vector database configuration manager."""
        super().__init__(file_path, VectorDBConfig)

    def get_provider(self) -> str:
        """Return the vector database provider name."""
        return self.config.provider

    def get_config(self) -> dict:
        """Return the provider-specific configuration dictionary."""
        return self.config.config
