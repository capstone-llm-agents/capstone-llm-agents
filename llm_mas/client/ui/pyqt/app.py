"""PyQt6 application with full screen navigation and proper QStackedWidget setup."""
from pathlib import Path
import asyncio
import os
import sys

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication, QStackedWidget
from qasync import QEventLoop

from components.agents.assistant_agent import ASSISTANT_AGENT
from components.agents.calendar_agent import CALENDAR_AGENT
from components.agents.github_agent import GITHUB_AGENT
from components.agents.weather_agent import WEATHER_AGENT
from components.agents.websearch_agent import WEBSEARCH_AGENT
from components.agents.travel_planner_agent import TRAVEL_PLANNER_AGENT
from components.agents.pdf_agent import PDF_AGENT
from llm_mas.client.account.client import Client
from llm_mas.client.ui.pyqt.screens.agent_network_screen import AgentNetworkScreen
from llm_mas.client.ui.pyqt.screens.conversation_screen import ConversationsScreen
from llm_mas.client.ui.pyqt.screens.friends_screen import FriendsScreen
from llm_mas.client.ui.pyqt.screens.login_screen import LoginScreen
from llm_mas.client.ui.pyqt.screens.main_menu import MainMenu
from llm_mas.client.ui.pyqt.screens.mcp_client import MCPClientScreen
from llm_mas.client.ui.pyqt.screens.upload_screen import UploadScreen
from llm_mas.client.ui.pyqt.screens.user_chat_screen import UserChatScreen
from llm_mas.logging.loggers import APP_LOGGER
from llm_mas.mas.agentstate import State
from llm_mas.mas.checkpointer import CheckPointer
from llm_mas.mas.mas import MAS
from llm_mas.mcp_client.client import MCPClient
from llm_mas.mcp_client.connected_server import HTTPConnectedServer, SSEConnectedServer
from llm_mas.utils.background_tasks import BACKGROUND_TASKS
from llm_mas.utils.config.general_config import GENERAL_CONFIG
from network_server.client import NetworkClient


class NavigationManager(QObject):
    """Signal manager to handle navigation requests between screens."""

    navigate = pyqtSignal(str, object)  # screen_name, payload


class PyQtApp(QStackedWidget):
    """Main PyQt application class with navigation and screen management."""

    def __init__(self, client: Client, checkpoint: CheckPointer, show_login=True) -> None:
        """Initialize the main application with client and navigation."""
        super().__init__()
        self.client = client
        self.network_client = None

        if client:
            self.checkpoint = checkpoint
            self.setWindowTitle(f"Welcome Back - {client.get_username()}")
        else:
            self.setWindowTitle("LLM Multi-Agent System")

        # Navigation manager
        self.nav = NavigationManager()
        self.nav.navigate.connect(self._navigate)

        # Screens cache
        self.screens = {}

        # Show login screen first if requested
        if show_login and not client:
            self.login_screen = LoginScreen()
            self.login_screen.login_successful.connect(self._on_login_success)
            self._add_screen("login", self.login_screen)
            self.setCurrentWidget(self.login_screen)
        else:
            # Instantiate MainMenu with nav
            self.main_menu = MainMenu(client, checkpoint, nav=self.nav)
            self._add_screen("main_menu", self.main_menu)
            # Show main menu initially
            self.setCurrentWidget(self.main_menu)

        self.resize(900, 600)

    def _on_login_success(self, network_client: NetworkClient):
        """Handle successful login - create Client and show main menu."""
        self.network_client = network_client

        if network_client:
            # Use network username
            username = network_client.username if hasattr(network_client, "username") else "Network User"
        else:
            # Offline mode
            username = "Offline User"

        # Initialize MAS and agents
        mas = MAS()
        mas.add_agent(ASSISTANT_AGENT)
        mas.add_agent(GITHUB_AGENT)
        mas.add_agent(CALENDAR_AGENT)
        mas.add_agent(WEATHER_AGENT)
        mas.add_agent(WEBSEARCH_AGENT)
        mas.add_agent(TRAVEL_PLANNER_AGENT)
        mas.add_agent(PDF_AGENT)

        # Setup MCP client
        mcp_client = MCPClient()
        server1 = SSEConnectedServer("http://localhost:8080/sse")
        server2 = SSEConnectedServer("http://localhost:8081/sse")
        server3 = SSEConnectedServer("http://localhost:8082/sse")
        mcp_client.add_connected_server(server1)
        mcp_client.add_connected_server(server2)
        mcp_client.add_connected_server(server3)

        # test github server
        github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")

        if not github_token:
            APP_LOGGER.warning("GITHUB_PERSONAL_ACCESS_TOKEN not set in environment variables.")
        else:
            github_server = HTTPConnectedServer("https://api.githubcopilot.com/mcp", auth_token=github_token)
            mcp_client.add_connected_server(github_server)

        # Setup agent friendships
        ASSISTANT_AGENT.add_friend(WEATHER_AGENT)
        ASSISTANT_AGENT.add_friend(CALENDAR_AGENT)
        ASSISTANT_AGENT.add_friend(WEBSEARCH_AGENT)
        ASSISTANT_AGENT.add_friend(TRAVEL_PLANNER_AGENT)
        ASSISTANT_AGENT.add_friend(PDF_AGENT)

        # Create the client with the logged-in user
        self.client = Client(username, mas, mcp_client, GENERAL_CONFIG)
        self.setWindowTitle(f"Welcome Back - {username}")

        # Store network client in application client if available
        if network_client:
            self.client.network_client = network_client

        # Setup user friendships
        self.client.user.add_friend(ASSISTANT_AGENT)

        # Create checkpoint if not exists
        if not hasattr(self, "checkpoint") or self.checkpoint is None:
            checkpointing_path = Path(__file__).parent.parent.parent.parent.parent.joinpath("db").joinpath("checkpoint.sqlite3")
            APP_LOGGER.info(checkpointing_path)
            self.checkpoint = CheckPointer(str(checkpointing_path))

        # Create and show main menu
        self.main_menu = MainMenu(self.client, self.checkpoint, nav=self.nav)
        self._add_screen("main_menu", self.main_menu)
        self.setCurrentWidget(self.main_menu)

    def _add_screen(self, name: str, widget):
        """Add a screen to the stacked widget and cache it."""
        self.screens[name] = widget
        self.addWidget(widget)

    def closeEvent(self, event) -> None:
        """Now only saves conversation on exiting the application since the memory is alread
        stored in memory
        """
        try:
            conversations = self.client.mas.conversation_manager.get_all_conversations()
            for conversation in conversations:
                if conversation.name == "User Assistant Chat":
                    message = conversation.get_chat_history()
                    state: State = {"messages": message.as_dicts()}
                    self.checkpoint.save(state)
            APP_LOGGER.info("User Assistant Chat Saved")
        except Exception as e:
            APP_LOGGER.info(f"Client wasn't initialized: {e}")
        finally:
            event.accept()

    def _navigate(self, screen_name: str, payload=None):
        """Handle navigation requests to switch screens."""
        APP_LOGGER.info(f"Navigate to {screen_name} with payload {payload}")

        if screen_name in self.screens:
            screen = self.screens[screen_name]
        else:
            # Dynamically create screens
            if screen_name == "mcp_client":
                screen = MCPClientScreen(self.client, self.nav)
            elif screen_name == "user_chat":
                conversation = payload.get("conversation") if payload else None
                screen = UserChatScreen(self.client, conversation, self.checkpoint, nav=self.nav)
            elif screen_name == "conversations":
                conversations = self.client.mas.conversation_manager.get_all_conversations()
                screen = ConversationsScreen(self.client, self.nav, conversations)
            elif screen_name == "agent_network":
                screen = AgentNetworkScreen(self.client, self.nav)
            elif screen_name == "friends":
                screen = FriendsScreen(self.client, self.nav)
            elif screen_name == "upload_kb":
                screen = UploadScreen(self.client, self.nav)
            else:
                APP_LOGGER.error(f"Unknown screen requested: {screen_name}")
                return
            self._add_screen(screen_name, screen)

        self.setCurrentWidget(screen)

    async def shutdown(self):
        """Cancel background tasks gracefully."""
        APP_LOGGER.info("Shutting down application, cancelling background tasks...")
        for task in list(BACKGROUND_TASKS):
            if not task.done():
                task.cancel()
        if BACKGROUND_TASKS:
            await asyncio.gather(*BACKGROUND_TASKS, return_exceptions=True)


def run_app(client, checkpoint):
    """Run the PyQt6 application with asyncio event loop."""
    app = QApplication(sys.argv)

    with open("llm_mas/client/ui/pyqt/styles.qss") as f:
        qss = f.read()
        app.setStyleSheet(qss)

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = PyQtApp(client, checkpoint)
    window.show()

    with loop:
        try:
            loop.run_forever()
        finally:
            loop.run_until_complete(window.shutdown())
