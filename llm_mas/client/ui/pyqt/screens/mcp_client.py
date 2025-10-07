# mcp_client_screen.py (PyQt6 version)
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QTextEdit
from llm_mas.client.account.client import Client
from llm_mas.mcp_client.connected_server import SSEConnectedServer
from llm_mas.logging.loggers import APP_LOGGER

class MCPClientScreen(QWidget):
    """PyQt6 MCP Client Info Screen"""

    def __init__(self, client: Client, nav: QWidget):
        super().__init__()
        self.client = client
        self.nav = nav

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Top bar with back button
        top_bar = QHBoxLayout()
        self.back_btn = QPushButton("← Back")
        self.back_btn.clicked.connect(lambda: self.nav.navigate.emit("main_menu", None))
        top_bar.addWidget(self.back_btn)
        top_bar.addStretch()
        layout.addLayout(top_bar)

        self.server_info = QTextEdit()
        self.server_info.setReadOnly(True)
        layout.addWidget(self.server_info)

        self.server_input = QLineEdit()
        self.server_input.setPlaceholderText("Enter server URL")
        self.server_input.setText("http://localhost:8080/sse")
        layout.addWidget(self.server_input)

        self.add_btn = QPushButton("Add Server")
        layout.addWidget(self.add_btn)
        self.add_btn.clicked.connect(self._on_add_server)

        self.error_label = QLabel("")
        layout.addWidget(self.error_label)

        self._load_server_info()

    def _load_server_info(self):
        mcp_client = self.client.mcp_client
        content = f"Connected Servers: {len(mcp_client.connected_servers)}\n"
        for server in mcp_client.connected_servers:
            content += f"- {server.server_url}\n"
        self.server_info.setText(content)

    def _on_add_server(self):
        url = self.server_input.text().strip()
        if not url:
            self.error_label.setText("Enter a valid URL")
            return

        if any(s.server_url == url for s in self.client.mcp_client.connected_servers):
            self.error_label.setText("Server already added")
            return

        try:
            server = SSEConnectedServer(url)
            self.client.mcp_client.add_connected_server(server)
            self.error_label.setText("")
            self._load_server_info()
        except Exception as e:
            self.error_label.setText(f"Error adding server: {e}")
            APP_LOGGER.exception(f"Failed to add server: {e}")
