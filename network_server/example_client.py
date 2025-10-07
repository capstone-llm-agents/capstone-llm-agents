"""Example client demonstrating how to use the network server.

This script shows how to:
1. Connect to the server
2. Login/signup
3. Get friends list
4. Get agents for friends
5. Send messages
6. Receive real-time messages via WebSocket
"""

import asyncio

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


async def on_message_received(message: dict) -> None:
    """Handle incoming messages from the WebSocket.

    Args:
        message: The received message data

    """
    print(f"\n[Received Message]: {message}\n")


async def example_usage() -> None:
    """Demonstrate the network client usage."""
    # Create a network client (connecting to local server)
    client = WebSocketNetworkClient(
        base_url="http://127.0.0.1:8000",
        ws_url="ws://127.0.0.1:8000/ws",
    )

    # Wrap it in the Network abstraction
    network = Network(client)

    print("=== Network Client Example ===\n")

    # Example 1: Login
    print("1. Logging in as 'alice'...")
    login_result = await network.login("alice", "password123")
    if login_result.get("success"):
        print(f"   ✓ Logged in successfully!")
        print(f"   Token: {login_result.get('token')[:20]}...")
        print(f"   User ID: {login_result.get('user', {}).get('id')}\n")
    else:
        print(f"   ✗ Login failed: {login_result.get('error')}\n")
        return

    # Store token for later use
    token = login_result.get("token")

    # Add a message handler for real-time messages
    client.add_message_handler(on_message_received)

    # Wait a bit for WebSocket to connect
    await asyncio.sleep(1)

    # Example 2: Get friends list
    print("2. Getting friends list...")
    friends = await network.get_friends(token)
    print(f"   Found {len(friends)} friend(s):")
    for friend in friends:
        print(f"   - {friend['username']} (ID: {friend['id']})")
    print()

    # Example 3: Get agents for a friend
    if friends:
        friend = friends[0]
        print(f"3. Getting agents for friend '{friend['username']}'...")
        agents = await network.get_agents(friend["id"], token)
        print(f"   Found {len(agents)} agent(s):")
        for agent in agents:
            print(f"   - {agent['name']}: {agent['description']}")
        print()

        # Example 4: Send a message to friend
        print(f"4. Sending a message to {friend['username']}'s assistant...")

        # Create a network fragment
        fragment = NetworkFragment(
            name="greeting",
            kind=FragmentKindSerializable(
                name="text",
                content={"text": "Hello! How are you doing today?"},
                description="A friendly greeting message",
            ),
            description="Greeting message",
            source=FragmentSource.USER,
        )

        # Create a network message
        message = NetworkMessage(
            sender="alice_assistant",
            sender_client=login_result["user"]["id"],
            recipient=f"{friend['username']}_assistant",
            recipient_client=friend["id"],
            fragments=[fragment],
            message_type=MessageType.PROPOSAL,
            context={"conversation_id": "example_001"},
        )

        # Send the message
        send_result = await network.send_message(message)
        if send_result.get("success"):
            print(f"   ✓ Message sent successfully!")
            print(f"   Message ID: {send_result.get('message_id')}\n")
        else:
            print(f"   ✗ Failed to send message: {send_result.get('error')}\n")

    # Example 5: Signup a new user
    print("5. Testing signup with a new user...")
    signup_result = await network.signup("test_user", "test_password")
    if signup_result.get("success"):
        print(f"   ✓ Signup successful!")
        print(f"   New user ID: {signup_result.get('user', {}).get('id')}\n")

        # Logout the new user
        new_user_client = WebSocketNetworkClient(
            base_url="http://127.0.0.1:8000",
            ws_url="ws://127.0.0.1:8000/ws",
        )
        new_user_client.token = signup_result.get("token")
        logout_result = await new_user_client.logout()
        if logout_result.get("success"):
            print("   ✓ New user logged out successfully\n")
    else:
        print(f"   Note: {signup_result.get('error')} (this is expected if user exists)\n")

    # Example 6: Send a friend request
    print("6. Sending a friend request to 'charlie'...")
    # Find charlie's username first
    charlie_username = "charlie"
    friend_request_result = await network.send_friend_request(charlie_username, token)
    if friend_request_result.get("success"):
        print(f"   ✓ Friend request sent to {charlie_username}!\n")
    else:
        print(f"   Note: {friend_request_result.get('error')}\n")

    # Keep the connection alive for a bit to receive any incoming messages
    print("7. Keeping connection alive for 5 seconds to receive messages...")
    await asyncio.sleep(5)

    # Logout
    print("\n8. Logging out...")
    logout_result = await client.logout()
    if logout_result.get("success"):
        print("   ✓ Logged out successfully!")

    print("\n=== Example Complete ===")


async def main() -> None:
    """Run the example."""
    try:
        await example_usage()
    except KeyboardInterrupt:
        print("\n\nExample interrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")


if __name__ == "__main__":
    asyncio.run(main())
