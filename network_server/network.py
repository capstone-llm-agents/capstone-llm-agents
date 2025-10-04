"""The network object."""

from llm_mas.client.account.client import Client


class Network:
    """A class representing the network server."""

    def __init__(self) -> None:
        """Initialize the network server."""
        self.clients: list[Client] = []

    def add_client(self, client: Client) -> None:
        """Add a client to the network server."""
        self.clients.append(client)

    def get_clients(self) -> list[Client]:
        """Get the list of clients connected to the network server."""
        return self.clients

    def remove_client(self, client: Client) -> None:
        """Remove a client from the network server."""
        self.clients.remove(client)
