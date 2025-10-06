# Network Server

A WebSocket-based network server for multi-agent communication with support for authentication, friend management, and real-time messaging.

## Features

- **User Authentication**: Login, signup, and logout functionality
- **Friend Management**: Send and accept friend requests
- **Agent Discovery**: List agents available for your friends
- **Message Sending**: Send messages to friend's agents via HTTP
- **Real-time Communication**: WebSocket support for receiving messages instantly
- **Pluggable Architecture**: Easy to swap between local test server and production server

## Architecture

The network server uses a clean interface-based design that makes it easy to switch between different implementations:

```
NetworkInterface (Abstract)
    ↓
WebSocketNetworkClient (Implementation)
    ↓
Network (Wrapper)
```

This means you can easily swap the `WebSocketNetworkClient` with a different implementation (e.g., gRPC, REST-only, etc.) without changing any code that uses the `Network` class.

## Installation

The server requires the following dependencies:

```bash
# FastAPI for the HTTP/WebSocket server
pip install fastapi uvicorn

# WebSocket support
pip install websockets

# HTTP client library
pip install httpx
```

Or if using uv (recommended):

```bash
uv pip install fastapi uvicorn websockets httpx
```

## Running the Server

### Start the local test server:

```bash
python -m network_server.run_network
```

Or with custom host/port:

```bash
python -m network_server.run_network --host 0.0.0.0 --port 8080
```

The server will start with three test users:
- `alice` / `password123`
- `bob` / `password123`
- `charlie` / `password123`

## API Endpoints

### Authentication

- **POST /login**
  - Query params: `username`, `password`
  - Returns: `{success: bool, token: str, user: {...}}`

- **POST /signup**
  - Query params: `username`, `password`
  - Returns: `{success: bool, token: str, user: {...}}`

- **POST /logout**
  - Query params: `token`
  - Returns: `{success: bool, message: str}`

### Friends Management

- **GET /friends**
  - Query params: `token`
  - Returns: List of friends `[{id: str, username: str}, ...]`

- **POST /friend_request/{friend_username}**
  - Query params: `token`
  - Returns: `{success: bool, message: str}`

- **POST /accept_friend_request/{requester_username}**
  - Query params: `token`
  - Returns: `{success: bool, message: str}`

### Agents

- **GET /agents/{friend_id}**
  - Query params: `token`
  - Returns: List of agents `[{name: str, description: str, type: str}, ...]`

### Messaging

- **POST /message/{friend_id}**
  - Query params: `token`
  - Body: NetworkMessage JSON
  - Returns: `{success: bool, message_id: str}`

### WebSocket

- **WS /ws**
  - Query params: `token`
  - Receives real-time messages

## Usage Example

```python
import asyncio
from network_server.network import Network
from network_server.websocket_client import WebSocketNetworkClient
from network_server.message import NetworkMessage, MessageType
from network_server.network_fragment import NetworkFragment, FragmentKindSerializable, FragmentSource

async def main():
    # Create client and network wrapper
    client = WebSocketNetworkClient(
        base_url="http://127.0.0.1:8000",
        ws_url="ws://127.0.0.1:8000/ws"
    )
    network = Network(client)
    
    # Login
    result = await network.login("alice", "password123")
    token = result["token"]
    
    # Get friends
    friends = await network.get_friends(token)
    print(f"Friends: {friends}")
    
    # Get agents for a friend
    if friends:
        agents = await network.get_agents(friends[0]["id"], token)
        print(f"Agents: {agents}")
    
    # Send a message
    fragment = NetworkFragment(
        name="greeting",
        kind=FragmentKindSerializable(
            name="text",
            content={"text": "Hello!"},
        ),
        source=FragmentSource.USER,
    )
    
    message = NetworkMessage(
        sender="alice_assistant",
        sender_client=result["user"]["id"],
        recipient="bob_assistant",
        recipient_client=friends[0]["id"],
        fragments=[fragment],
        message_type=MessageType.PROPOSAL,
    )
    
    await network.send_message(message)
    
    # Logout
    await client.logout()

if __name__ == "__main__":
    asyncio.run(main())
```

See `example_client.py` for a more comprehensive example.

## Switching to Production

To switch from the local test server to a production server:

1. Implement a new class that inherits from `NetworkInterface`
2. Update the connection URLs when creating the client
3. No other code changes needed!

Example:

```python
# Development
client = WebSocketNetworkClient(
    base_url="http://127.0.0.1:8000",
    ws_url="ws://127.0.0.1:8000/ws"
)

# Production
client = WebSocketNetworkClient(
    base_url="https://api.yourserver.com",
    ws_url="wss://api.yourserver.com/ws"
)

# Everything else stays the same!
network = Network(client)
```

## Message Types

The server supports the following message types (from `MessageType` enum):

- `PROPOSAL`: Initiate a conversation
- `ACCEPTANCE`: Accept a proposal
- `REJECTION`: Reject a proposal
- `QUERY`: Ask for information
- `TASK`: Request an action
- `WAIT`: Acknowledge and wait for completion
- `INFORMATION`: Provide results
- `THANKS`: Express gratitude
- `DISAPPOINTMENT`: Express dissatisfaction
- `ERROR`: Report an error
- `END`: End the conversation

## Data Models

### NetworkMessage

```python
NetworkMessage(
    sender: str,              # Agent name
    sender_client: str,       # Client/user ID
    recipient: str,           # Recipient agent name
    recipient_client: str,    # Recipient client/user ID
    fragments: list[NetworkFragment],
    message_type: MessageType,
    context: dict | None = None
)
```

### NetworkFragment

```python
NetworkFragment(
    name: str,
    kind: FragmentKindSerializable,
    description: str | None = None,
    source: FragmentSource = FragmentSource.UNKNOWN
)
```

## Testing

Run the example client (make sure the server is running first):

```bash
# Terminal 1: Start server
python -m network_server.run_network

# Terminal 2: Run example
python -m network_server.example_client
```

## Future Enhancements

- Add database persistence (currently uses in-memory storage)
- Implement proper password hashing
- Add rate limiting
- Add message history/persistence
- Add support for group chats
- Add file/media sharing
- Add encryption for messages
- Add presence/status indicators
