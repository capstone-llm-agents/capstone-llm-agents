from core.api import MASAPI
from user_interface.inteface import UserInterface


class App:
    """The main application class."""

    def __init__(self, api: MASAPI, interface: UserInterface):
        self.api = api
        self.interface = interface

    def run(self):
        """Run the application."""
        self.interface.run()
