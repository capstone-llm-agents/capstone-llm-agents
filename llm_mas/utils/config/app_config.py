"""Application configuration manager using pydantic and YAML."""

from enum import Enum

from llm_mas.utils.config.base_config import BaseConfigManager, ConfigBaseModel


class AppMode(Enum):
    """Enumeration of application modes."""

    DEV = "dev"
    PROD = "prod"
    TEST = "test"


class AppConfig(ConfigBaseModel):
    """Application configuration settings."""

    mode: AppMode
    use_memory: bool


class AppConfigManager(BaseConfigManager[AppConfig]):
    """Manager for vector database configuration."""

    def __init__(self, file_path: str) -> None:
        """Initialize the application configuration manager."""
        super().__init__(file_path, AppConfig)

    def get_mode(self) -> AppMode:
        """Return the application mode."""
        return self.config.mode

    def memory_enabled(self) -> bool:
        """Return whether agent memory is enabled."""
        return self.config.use_memory
