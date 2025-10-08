# Quick Start Guide

## 1. Install Dependencies

```bash
# If using uv (recommended)
uv pip install fastapi uvicorn websockets httpx

# Or with regular pip
pip install fastapi uvicorn websockets httpx
```

## 2. Start the Server

Open a terminal and run:

```bash
python -m network_server.run_network
```

You should see:
```
Starting local network server on 127.0.0.1:8000
HTTP endpoints available at: http://127.0.0.1:8000
WebSocket endpoint available at: ws://127.0.0.1:8000/ws

Test users available:
  - alice / password123
  - bob / password123
  - charlie / password123

Press Ctrl+C to stop the server
```

## 3. Run the Simple Example

Open another terminal and run:

```bash
python -m network_server.simple_example
```

This will demonstrate:
- Logging in as a user
- Getting the friends list
- Viewing available agents
- Sending a message
- Logging out

## 4. Run the Full Example

For a more comprehensive demonstration:

```bash
python -m network_server.example_client
```

This demonstrates:
- All authentication features
- Friend management
- Agent discovery
- Message sending with custom fragments
- WebSocket message handling
- Friend requests

## 5. Test the Implementation

Run a quick test to verify everything works:

```bash
python -m network_server.test_network
```

## 6. Use in Your Code

### Simple Usage

```python
import asyncio
from network_server.network_client import NetworkClient
from network_server.message import MessageType

async def main():
    # Create and login
    client = NetworkClient()
    await client.login("alice", "password123")
    
    # Get friends
    friends = await client.get_friends()
    
    # Send a message
    if friends:
        await client.send_text_message(
            recipient_id=friends[0]["id"],
            recipient_agent="assistant",
            text="Hello!",
            message_type=MessageType.PROPOSAL
        )
    
    # Logout
    await client.logout()

asyncio.run(main())
```

### Advanced Usage with Message Handlers

```python
import asyncio
from network_server.network_client import NetworkClient

def handle_message(msg):
    print(f"Received: {msg}")

async def main():
    client = NetworkClient()
    
    # Add handler for incoming messages
    client.add_message_handler(handle_message)
    
    # Login (WebSocket will automatically connect)
    await client.login("alice", "password123")
    
    # Keep alive to receive messages
    await asyncio.sleep(10)
    
    await client.logout()

asyncio.run(main())
```

## 7. Switching to Production

When ready to deploy, simply change the URLs:

```python
# Development
client = NetworkClient(
    base_url="http://127.0.0.1:8000",
    ws_url="ws://127.0.0.1:8000/ws"
)

# Production
client = NetworkClient(
    base_url="https://api.yourserver.com",
    ws_url="wss://api.yourserver.com/ws"
)
```

No other code changes needed!

## Available Endpoints

### Authentication
- `POST /login` - Log in a user
- `POST /signup` - Create a new account
- `POST /logout` - Log out

### Friends
- `GET /friends` - Get friends list
- `POST /friend_request/{username}` - Send friend request
- `POST /accept_friend_request/{username}` - Accept request

### Agents
- `GET /agents/{friend_id}` - List friend's agents

### Messaging
- `POST /message/{friend_id}` - Send a message
- `WS /ws` - WebSocket for real-time messages

## Troubleshooting

### Port Already in Use

If port 8000 is already taken:

```bash
python -m network_server.run_network --port 8080
```

### Connection Refused

Make sure the server is running before trying to connect with the client.

### Import Errors

Make sure you're running from the project root directory and all dependencies are installed.

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [IMPLEMENTATION.md](IMPLEMENTATION.md) for architecture details
- Explore the example files to understand the API
- Integrate into your agent system!
