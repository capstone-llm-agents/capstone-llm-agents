"""Convenient client wrapper for network operations.

This module provides a high-level client that simplifies common operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from network_server.message import (
    MessageType,
    NetworkMessage,
)
from network_server.network import Network
from network_server.network_fragment import (
    FragmentKindSerializable,
    FragmentSource,
    NetworkFragment,
)
from network_server.websocket_client import WebSocketNetworkClient

if TYPE_CHECKING:
    from collections.abc import Callable


class NotAuthenticatedError(Exception):
    """Exception raised when an operation requires authentication but the client is not authenticated."""


class NetworkClient:
    """High-level client for network operations.

    This class wraps the Network and WebSocketNetworkClient to provide
    a simpler API for common operations.
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8000",
        ws_url: str = "ws://127.0.0.1:8000/ws",
    ) -> None:
        """Initialize the network client.

        Args:
            base_url: Base URL for HTTP endpoints
            ws_url: WebSocket URL for real-time communication

        """
        self._ws_client = WebSocketNetworkClient(base_url=base_url, ws_url=ws_url)
        self._network = Network(self._ws_client)
        self._user_id: str | None = None
        self._username: str | None = None
        self._token: str | None = None

    @property
    def is_authenticated(self) -> bool:
        """Check if the client is authenticated."""
        return self._token is not None

    @property
    def user_id(self) -> str | None:
        """Get the current user ID."""
        return self._user_id

    @property
    def username(self) -> str | None:
        """Get the current username."""
        return self._username

    @property
    def token(self) -> str | None:
        """Get the authentication token."""
        return self._token

    async def login(self, username: str, password: str) -> bool:
        """Log in to the network.

        Args:
            username: User's username
            password: User's password

        Returns:
            True if login successful, False otherwise

        """
        result = await self._network.login(username, password)
        if result.get("success"):
            self._token = result.get("token")
            self._user_id = result.get("user", {}).get("id")
            self._username = username
            return True
        return False

    async def signup(self, username: str, password: str) -> bool:
        """Sign up for a new account.

        Args:
            username: Desired username
            password: Desired password

        Returns:
            True if signup successful, False otherwise

        """
        result = await self._network.signup(username, password)
        if result.get("success"):
            self._token = result.get("token")
            self._user_id = result.get("user", {}).get("id")
            self._username = username
            return True
        return False

    async def logout(self) -> bool:
        """Log out from the network.

        Returns:
            True if logout successful, False otherwise

        """
        if not self._token:
            return False

        result = await self._ws_client.logout()
        if result.get("success"):
            self._token = None
            self._user_id = None
            self._username = None
            return True
        return False

    async def get_friends(self) -> list[dict[str, Any]]:
        """Get the list of friends.

        Returns:
            List of friend dictionaries

        """
        if not self._token:
            msg = "Not authenticated. Please log in first."
            raise NotAuthenticatedError(msg)
        return await self._network.get_friends(self._token)

    async def get_pending_friend_requests(self) -> list[dict[str, Any]]:
        """Get the list of pending friend requests.

        Returns:
            List of friend request dictionaries

        """
        if not self._token:
            return []
        return await self._network.get_pending_friend_requests(self._token)

    async def get_agents(self, friend_id: str) -> list[dict[str, Any]]:
        """Get the list of agents for a friend.

        Args:
            friend_id: ID of the friend

        Returns:
            List of agent dictionaries

        """
        if not self._token:
            return []
        return await self._network.get_agents(friend_id, self._token)

    async def send_friend_request(self, friend_username: str) -> bool:
        """Send a friend request.

        Args:
            friend_username: Username of the person to add

        Returns:
            True if request sent successfully, False otherwise
        """
        if not self._token:
            return False
        result = await self._network.send_friend_request(friend_username, self._token)
        return result.get("success", False)

    async def accept_friend_request(self, requester_username: str) -> bool:
        """Accept a friend request.

        Args:
            requester_username: Username of the person who sent the request

        Returns:
            True if request accepted successfully, False otherwise
        """
        if not self._token:
            return False
        result = await self._network.accept_friend_request(requester_username, self._token)
        return result.get("success", False)

    async def send_text_message(
        self,
        recipient_id: str,
        recipient_agent: str,
        text: str,
        message_type: MessageType = MessageType.PROPOSAL,
        sender_agent: str = "assistant",
    ) -> bool:
        """Send a simple text message.

        Args:
            recipient_id: ID of the recipient user
            recipient_agent: Name of the recipient's agent
            text: The text message to send
            message_type: Type of message (default: PROPOSAL)
            sender_agent: Name of the sender's agent (default: "assistant")

        Returns:
            True if message sent successfully, False otherwise

        """
        if not self._token or not self._user_id:
            return False

        # Create a text fragment
        fragment = NetworkFragment(
            name="message",
            kind=FragmentKindSerializable(
                name="text",
                content={"text": text},
            ),
            source=FragmentSource.USER,
        )

        # Create the message
        message = NetworkMessage(
            sender=f"{self._username}_{sender_agent}",
            sender_client=self._user_id,
            recipient=recipient_agent,
            recipient_client=recipient_id,
            fragments=[fragment],
            message_type=message_type,
        )

        # Send the message
        result = await self._network.send_message(message)
        return result.get("success", False)

    async def send_message(
        self,
        recipient_id: str,
        recipient_agent: str,
        fragments: list[NetworkFragment],
        message_type: MessageType,
        sender_agent: str = "assistant",
        context: dict[str, Any] | None = None,
    ) -> bool:
        """Send a message with custom fragments.

        Args:
            recipient_id: ID of the recipient user
            recipient_agent: Name of the recipient's agent
            fragments: List of message fragments
            message_type: Type of message
            sender_agent: Name of the sender's agent (default: "assistant")
            context: Optional context dictionary

        Returns:
            True if message sent successfully, False otherwise

        """
        if not self._token or not self._user_id:
            return False

        message = NetworkMessage(
            sender=f"{self._username}_{sender_agent}",
            sender_client=self._user_id,
            recipient=recipient_agent,
            recipient_client=recipient_id,
            fragments=fragments,
            message_type=message_type,
            context=context,
        )

        result = await self._network.send_message(message)
        return result.get("success", False)

    def add_message_handler(self, handler: Callable[[dict[str, Any]], None]) -> None:
        """Add a handler for incoming messages.

        Args:
            handler: Callback function that takes a message dict

        """
        self._ws_client.add_message_handler(handler)

    async def ping(self) -> dict[str, Any]:
        """Ping the server to check connectivity.

        Returns:
            dict containing server status

        """
        return await self._network.ping()
