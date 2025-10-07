"""PyQt6 application with full screen navigation and proper QStackedWidget setup."""

import asyncio
import sys

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication, QStackedWidget
from qasync import QEventLoop

from llm_mas.client.account.client import Client
from llm_mas.client.ui.pyqt.screens.agent_network_screen import AgentNetworkScreen
from llm_mas.client.ui.pyqt.screens.conversation_screen import ConversationsScreen
from llm_mas.client.ui.pyqt.screens.main_menu import MainMenu
from llm_mas.client.ui.pyqt.screens.mcp_client import MCPClientScreen
from llm_mas.client.ui.pyqt.screens.upload_screen import UploadScreen
from llm_mas.client.ui.pyqt.screens.user_chat_screen import UserChatScreen
from llm_mas.logging.loggers import APP_LOGGER
from llm_mas.utils.background_tasks import BACKGROUND_TASKS


class NavigationManager(QObject):
    """Signal manager to handle navigation requests between screens."""

    navigate = pyqtSignal(str, object)  # screen_name, payload


class PyQtApp(QStackedWidget):
    """Main PyQt application class with navigation and screen management."""

    def __init__(self, client: Client) -> None:
        """Initialize the main application with client and navigation."""
        super().__init__()
        self.client = client
        self.setWindowTitle(f"Welcome Back - {client.get_username()}")

        # Navigation manager
        self.nav = NavigationManager()
        self.nav.navigate.connect(self._navigate)

        # Screens cache
        self.screens = {}

        # Instantiate MainMenu with nav
        self.main_menu = MainMenu(client, nav=self.nav)
        self._add_screen("main_menu", self.main_menu)

        # Show main menu initially
        self.setCurrentWidget(self.main_menu)
        self.resize(900, 600)

    def _add_screen(self, name: str, widget):
        """Add a screen to the stacked widget and cache it."""
        self.screens[name] = widget
        self.addWidget(widget)

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
                screen = UserChatScreen(self.client, conversation, nav=self.nav)
            elif screen_name == "conversations":
                conversations = self.client.mas.conversation_manager.get_all_conversations()
                screen = ConversationsScreen(self.client, self.nav, conversations)
            elif screen_name == "agent_network":
                screen = AgentNetworkScreen(self.client, self.nav)
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


def run_app(client):
    """Run the PyQt6 application with asyncio event loop."""
    app = QApplication(sys.argv)

    with open("llm_mas/client/ui/pyqt/styles.qss") as f:
        qss = f.read()
        app.setStyleSheet(qss)

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = PyQtApp(client)
    window.show()

    with loop:
        try:
            loop.run_forever()
        finally:
            loop.run_until_complete(window.shutdown())
