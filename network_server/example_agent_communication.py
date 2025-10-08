"""Example demonstrating cross-network agent communication.

This script shows how to set up two clients that can send messages
between their agents using the NetworkMessage/NetworkFragment system.
"""

import asyncio
import logging

from llm_mas.client.account.client import Client
from llm_mas.communication.message_types import MessageType
from network_server.network_client import NetworkClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_agent_communication():
    """Demonstrate agent-to-agent communication across the network."""
    
    # Assume we have two clients already set up (Alice and Bob)
    # In a real scenario, these would be created with full MAS, agents, etc.
    
    # Client 1: Alice
    alice_client = NetworkClient()
    
    # Client 2: Bob  
    bob_client = NetworkClient()
    
    try:
        # Step 1: Authenticate both clients
        logger.info("Authenticating Alice...")
        alice_success = await alice_client.login("alice", "password123")
        if not alice_success:
            logger.error("Alice login failed")
            return
            
        logger.info("Authenticating Bob...")
        bob_success = await bob_client.login("bob", "password123")
        if not bob_success:
            logger.error("Bob login failed")
            return
        
        # Step 2: Set up message routing (if using full Client class)
        # alice_full_client.setup_message_routing()
        # bob_full_client.setup_message_routing()
        
        # Step 3: Get friend list and verify friendship
        logger.info("Getting Alice's friends...")
        alice_friends = await alice_client.get_friends(alice_client.token)
        logger.info(f"Alice's friends: {alice_friends}")
        
        # Find Bob's user ID
        bob_user = next((f for f in alice_friends if f["username"] == "bob"), None)
        if not bob_user:
            logger.error("Bob is not Alice's friend")
            return
        
        bob_user_id = bob_user["id"]
        
        # Step 4: Get Bob's agents
        logger.info(f"Getting Bob's agents...")
        bob_agents = await alice_client.get_agents(bob_user_id, alice_client.token)
        logger.info(f"Bob's agents: {bob_agents}")
        
        # Step 5: Send a message from Alice's assistant to Bob's assistant
        logger.info("Sending PROPOSAL message from Alice to Bob...")
        
        # Using the high-level API
        success = await alice_client.send_text_message(
            recipient_id=bob_user_id,
            recipient_agent="assistant",
            text="Hi Bob! Can you help me plan a trip to New York?",
            message_type=MessageType.PROPOSAL,
            sender_agent="assistant",
        )
        
        if success:
            logger.info("Message sent successfully!")
        else:
            logger.error("Failed to send message")
        
        # Step 6: Wait a bit for message to be processed
        await asyncio.sleep(2)
        
        # Step 7: Send a QUERY message
        logger.info("Sending QUERY message from Alice to Bob...")
        success = await alice_client.send_text_message(
            recipient_id=bob_user_id,
            recipient_agent="calendar",
            text="What's on your calendar for next week?",
            message_type=MessageType.QUERY,
            sender_agent="assistant",
        )
        
        if success:
            logger.info("Query sent successfully!")
        
        # Wait for potential responses
        await asyncio.sleep(2)
        
    finally:
        # Cleanup
        logger.info("Logging out...")
        await alice_client.logout()
        await bob_client.logout()


async def example_with_custom_fragments():
    """Example showing how to send messages with custom fragments."""
    
    from network_server.network_fragment import (
        FragmentKindSerializable,
        FragmentSource,
        NetworkFragment,
    )
    
    client = NetworkClient()
    
    try:
        # Login
        await client.login("alice", "password123")
        
        # Get Bob's user ID (assume they're friends)
        friends = await client.get_friends(client.token)
        bob = next((f for f in friends if f["username"] == "bob"), None)
        
        if not bob:
            logger.error("Bob not found in friends list")
            return
        
        # Create custom fragments
        fragments = [
            NetworkFragment(
                name="greeting",
                kind=FragmentKindSerializable(
                    name="text",
                    content={"text": "Hello from Alice!"},
                    description="Greeting message",
                ),
                source=FragmentSource.USER,
            ),
            NetworkFragment(
                name="task_detail",
                kind=FragmentKindSerializable(
                    name="text",
                    content={"text": "I need help booking a flight to NYC"},
                    description="Task description",
                ),
                source=FragmentSource.USER,
            ),
        ]
        
        # Send with custom fragments
        success = await client.send_message(
            recipient_id=bob["id"],
            recipient_agent="travel",
            fragments=fragments,
            message_type=MessageType.TASK,
            sender_agent="assistant",
            context={"task_description": "Book flight to NYC"},
        )
        
        if success:
            logger.info("Custom message sent successfully!")
            
    finally:
        await client.logout()


if __name__ == "__main__":
    logger.info("Starting agent communication example...")
    
    # Run the basic example
    asyncio.run(example_agent_communication())
    
    # Uncomment to run the custom fragments example
    # asyncio.run(example_with_custom_fragments())
