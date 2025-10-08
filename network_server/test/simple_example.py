"""Simple usage example using the high-level NetworkClient.

This demonstrates the easiest way to use the network server.
"""

import asyncio

from network_server.network_client import NetworkClient
from network_server.message import MessageType


async def simple_example() -> None:
    """Simple example of using the NetworkClient."""
    # Create a client
    client = NetworkClient()

    print("=== Simple Network Client Example ===\n")

    # Login
    print("1. Logging in as 'alice'...")
    success = await client.login("alice", "password123")
    if success:
        print(f"   ✓ Logged in as {client.username} (ID: {client.user_id})\n")
    else:
        print("   ✗ Login failed\n")
        return

    # Get friends
    print("2. Getting friends...")
    friends = await client.get_friends()
    print(f"   Found {len(friends)} friend(s):")
    for friend in friends:
        print(f"   - {friend['username']}")
    print()

    # Get agents for first friend
    if friends:
        friend = friends[0]
        print(f"3. Getting agents for {friend['username']}...")
        agents = await client.get_agents(friend["id"])
        print(f"   Found {len(agents)} agent(s):")
        for agent in agents:
            print(f"   - {agent['name']}: {agent['description']}")
        print()

        # Send a simple text message
        print(f"4. Sending a text message to {friend['username']}'s assistant...")
        success = await client.send_text_message(
            recipient_id=friend["id"],
            recipient_agent="assistant",
            text="Hi! This is a test message from the simple example.",
            message_type=MessageType.PROPOSAL,
        )
        if success:
            print("   ✓ Message sent successfully!\n")
        else:
            print("   ✗ Failed to send message\n")

    # Logout
    print("5. Logging out...")
    success = await client.logout()
    if success:
        print("   ✓ Logged out successfully\n")

    print("=== Example Complete ===")


if __name__ == "__main__":
    asyncio.run(simple_example())
