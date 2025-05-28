from core.app_api import AppAPI


class UserInterface:
    """A base class for user interfaces in the application."""

    def __init__(self):
        self.api: AppAPI | None = None

    def set_api(self, api: AppAPI):
        """Set the AppAPI instance for this interface."""
        self.api = api

    def exit(self):
        """Exit the application."""
        self.api.exit()
