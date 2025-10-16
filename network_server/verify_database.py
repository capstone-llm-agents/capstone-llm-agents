"""Verify that the database migration is working correctly.

This script tests the database functionality without starting the full server.
"""

import os
import sqlite3
from pathlib import Path

from network_server.local_server import LocalServer


def verify_database() -> None:
    """Verify database setup and test data."""
    print("🔍 Verifying Network Server Database Setup\n")
    print("-" * 50)

    # Initialize server (creates database)
    print("\n1. Initializing server...")
    server = LocalServer()
    print("   ✓ Server initialized")

    # Check database file exists
    print("\n2. Checking database file...")
    db_path = Path(__file__).parent.parent / "db" / "network.sqlite3"
    if db_path.exists():
        size = db_path.stat().st_size
        print(f"   ✓ Database exists at: {db_path}")
        print(f"   ✓ Size: {size:,} bytes")
    else:
        print(f"   ✗ Database not found at: {db_path}")
        return

    # Connect and verify schema
    print("\n3. Verifying database schema...")
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]

    expected_tables = ["users", "tokens", "friends", "friend_requests", "agents", "message_queue"]
    for table in expected_tables:
        if table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   ✓ Table '{table}' exists ({count} rows)")
        else:
            print(f"   ✗ Table '{table}' missing")

    # Verify test data
    print("\n4. Verifying test users...")
    cursor.execute("SELECT username FROM users ORDER BY username")
    users = [row[0] for row in cursor.fetchall()]

    expected_users = ["alice", "bob", "charlie"]
    for user in expected_users:
        if user in users:
            print(f"   ✓ User '{user}' exists")
        else:
            print(f"   ✗ User '{user}' missing")

    # Verify friendships
    print("\n5. Verifying friendships...")
    cursor.execute("""
        SELECT u1.username, u2.username
        FROM friends f
        JOIN users u1 ON f.user_id = u1.id
        JOIN users u2 ON f.friend_id = u2.id
        ORDER BY u1.username, u2.username
    """)
    friendships = cursor.fetchall()
    print(f"   ✓ Found {len(friendships)} friendship records:")
    for user1, user2 in friendships:
        print(f"     - {user1} ↔ {user2}")

    # Verify agents
    print("\n6. Verifying agents...")
    cursor.execute("""
        SELECT u.username, a.name
        FROM agents a
        JOIN users u ON a.user_id = u.id
        ORDER BY u.username, a.name
    """)
    agents = cursor.fetchall()
    print(f"   ✓ Found {len(agents)} agents:")
    for username, agent_name in agents:
        print(f"     - {username}: {agent_name}")

    conn.close()

    print("\n" + "-" * 50)
    print("✅ Database verification complete!\n")


if __name__ == "__main__":
    verify_database()
