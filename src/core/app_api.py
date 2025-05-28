"""A collection of APIs to interact with the application."""

from core.mas_api import MASAPI
from storage.api import StorageAPI


class AppAPI:
    """A class to interact with the application APIs."""

    def __init__(self, mas_api: MASAPI, storage_api: StorageAPI):
        self.mas_api = mas_api
        self.storage_api = storage_api

    def start(self):
        """Start the application."""
        # NOTE: order matters because mas_api uses chat history loaded from storage_api
        self.storage_api.start()

        # sync chat history
        self.mas_api.set_chat_history(self.storage_api.get_chat_history())

        self.mas_api.mas.start()

    def exit(self):
        """Exit the application."""
        self.storage_api.save()
        print("Exiting application...")
