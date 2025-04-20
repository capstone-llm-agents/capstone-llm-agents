"""Module for ConfigManager class"""


class ConfigManager:
    """Class to manage configuration settings for the application."""

    def __init__(self, config_file_path: str):
        """
        Initialise the ConfigManager with a configuration file.

        Args:
            config_file (str): Path to the configuration file.
        """
        self.config_file = config_file_path
        self.config = {}
