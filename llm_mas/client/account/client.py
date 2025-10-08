"""The client module defines the client account functionality for the MAS."""

import asyncio
import logging

from llm_mas.logging.loggers import APP_LOGGER
from llm_mas.mas.agent import Agent
from llm_mas.mas.mas import MAS
from llm_mas.mas.user import User
from llm_mas.mcp_client.client import MCPClient
from llm_mas.utils.config.general_config import GeneralConfig
from network_server.message_router import MessageRouter
from network_server.network_client import NetworkClient

logger = logging.getLogger(__name__)


class Client:
    """The Client class represents a user account in the MAS."""

    def __init__(self, username: str, mas: MAS, mcp_client: MCPClient, config: GeneralConfig) -> None:
        """Initialize the client with a username."""
        self.mas = mas
        self.mcp_client = mcp_client
        self.user = User(name=username, description="A user of the multi-agent system.")
        self.config = config

        self.network_client = None

        # Message router will be initialized after network client is connected
        self.message_router: MessageRouter | None = None

        # Background tasks for handling incoming messages
        self.background_tasks: set[asyncio.Task] = set()

    def setup_message_routing(self) -> None:
        """Set up message routing after network client is authenticated.

        This should be called after successful login/signup to enable
        agents to receive messages from the network.
        """
        print("Setting up message routing...")
        if self.message_router is None:
            print("Initializing message router...")
            self.message_router = MessageRouter(self)
            # Register the message router as a handler for incoming messages
            self.network_client.add_message_handler(
                lambda msg: self._handle_network_message_sync(msg),
            )

    def _handle_network_message_sync(self, message_data: dict) -> None:
        """Handle incoming network messages synchronously.

        Wraps the async message handling in a way that works with
        the synchronous callback interface.

        Args:
            message_data: The incoming message data from the network

        """
        APP_LOGGER.debug(f"Client received network message: {message_data}")
        print(f"Client received network message: {message_data}")
        if not self.message_router:
            logger.warning("Message router not initialized, ignoring message")
            return

        # Create async task to handle the message
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, schedule as a task
                task = asyncio.create_task(
                    self.message_router.handle_incoming_network_message(message_data),
                )
                self.background_tasks.add(task)
                task.add_done_callback(self.background_tasks.discard)
            else:
                # If no loop is running, run it directly
                loop.run_until_complete(
                    self.message_router.handle_incoming_network_message(message_data),
                )
        except RuntimeError:
            # No event loop exists, create a new one
            asyncio.run(self.message_router.handle_incoming_network_message(message_data))

    def get_username(self) -> str:
        """Return the username of the client."""
        return self.user.get_name()

    def get_mas(self) -> MAS:
        """Return the MAS instance associated with the client."""
        return self.mas

    def add_agent(self, agent: Agent) -> None:
        """Add an agent to the MAS associated with the client."""
        self.mas.add_agent(agent)

    def get_agents(self) -> list[Agent]:
        """Return the list of agents in the MAS associated with the client."""
        return self.mas.get_agents()

    def get_assistant_agent(self) -> Agent | None:
        """Return the assistant agent in the MAS associated with the client."""
        return self.mas.get_assistant_agent()

    def get_discovery_agent(self) -> Agent | None:
        """Return the discovery agent in the MAS associated with the client."""
        return self.mas.get_discovery_agent()
