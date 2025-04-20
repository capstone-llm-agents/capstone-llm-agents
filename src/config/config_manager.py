"""Module for ConfigManager class"""

import json

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
