"""The MCP client screen of the textual app."""

from textual import events
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Static

from llm_mas.client.account.client import Client
from llm_mas.logging.loggers import APP_LOGGER
from llm_mas.mcp_client.connected_server import SSEConnectedServer


class MCPClientScreen(Screen):
    """Screen to display MCP client information."""

    CSS_PATH = "../styles/mcp.tcss"

    def __init__(self, client: Client) -> None:
        """Initialize the MCP client screen with a client."""
        super().__init__()
        self.client = client
        self.server_info_widget: Static | None = None
        self.error_display: Static | None = None

    def compose(self) -> ComposeResult:
        """Compose the MCP client layout."""
        yield Header(name="MCP Client Info")

        mcp_client = self.client.mcp_client
        initial_content = f"Connected Servers: {len(mcp_client.connected_servers)}\nLoading server details..."

        self.server_info_widget = Static(initial_content, classes="mcp-client-info")
        yield self.server_info_widget

        # text input and button to add a new server
        with Horizontal(classes="mcp-add-server"):
            value = "http://localhost:8080/sse"
            self.server_input = Input(value=value, placeholder="Enter server URL", id="server_input")
            yield self.server_input
        yield Button("Add Server", id="add_server_button")

        # error display widget
        self.error_display = Static("", classes="error-display")
        yield self.error_display

        yield Footer()

    async def on_mount(self) -> None:
        """Load server information after the screen is mounted."""
        await self._load_server_info()

    def _show_error(self, message: str) -> None:
        """Display an error message below the input."""
        if self.error_display:
            self.error_display.update(message)
            self.error_display.add_class("visible")

    def _clear_error(self) -> None:
        """Clear any displayed error message."""
        if self.error_display:
            self.error_display.update("")
            self.error_display.remove_class("visible")

    async def _load_server_info(self) -> None:
        """Load and display server information asynchronously."""
        if not self.server_info_widget:
            return

        mcp_client = self.client.mcp_client
        content = f"Connected Servers: {len(mcp_client.connected_servers)}\n"

        server_details = ""

        for server in mcp_client.connected_servers:
            try:
                async with server.connect() as session:
                    info = await server.initialize(session)
                    server_details += f"Server URL: {server.server_url}\nName: {info.name}\n\n"
            # TODO: More specific exception handling here  # noqa: TD003
            except Exception as e:  # noqa: BLE001
                msg = f"Error connecting to server {server.server_url}: {e!s}"
                APP_LOGGER.exception(msg)
                server_details += f"({server.server_url}) Error connecting to server. Please check the URL and make sure the server is running.\n\n"  # noqa: E501

        content += server_details
        self.server_info_widget.update(content)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses to add a new server."""
        if event.button.id == "add_server_button":
            server_url = self.server_input.value.strip()

            # already have a server with this URL
            if any(server.server_url == server_url for server in self.client.mcp_client.connected_servers):
                self._show_error("Server already added.")
                return

            if server_url:
                # clear any previous error
                self._clear_error()

                try:
                    new_server = SSEConnectedServer(server_url)
                    self.server_input.value = ""

                    async with new_server.connect() as session:
                        await new_server.initialize(session)

                    self.client.mcp_client.add_connected_server(new_server)

                    await self._load_server_info()

                # TODO: More specific exception handling here  # noqa: TD003
                except Exception as e:  # noqa: BLE001
                    msg = f"Failed to add server: {e}"
                    APP_LOGGER.exception(msg)
                    self._show_error("Could not add server. Please check the URL and make sure the server is running.")

    def on_key(self, event: events.Key) -> None:
        """Handle key events for navigation."""
        if event.key == "escape":
            self.app.pop_screen()
