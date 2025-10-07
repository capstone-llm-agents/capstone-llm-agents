"""Local WebSocket server implementation for testing.

This module provides a local test server that can be easily swapped
with a production implementation in the future.
"""

import json
import secrets
import sqlite3
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware


class LocalServer:
    """Local server implementation for testing network functionality."""

    def __init__(self, db_path: str | None = None) -> None:
        """Initialize the local server with SQLite database storage.
        
        Args:
            db_path: Path to the SQLite database file. If None, uses db/network.sqlite3
        """
        # Set up database path
        if db_path is None:
            db_dir = Path(__file__).parent.parent / "db"
            db_dir.mkdir(exist_ok=True)
            db_path = str(db_dir / "network.sqlite3")
        
        self.db_path = db_path
        self.active_connections: dict[str, WebSocket] = {}  # user_id -> websocket (not persisted)
        
        # Initialize database
        self._init_database()

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

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_database(self) -> None:
        """Initialize the database schema."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        # Tokens table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tokens (
                token TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                username TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)

        # Friends table (bidirectional relationships)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS friends (
                user_id TEXT NOT NULL,
                friend_id TEXT NOT NULL,
                PRIMARY KEY (user_id, friend_id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (friend_id) REFERENCES users (id)
            )
        """)

        # Friend requests table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS friend_requests (
                requester_id TEXT NOT NULL,
                recipient_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                PRIMARY KEY (requester_id, recipient_id),
                FOREIGN KEY (requester_id) REFERENCES users (id),
                FOREIGN KEY (recipient_id) REFERENCES users (id)
            )
        """)

        # Agents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                type TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)

        # Message queue table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS message_queue (
                id TEXT PRIMARY KEY,
                recipient_id TEXT NOT NULL,
                from_user_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                message_json TEXT NOT NULL,
                FOREIGN KEY (recipient_id) REFERENCES users (id),
                FOREIGN KEY (from_user_id) REFERENCES users (id)
            )
        """)

        conn.commit()
        conn.close()

    def _setup_test_data(self) -> None:
        """Set up some test data for development."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Check if test data already exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", ("alice",))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return  # Test data already exists

        # Create test users
        test_users = [
            {"username": "alice", "password": "password123"},
            {"username": "bob", "password": "password123"},
            {"username": "charlie", "password": "password123"},
        ]

        user_ids = {}
        for user_data in test_users:
            user_id = str(uuid.uuid4())
            user_ids[user_data["username"]] = user_id
            cursor.execute(
                "INSERT INTO users (id, username, password, created_at) VALUES (?, ?, ?, ?)",
                (user_id, user_data["username"], user_data["password"], datetime.now().isoformat()),
            )

        # Set up friendships
        friendships = [
            (user_ids["alice"], user_ids["bob"]),
            (user_ids["bob"], user_ids["alice"]),
            (user_ids["bob"], user_ids["charlie"]),
            (user_ids["charlie"], user_ids["bob"]),
        ]
        for user_id, friend_id in friendships:
            cursor.execute(
                "INSERT INTO friends (user_id, friend_id) VALUES (?, ?)",
                (user_id, friend_id),
            )

        # Set up some default agents
        agents_data = [
            (user_ids["alice"], "assistant", "A helpful assistant agent", "assistant"),
            (user_ids["alice"], "calendar", "Manages calendar and scheduling", "calendar"),
            (user_ids["bob"], "assistant", "Bob's personal assistant", "assistant"),
            (user_ids["bob"], "travel", "Helps plan trips and travel", "travel"),
            (user_ids["charlie"], "assistant", "Charlie's assistant", "assistant"),
        ]
        for user_id, name, description, agent_type in agents_data:
            cursor.execute(
                "INSERT INTO agents (id, user_id, name, description, type) VALUES (?, ?, ?, ?, ?)",
                (str(uuid.uuid4()), user_id, name, description, agent_type),
            )

        conn.commit()
        conn.close()

    def _generate_token(self, user_id: str, username: str) -> str:
        """Generate an authentication token for a user."""
        token = secrets.token_urlsafe(32)
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tokens (token, user_id, username, expires_at) VALUES (?, ?, ?, ?)",
            (token, user_id, username, (datetime.now() + timedelta(days=7)).isoformat()),
        )
        conn.commit()
        conn.close()
        return token

    def _validate_token(self, token: str) -> dict[str, Any] | None:
        """Validate a token and return user info if valid."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id, username, expires_at FROM tokens WHERE token = ?",
            (token,),
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        expires_at = datetime.fromisoformat(row["expires_at"])
        if datetime.now() > expires_at:
            # Delete expired token
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tokens WHERE token = ?", (token,))
            conn.commit()
            conn.close()
            return None

        return {"user_id": row["user_id"], "username": row["username"]}

    def _register_routes(self) -> None:
        """Register all the HTTP and WebSocket routes."""

        @self.app.post("/login")
        async def login(username: str, password: str) -> dict[str, Any]:
            """Log in a user and return an authentication token."""
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()

            if not row:
                conn.close()
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

            if row["password"] != password:  # In production, use proper password hashing
                conn.close()
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

            user_id = row["id"]

            # Check if user already has an active WebSocket connection
            if user_id in self.active_connections:
                conn.close()
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User is already logged in from another location.",
                )

            # Generate new token (old tokens can remain for token validation)
            token = self._generate_token(user_id, username)
            conn.close()
            return {
                "success": True,
                "token": token,
                "user": {"id": user_id, "username": username},
            }

        @self.app.post("/signup")
        async def signup(username: str, password: str) -> dict[str, Any]:
            """Sign up a new user."""
            conn = self._get_connection()
            cursor = conn.cursor()

            # Check if username exists
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                conn.close()
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

            user_id = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO users (id, username, password, created_at) VALUES (?, ?, ?, ?)",
                (user_id, username, password, datetime.now().isoformat()),
            )

            # Create default assistant agent
            cursor.execute(
                "INSERT INTO agents (id, user_id, name, description, type) VALUES (?, ?, ?, ?, ?)",
                (str(uuid.uuid4()), user_id, "assistant", "Your personal assistant", "assistant"),
            )

            conn.commit()
            conn.close()

            token = self._generate_token(user_id, username)
            return {
                "success": True,
                "token": token,
                "user": {"id": user_id, "username": username},
            }

        @self.app.get("/friends")
        async def get_friends(token: str) -> list[dict[str, Any]]:
            """Get the list of friends for the authenticated user."""
            user_data = self._validate_token(token)
            if not user_data:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

            user_id = user_data["user_id"]
            
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.id, u.username
                FROM friends f
                JOIN users u ON f.friend_id = u.id
                WHERE f.user_id = ?
            """, (user_id,))
            
            friends_list = [{"id": row["id"], "username": row["username"]} for row in cursor.fetchall()]
            conn.close()
            
            return friends_list

        @self.app.get("/agents/{friend_id}")
        async def get_agents(friend_id: str, token: str) -> list[dict[str, Any]]:
            """Get the list of agents for a specific friend."""
            user_data = self._validate_token(token)
            if not user_data:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

            user_id = user_data["user_id"]

            # Check if the friend exists and is actually a friend
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM friends WHERE user_id = ? AND friend_id = ?",
                (user_id, friend_id),
            )
            if cursor.fetchone()[0] == 0:
                conn.close()
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not friends with this user")

            # Get agents
            cursor.execute(
                "SELECT name, description, type FROM agents WHERE user_id = ?",
                (friend_id,),
            )
            agents = [{"name": row["name"], "description": row["description"], "type": row["type"]} 
                     for row in cursor.fetchall()]
            conn.close()
            
            return agents

        @self.app.post("/friend_request/{friend_username}")
        async def send_friend_request(friend_username: str, token: str) -> dict[str, Any]:
            """Send a friend request to another user."""
            user_data = self._validate_token(token)
            if not user_data:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

            conn = self._get_connection()
            cursor = conn.cursor()

            # Check if friend exists
            cursor.execute("SELECT id FROM users WHERE username = ?", (friend_username,))
            friend_row = cursor.fetchone()
            if not friend_row:
                conn.close()
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

            user_id = user_data["user_id"]
            friend_id = friend_row["id"]

            # Check if already friends
            cursor.execute(
                "SELECT COUNT(*) FROM friends WHERE user_id = ? AND friend_id = ?",
                (user_id, friend_id),
            )
            if cursor.fetchone()[0] > 0:
                conn.close()
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already friends")

            # Check if request already sent
            cursor.execute(
                "SELECT COUNT(*) FROM friend_requests WHERE requester_id = ? AND recipient_id = ?",
                (user_id, friend_id),
            )
            if cursor.fetchone()[0] > 0:
                conn.close()
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Friend request already sent")

            # Send friend request
            cursor.execute(
                "INSERT INTO friend_requests (requester_id, recipient_id, created_at) VALUES (?, ?, ?)",
                (user_id, friend_id, datetime.now().isoformat()),
            )
            conn.commit()
            conn.close()

            return {"success": True, "message": "Friend request sent"}

        @self.app.post("/accept_friend_request/{requester_username}")
        async def accept_friend_request(requester_username: str, token: str) -> dict[str, Any]:
            """Accept a friend request from another user."""
            user_data = self._validate_token(token)
            if not user_data:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

            conn = self._get_connection()
            cursor = conn.cursor()

            # Check if requester exists
            cursor.execute("SELECT id FROM users WHERE username = ?", (requester_username,))
            requester_row = cursor.fetchone()
            if not requester_row:
                conn.close()
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

            user_id = user_data["user_id"]
            requester_id = requester_row["id"]

            # Check if there's a pending request
            cursor.execute(
                "SELECT COUNT(*) FROM friend_requests WHERE requester_id = ? AND recipient_id = ?",
                (requester_id, user_id),
            )
            if cursor.fetchone()[0] == 0:
                conn.close()
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No pending friend request")

            # Add to friends list (bidirectional)
            cursor.execute("INSERT INTO friends (user_id, friend_id) VALUES (?, ?)", (user_id, requester_id))
            cursor.execute("INSERT INTO friends (user_id, friend_id) VALUES (?, ?)", (requester_id, user_id))

            # Remove the friend request
            cursor.execute(
                "DELETE FROM friend_requests WHERE requester_id = ? AND recipient_id = ?",
                (requester_id, user_id),
            )

            conn.commit()
            conn.close()

            return {"success": True, "message": "Friend request accepted"}

        @self.app.post("/message/{friend_id}")
        async def send_message(friend_id: str, token: str, message: dict[str, Any]) -> dict[str, Any]:
            """Send a message to a friend's agent."""
            user_data = self._validate_token(token)
            if not user_data:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

            user_id = user_data["user_id"]

            # Check if the friend exists and is actually a friend
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM friends WHERE user_id = ? AND friend_id = ?",
                (user_id, friend_id),
            )
            if cursor.fetchone()[0] == 0:
                conn.close()
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not friends with this user")

            # Store the message in the queue
            message_id = str(uuid.uuid4())
            message_data = {
                "id": message_id,
                "from_user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "message": message,
            }

            cursor.execute(
                "INSERT INTO message_queue (id, recipient_id, from_user_id, timestamp, message_json) VALUES (?, ?, ?, ?, ?)",
                (message_id, friend_id, user_id, message_data["timestamp"], json.dumps(message)),
            )
            conn.commit()
            conn.close()

            # If the friend is connected via WebSocket, send the message directly
            if friend_id in self.active_connections:
                try:
                    await self.active_connections[friend_id].send_json(message_data)
                    # Remove from queue since it was delivered
                    conn = self._get_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM message_queue WHERE id = ?", (message_id,))
                    conn.commit()
                    conn.close()
                except Exception:
                    # Connection might be stale, remove it
                    del self.active_connections[friend_id]

            return {"success": True, "message_id": message_id}

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
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, from_user_id, timestamp, message_json FROM message_queue WHERE recipient_id = ?",
                    (user_id,),
                )
                queued_messages = cursor.fetchall()
                
                for msg_row in queued_messages:
                    message_data = {
                        "id": msg_row["id"],
                        "from_user_id": msg_row["from_user_id"],
                        "timestamp": msg_row["timestamp"],
                        "message": json.loads(msg_row["message_json"]),
                    }
                    await websocket.send_json(message_data)
                
                # Clear the queue
                cursor.execute("DELETE FROM message_queue WHERE recipient_id = ?", (user_id,))
                conn.commit()
                conn.close()

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
