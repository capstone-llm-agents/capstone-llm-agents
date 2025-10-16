"""Run the network server.

This module provides a simple way to run the local network server for testing.
The server supports:
- User authentication (login/signup/logout)
- Friend management (add friends, accept friend requests)
- Agent discovery (list friends' agents)
- Message sending via HTTP
- Real-time WebSocket communication
"""

import argparse
import sys


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Run the local network server.

    Args:
        host: The host to bind the server to
        port: The port to bind the server to

    """
    from network_server.local_server import LocalServer

    print(f"Starting local network server on {host}:{port}")
    print(f"HTTP endpoints available at: http://{host}:{port}")
    print(f"WebSocket endpoint available at: ws://{host}:{port}/ws")
    print("\nTest users available:")
    print("  - alice / password123")
    print("  - bob / password123")
    print("  - charlie / password123")
    print("\nPress Ctrl+C to stop the server\n")

    server = LocalServer()
    server.run(host=host, port=port)


def main() -> None:
    """Main entry point for running the server."""
    parser = argparse.ArgumentParser(description="Run the local network server")
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind the server to (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server to (default: 8000)",
    )

    args = parser.parse_args()

    try:
        run_server(host=args.host, port=args.port)
    except KeyboardInterrupt:
        print("\nShutting down server...")
        sys.exit(0)


if __name__ == "__main__":
    main()
