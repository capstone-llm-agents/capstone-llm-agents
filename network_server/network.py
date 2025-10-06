"""The network object."""

from abc import ABC, abstractmethod
from typing import Any

from network_server.message import NetworkMessage


class NetworkInterface(ABC):
    """Abstract interface for network operations.

    This interface defines the contract for network operations,
    making it easy to swap between test/local and production implementations.
    """

    @abstractmethod
    async def send_message(self, message: NetworkMessage) -> dict[str, Any]:
        """Send a message to a recipient.

        Args:
            message: The NetworkMessage to send

        Returns:
            dict containing status and any response data

        """


    @abstractmethod
    async def get_friends(self, user_token: str) -> list[dict[str, Any]]:
        """Get the list of friends for a user.

        Args:
            user_token: Authentication token for the user

        Returns:
            List of friend dictionaries containing id, name, etc.

        """

    @abstractmethod
    async def get_agents(self, friend_id: str, user_token: str) -> list[dict[str, Any]]:
        """Get the list of agents for a friend.

        Args:
            friend_id: ID of the friend
            user_token: Authentication token for the user

        Returns:
            List of agent dictionaries containing name, description, etc.

        """

    @abstractmethod
    async def login(self, username: str, password: str) -> dict[str, Any]:
        """Log in a user and get authentication token.

        Args:
            username: User's username
            password: User's password

        Returns:
            dict containing token and user info or error

        """


    @abstractmethod
    async def signup(self, username: str, password: str) -> dict[str, Any]:
        """Sign up a new user.

        Args:
            username: Desired username
            password: Desired password

        Returns:
            dict containing token and user info or error

        """

    @abstractmethod
    async def send_friend_request(self, friend_id: str, user_token: str) -> dict[str, Any]:
        """Send a friend request to another user.

        Args:
            friend_id: ID of the user to send request to
            user_token: Authentication token for the user

        Returns:
            dict containing status

        """

    @abstractmethod
    async def accept_friend_request(self, friend_id: str, user_token: str) -> dict[str, Any]:
        """Accept a friend request from another user.

        Args:
            friend_id: ID of the user who sent the request
            user_token: Authentication token for the user

        Returns:
            dict containing status

        """


class Network:
    """A class representing the network client.

    This class wraps a NetworkInterface implementation and provides
    a clean API for network operations.
    """

    def __init__(self, network_impl: NetworkInterface) -> None:
        """Initialize the network client with a specific implementation.

        Args:
            network_impl: The concrete NetworkInterface implementation to use

        """
        self._impl = network_impl

    async def send_message(self, message: NetworkMessage) -> dict[str, Any]:
        """Send a message to a recipient."""
        return await self._impl.send_message(message)

    async def get_friends(self, user_token: str) -> list[dict[str, Any]]:
        """Get the list of friends for a user."""
        return await self._impl.get_friends(user_token)

    async def get_agents(self, friend_id: str, user_token: str) -> list[dict[str, Any]]:
        """Get the list of agents for a friend."""
        return await self._impl.get_agents(friend_id, user_token)

    async def login(self, username: str, password: str) -> dict[str, Any]:
        """Log in a user and get authentication token."""
        return await self._impl.login(username, password)

    async def signup(self, username: str, password: str) -> dict[str, Any]:
        """Sign up a new user."""
        return await self._impl.signup(username, password)

    async def send_friend_request(self, friend_id: str, user_token: str) -> dict[str, Any]:
        """Send a friend request to another user."""
        return await self._impl.send_friend_request(friend_id, user_token)

    async def accept_friend_request(self, friend_id: str, user_token: str) -> dict[str, Any]:
        """Accept a friend request from another user."""
        return await self._impl.accept_friend_request(friend_id, user_token)
