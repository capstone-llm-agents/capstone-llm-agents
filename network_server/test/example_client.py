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

# Global flag to track if messages were received
messages_received = []


def on_message_received(message: dict) -> None:
    """Handle incoming messages from the WebSocket.

    Args:
        message: The received message data

    """
    print(f"\n{'=' * 60}")
    print(f"[✓ MESSAGE RECEIVED]")
    print(f"{'=' * 60}")
    print(f"Message Type: {message.get('type', 'unknown')}")
    print(f"Content: {message}")
    print(f"{'=' * 60}\n")
    messages_received.append(message)


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
    print("7. Testing message receive functionality...")
    print("   Creating a second client as 'bob' to send a message to alice...\n")

    # Create a second client to send a message to alice
    sender_client = WebSocketNetworkClient(
        base_url="http://127.0.0.1:8000",
        ws_url="ws://127.0.0.1:8000/ws",
    )
    sender_network = Network(sender_client)

    # Login as bob
    print("   Logging in as 'bob'...")
    bob_login = await sender_network.login("bob", "password123")
    if bob_login.get("success"):
        print(f"   ✓ Bob logged in successfully!")
        bob_token = bob_login.get("token")
        bob_user_id = bob_login.get("user", {}).get("id")
        alice_user_id = login_result.get("user", {}).get("id")

        # Wait a moment for WebSocket to connect
        await asyncio.sleep(1)

        # Create a test message from bob to alice
        print(f"   Sending test message from bob to alice...\n")
        test_fragment = NetworkFragment(
            name="test_message",
            kind=FragmentKindSerializable(
                name="text",
                content={"text": "Hi Alice! This is a test message from Bob."},
                description="Test message for receive functionality",
            ),
            description="Test message",
            source=FragmentSource.USER,
        )

        test_message = NetworkMessage(
            sender="bob_assistant",
            sender_client=bob_user_id,
            recipient="alice_assistant",
            recipient_client=alice_user_id,
            fragments=[test_fragment],
            message_type=MessageType.PROPOSAL,
            context={"conversation_id": "test_receive_001"},
        )

        # Send the message from bob to alice
        send_result = await sender_network.send_message(test_message)
        if send_result.get("success"):
            print(f"   ✓ Test message sent from bob to alice!")
            print(f"   Message ID: {send_result.get('message_id')}\n")
        else:
            print(f"   ✗ Failed to send test message: {send_result.get('error')}\n")

        # Logout bob
        await sender_client.logout()
        print("   ✓ Bob logged out\n")
    else:
        print(f"   ✗ Bob login failed: {bob_login.get('error')}\n")

    # Now wait for alice to receive the message
    print("   Waiting for 5 seconds for alice to receive the message...")
    print("   (Messages will be displayed with '✓ MESSAGE RECEIVED' banner)\n")

    initial_message_count = len(messages_received)
    print("   (Messages will be displayed with '✓ MESSAGE RECEIVED' banner)\n")
    await asyncio.sleep(5)

    # Check if any messages were received
    new_messages_count = len(messages_received) - initial_message_count
    if new_messages_count > 0:
        print(f"\n   ✓ SUCCESS: Received {new_messages_count} message(s) during the wait period!")
    else:
        print("\n   ✗ WARNING: No messages were received during the wait period.")
        print("   This may indicate an issue with the WebSocket connection or message routing.")

    print(f"\n   Total messages received during this session: {len(messages_received)}")

    # Logout
    print("\n8. Logging out...")
    logout_result = await client.logout()
    if logout_result.get("success"):
        print("   ✓ Logged out successfully!")

    print("\n=== Example Complete ===")
    print(f"=== Total Messages Received: {len(messages_received)} ===")


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
