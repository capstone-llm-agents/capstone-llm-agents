"""Simple test to verify the network server setup.

This script can be used to quickly test if all the components are working.
"""

import asyncio

from network_server.local_server import LocalServer
from network_server.network import Network
from network_server.websocket_client import WebSocketNetworkClient


async def test_client() -> None:
    """Test the client connection."""
    await asyncio.sleep(2)  # Wait for server to start

    client = WebSocketNetworkClient()
    network = Network(client)

    # Test login
    result = await network.login("alice", "password123")
    assert result.get("success"), f"Login failed: {result}"
    print("✓ Login successful")

    # Test getting friends
    token = result["token"]
    friends = await network.get_friends(token)
    assert len(friends) > 0, "No friends found"
    print(f"✓ Found {len(friends)} friends")

    # Test logout
    await client.logout()
    print("✓ Logout successful")

    print("\nAll tests passed! ✓")


def run_server_in_background() -> None:
    """Run the server in a separate thread."""
    import threading

    import uvicorn

    server = LocalServer()

    def start_server() -> None:
        uvicorn.run(server.app, host="127.0.0.1", port=8000, log_level="error")

    thread = threading.Thread(target=start_server, daemon=True)
    thread.start()


async def main() -> None:
    """Run the test."""
    print("Starting server test...")
    print("-" * 40)

    # Start server in background
    run_server_in_background()

    try:
        await test_client()
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
