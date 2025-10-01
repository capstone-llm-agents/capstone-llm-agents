"""General configuration manager combining models and vector configs."""

from typing import TYPE_CHECKING

from llm_mas.utils.config.models_config import ModelsConfigManager
from llm_mas.utils.config.vector_config import VectorConfigManager

if TYPE_CHECKING:
    from llm_mas.utils.config.base_config import BaseConfigManager


class GeneralConfig:
    """Unified configuration manager for models and vector database."""

    def __init__(self, models_path: str, vector_path: str) -> None:
        """Initialize the general configuration manager."""
        self.models = ModelsConfigManager(models_path)
        self.vector = VectorConfigManager(vector_path)

        self.configs: list[BaseConfigManager] = []

        # add the configs
        self.add_config(self.models)
        self.add_config(self.vector)

    def add_config(self, config: "BaseConfigManager") -> None:
        """Add an additional configuration manager."""
        self.configs.append(config)
