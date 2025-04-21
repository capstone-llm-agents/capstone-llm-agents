"""Module for ConfigManager class"""

import json

from autogen import LLMConfig

from config.config_models import AppConfig, ModelsConfig


class ConfigManager:
    """Class to manage configuration settings for the application."""

    def __init__(self, config_file_path: str):
        """
        Initialise the ConfigManager with a configuration file.

        Args:
            config_file (str): Path to the configuration file.
        """
        self.config_file = config_file_path

        app_config, models_config = self.load_config()

        self.app_config = app_config
        self.models_config = models_config

    def load_config(self) -> tuple[AppConfig, ModelsConfig]:
        """
        Load the configuration from the file.

        Raises:
            FileNotFoundError: If the configuration file does not exist.
            ValueError: If the configuration file is empty or invalid.
        """
        # load pydantic model from file
        # validate the model

        with open(self.config_file, "r", encoding="utf") as file:
            config_data = json.load(file)
            if not config_data:
                raise ValueError("Configuration file is empty.")

        # validate the model
        app_config_model = AppConfig(**config_data)

        models_path = app_config_model.models

        with open(models_path, "r", encoding="utf") as file:
            models_data = json.load(file)
            if not models_data:
                raise ValueError("Models configuration file is empty.")

        models_config_model = ModelsConfig(**models_data)

        # TODO handle .env config (not used ATM)

        return app_config_model, models_config_model

    def get_llm_config(
        self, use_tools: bool = False, model_index: int | None = None
    ) -> LLMConfig:
        # TODO refactor this out to be specific to AG2
        """
        Get the LLM configuration.

        Args:
            include_tools (bool): Whether to include tools in the configuration. Defaults to False.
            model_index (int | None): The index of the model to use. If None, uses the default model.

        Returns:
            dict: The LLM configuration.
        """
        if model_index is None:
            model_index = self.models_config.default_model

        if use_tools and self.models_config.default_model_with_tools is not None:
            model_index = self.models_config.default_model_with_tools

        if model_index >= len(self.models_config.models):
            raise ValueError(
                f"Model index {model_index} is out of range. "
                f"Max index is {len(self.models_config.models) - 1}."
            )

        model_config = self.models_config.models[model_index]
        return LLMConfig(
            api_type=model_config.api_type,
            model=model_config.model,
        )
