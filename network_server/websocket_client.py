"""WebSocket client implementation for network communication.

This module provides a client that connects to the network server
via WebSockets for real-time communication.
"""

import asyncio
import contextlib
from collections.abc import Callable
from typing import Any

import httpx
import websockets

from network_server.message import NetworkMessage
from network_server.network import NetworkInterface


class WebSocketNetworkClient(NetworkInterface):
    """WebSocket-based network client implementation.

    This client can connect to either a local test server or a production server,
    making it easy to swap between environments.
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8000",
        ws_url: str = "ws://127.0.0.1:8000/ws",
    ) -> None:
        """Initialize the WebSocket network client.

        Args:
            base_url: Base URL for HTTP endpoints
            ws_url: WebSocket URL for real-time communication

        """
        self.base_url = base_url.rstrip("/")
        self.ws_url = ws_url
        self.token: str | None = None
        self.websocket: Any | None = None
        self.message_handlers: list[Callable[[dict[str, Any]], None]] = []
        self._ws_task: asyncio.Task | None = None

    async def send_message(self, message: NetworkMessage) -> dict[str, Any]:
        """Send a message to a recipient via HTTP.

        Args:
            message: The NetworkMessage to send

        Returns:
            dict containing status and any response data

        """
        if not self.token:
            return {"success": False, "error": "Not authenticated"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/message/{message.recipient_client}",
                    params={"token": self.token},
                    json=message.serialize(),
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            return {"success": False, "error": str(e)}

    async def get_friends(self, user_token: str) -> list[dict[str, Any]]:
        """Get the list of friends for a user.

        Args:
            user_token: Authentication token for the user

        Returns:
            List of friend dictionaries

        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/friends",
                    params={"token": user_token},
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            print(f"Error getting friends: {e}")
            return []

    async def get_pending_friend_requests(self, user_token: str) -> list[dict[str, Any]]:
        """Get the list of pending friend requests for a user.

        Args:
            user_token: Authentication token for the user

        Returns:
            List of friend request dictionaries

        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/friend-requests/pending",
                    params={"token": user_token},
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            print(f"Error getting pending friend requests: {e}")
            return []

    async def get_agents(self, friend_id: str, user_token: str) -> list[dict[str, Any]]:
        """Get the list of agents for a friend.

        Args:
            friend_id: ID of the friend
            user_token: Authentication token for the user

        Returns:
            List of agent dictionaries

        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/agents/{friend_id}",
                    params={"token": user_token},
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            print(f"Error getting agents: {e}")
            return []

    async def login(self, username: str, password: str) -> dict[str, Any]:
        """Log in a user and get authentication token.

        Args:
            username: User's username
            password: User's password

        Returns:
            dict containing token and user info or error

        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/login",
                    params={"username": username, "password": password},
                    timeout=30.0,
                )
                response.raise_for_status()
                result = response.json()

                if result.get("success"):
                    self.token = result.get("token")
                    # Start WebSocket connection after successful login
                    await self._connect_websocket()

                return result
        except httpx.HTTPError as e:
            return {"success": False, "error": str(e)}

    async def signup(self, username: str, password: str) -> dict[str, Any]:
        """Sign up a new user.

        Args:
            username: Desired username
            password: Desired password

        Returns:
            dict containing token and user info or error

        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/signup",
                    params={"username": username, "password": password},
                    timeout=30.0,
                )
                response.raise_for_status()
                result = response.json()

                if result.get("success"):
                    self.token = result.get("token")
                    # Start WebSocket connection after successful signup
                    await self._connect_websocket()

                return result
        except httpx.HTTPError as e:
            return {"success": False, "error": str(e)}

    async def logout(self) -> dict[str, Any]:
        """Log out the current user."""
        if not self.token:
            return {"success": False, "error": "Not authenticated"}

        try:
            # Close WebSocket connection
            await self._disconnect_websocket()

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/logout",
                    params={"token": self.token},
                    timeout=30.0,
                )
                response.raise_for_status()
                result = response.json()

                self.token = None
                return result
        except httpx.HTTPError as e:
            return {"success": False, "error": str(e)}

    async def send_friend_request(self, friend_id: str, user_token: str) -> dict[str, Any]:
        """Send a friend request to another user.

        Args:
            friend_id: ID/username of the user to send request to
            user_token: Authentication token for the user

        Returns:
            dict containing status

        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/friend_request/{friend_id}",
                    params={"token": user_token},
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            return {"success": False, "error": str(e)}

    async def accept_friend_request(self, friend_id: str, user_token: str) -> dict[str, Any]:
        """Accept a friend request from another user.

        Args:
            friend_id: ID/username of the user who sent the request
            user_token: Authentication token for the user

        Returns:
            dict containing status
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/accept_friend_request/{friend_id}",
                    params={"token": user_token},
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            return {"success": False, "error": str(e)}

    def add_message_handler(self, handler: Callable[[dict[str, Any]], None]) -> None:
        """Add a callback handler for incoming messages.

        Args:
            handler: Callback function that takes a message dict

        """
        self.message_handlers.append(handler)

    async def _connect_websocket(self) -> None:
        """Establish WebSocket connection for real-time communication."""
        if not self.token:
            return

        try:
            # Close existing connection if any
            await self._disconnect_websocket()

            # Start new WebSocket task
            self._ws_task = asyncio.create_task(self._websocket_listener())
        except Exception as e:
            print(f"Error connecting to WebSocket: {e}")

    async def _disconnect_websocket(self) -> None:
        """Close the WebSocket connection."""
        if self._ws_task:
            self._ws_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._ws_task
            self._ws_task = None

        if self.websocket:
            await self.websocket.close()
            self.websocket = None

    async def _websocket_listener(self) -> None:
        """Listen for incoming WebSocket messages."""
        if not self.token:
            return

        ws_url_with_token = f"{self.ws_url}?token={self.token}"

        try:
            async with websockets.connect(ws_url_with_token) as websocket:
                self.websocket = websocket

                async for message in websocket:
                    try:
                        import json

                        data = json.loads(message)

                        # Call all registered message handlers
                        for handler in self.message_handlers:
                            handler(data)
                    except Exception as e:
                        print(f"Error processing WebSocket message: {e}")
        except asyncio.CancelledError:
            # Clean cancellation
            pass
        except Exception as e:
            print(f"WebSocket connection error: {e}")
