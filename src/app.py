"""Module for the main application logic"""

from config.config_manager import ConfigManager


class App:
    """Main application class."""

    def __init__(self):
        """
        Initialise the application.
        """
        self.config_manager = ConfigManager("./config/app.json")

    def run(self):
        """
        Run the application.
        """
        print("Running application...")
