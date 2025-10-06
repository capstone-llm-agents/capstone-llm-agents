"""Local WebSocket server implementation for testing.

This module provides a local test server that can be easily swapped
with a production implementation in the future.
"""

import secrets
import uuid
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware


class LocalServer:
    """Local server implementation for testing network functionality."""

    def __init__(self) -> None:
        """Initialize the local server with in-memory storage."""
        # In-memory storage (would be replaced with a database in production)
        self.users: dict[str, dict[str, Any]] = {}  # username -> user data
        self.tokens: dict[str, dict[str, Any]] = {}  # token -> user info
        self.friends: dict[str, list[str]] = defaultdict(list)  # user_id -> [friend_ids]
        self.friend_requests: dict[str, list[str]] = defaultdict(list)  # user_id -> [requester_ids]
        self.agents: dict[str, list[dict[str, Any]]] = defaultdict(list)  # user_id -> [agents]
        self.message_queues: dict[str, list[dict[str, Any]]] = defaultdict(list)  # user_id -> [messages]
        self.active_connections: dict[str, WebSocket] = {}  # user_id -> websocket

        # Create the FastAPI app
        self.app = FastAPI(title="Local Network Server")

        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Register routes
        self._register_routes()

        # Add some default test users and agents
        self._setup_test_data()

    def _setup_test_data(self) -> None:
        """Set up some test data for development."""
        # Create test users
        test_users = [
            {"username": "alice", "password": "password123"},
            {"username": "bob", "password": "password123"},
            {"username": "charlie", "password": "password123"},
        ]

        for user_data in test_users:
            user_id = str(uuid.uuid4())
            self.users[user_data["username"]] = {
                "id": user_id,
                "username": user_data["username"],
                "password": user_data["password"],  # In production, hash this!
                "created_at": datetime.now().isoformat(),
            }

        # Set up friendships
        alice_id = self.users["alice"]["id"]
        bob_id = self.users["bob"]["id"]
        charlie_id = self.users["charlie"]["id"]

        self.friends[alice_id] = [bob_id]
        self.friends[bob_id] = [alice_id, charlie_id]
        self.friends[charlie_id] = [bob_id]

        # Set up some default agents
        self.agents[alice_id] = [
            {"name": "assistant", "description": "A helpful assistant agent", "type": "assistant"},
            {"name": "calendar", "description": "Manages calendar and scheduling", "type": "calendar"},
        ]
        self.agents[bob_id] = [
            {"name": "assistant", "description": "Bob's personal assistant", "type": "assistant"},
            {"name": "travel", "description": "Helps plan trips and travel", "type": "travel"},
        ]
        self.agents[charlie_id] = [
            {"name": "assistant", "description": "Charlie's assistant", "type": "assistant"},
        ]

    def _generate_token(self, user_id: str, username: str) -> str:
        """Generate an authentication token for a user."""
        token = secrets.token_urlsafe(32)
        self.tokens[token] = {
            "user_id": user_id,
            "username": username,
            "expires_at": (datetime.now() + timedelta(days=7)).isoformat(),
        }
        return token

    def _validate_token(self, token: str) -> dict[str, Any] | None:
        """Validate a token and return user info if valid."""
        if token not in self.tokens:
            return None

        token_data = self.tokens[token]
        expires_at = datetime.fromisoformat(token_data["expires_at"])

        if datetime.now() > expires_at:
            del self.tokens[token]
            return None

        return token_data

    def _register_routes(self) -> None:
        """Register all the HTTP and WebSocket routes."""

        @self.app.post("/login")
        async def login(username: str, password: str) -> dict[str, Any]:
            """Log in a user and return an authentication token."""
            if username not in self.users:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

            user = self.users[username]
            if user["password"] != password:  # In production, use proper password hashing
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

            token = self._generate_token(user["id"], username)
            return {
                "success": True,
                "token": token,
                "user": {"id": user["id"], "username": username},
            }

        @self.app.post("/signup")
        async def signup(username: str, password: str) -> dict[str, Any]:
            """Sign up a new user."""
            if username in self.users:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

            user_id = str(uuid.uuid4())
            self.users[username] = {
                "id": user_id,
                "username": username,
                "password": password,  # In production, hash this!
                "created_at": datetime.now().isoformat(),
            }

            # Create default assistant agent
            self.agents[user_id] = [
                {"name": "assistant", "description": "Your personal assistant", "type": "assistant"},
            ]

            token = self._generate_token(user_id, username)
            return {
                "success": True,
                "token": token,
                "user": {"id": user_id, "username": username},
            }

        @self.app.post("/logout")
        async def logout(token: str) -> dict[str, Any]:
            """Log out a user by invalidating their token."""
            if token in self.tokens:
                del self.tokens[token]
            return {"success": True, "message": "Logged out successfully"}

        @self.app.get("/friends")
        async def get_friends(token: str) -> list[dict[str, Any]]:
            """Get the list of friends for the authenticated user."""
            user_data = self._validate_token(token)
            if not user_data:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

            user_id = user_data["user_id"]
            friend_ids = self.friends.get(user_id, [])

            # Get friend details
            friends_list = []
            for friend_id in friend_ids:
                # Find the username for this friend_id
                for username, user in self.users.items():
                    if user["id"] == friend_id:
                        friends_list.append({
                            "id": friend_id,
                            "username": username,
                        })
                        break

            return friends_list

        @self.app.get("/agents/{friend_id}")
        async def get_agents(friend_id: str, token: str) -> list[dict[str, Any]]:
            """Get the list of agents for a specific friend."""
            user_data = self._validate_token(token)
            if not user_data:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

            user_id = user_data["user_id"]

            # Check if the friend exists and is actually a friend
            if friend_id not in self.friends.get(user_id, []):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not friends with this user")

            return self.agents.get(friend_id, [])

        @self.app.post("/friend_request/{friend_username}")
        async def send_friend_request(friend_username: str, token: str) -> dict[str, Any]:
            """Send a friend request to another user."""
            user_data = self._validate_token(token)
            if not user_data:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

            if friend_username not in self.users:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

            user_id = user_data["user_id"]
            friend_id = self.users[friend_username]["id"]

            # Check if already friends
            if friend_id in self.friends.get(user_id, []):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already friends")

            # Check if request already sent
            if user_id in self.friend_requests.get(friend_id, []):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Friend request already sent")

            self.friend_requests[friend_id].append(user_id)
            return {"success": True, "message": "Friend request sent"}

        @self.app.post("/accept_friend_request/{requester_username}")
        async def accept_friend_request(requester_username: str, token: str) -> dict[str, Any]:
            """Accept a friend request from another user."""
            user_data = self._validate_token(token)
            if not user_data:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

            if requester_username not in self.users:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

            user_id = user_data["user_id"]
            requester_id = self.users[requester_username]["id"]

            # Check if there's a pending request
            if requester_id not in self.friend_requests.get(user_id, []):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No pending friend request")

            # Add to friends list (bidirectional)
            self.friends[user_id].append(requester_id)
            self.friends[requester_id].append(user_id)

            # Remove the friend request
            self.friend_requests[user_id].remove(requester_id)

            return {"success": True, "message": "Friend request accepted"}

        @self.app.post("/message/{friend_id}")
        async def send_message(friend_id: str, token: str, message: dict[str, Any]) -> dict[str, Any]:
            """Send a message to a friend's agent."""
            user_data = self._validate_token(token)
            if not user_data:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

            user_id = user_data["user_id"]

            # Check if the friend exists and is actually a friend
            if friend_id not in self.friends.get(user_id, []):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not friends with this user")

            # Store the message in the queue
            message_data = {
                "id": str(uuid.uuid4()),
                "from_user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "message": message,
            }
            self.message_queues[friend_id].append(message_data)

            # If the friend is connected via WebSocket, send the message directly
            if friend_id in self.active_connections:
                try:
                    await self.active_connections[friend_id].send_json(message_data)
                except Exception:
                    # Connection might be stale, remove it
                    del self.active_connections[friend_id]

            return {"success": True, "message_id": message_data["id"]}

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket, token: str) -> None:
            """WebSocket endpoint for real-time communication."""
            # Validate token
            user_data = self._validate_token(token)
            if not user_data:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return

            user_id = user_data["user_id"]

            # Accept the connection
            await websocket.accept()
            self.active_connections[user_id] = websocket

            try:
                # Send any queued messages
                queued_messages = self.message_queues.get(user_id, [])
                for msg in queued_messages:
                    await websocket.send_json(msg)
                self.message_queues[user_id] = []

                # Keep the connection alive and listen for messages
                while True:
                    data = await websocket.receive_json()
                    # Handle incoming messages from the client
                    # For now, just echo back or handle specific message types
                    await websocket.send_json({
                        "type": "ack",
                        "message": "Message received",
                        "data": data,
                    })
            except WebSocketDisconnect:
                # Clean up when the client disconnects
                if user_id in self.active_connections:
                    del self.active_connections[user_id]
            except Exception as e:
                # Handle other exceptions
                if user_id in self.active_connections:
                    del self.active_connections[user_id]
                print(f"WebSocket error: {e}")

    def run(self, host: str = "127.0.0.1", port: int = 8000) -> None:
        """Run the server."""
        import uvicorn

        uvicorn.run(self.app, host=host, port=port)
