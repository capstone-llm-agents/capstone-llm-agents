"""PyQt6 MCP Client Info Screen."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QTextEdit, QComboBox
from llm_mas.client.account.client import Client
from llm_mas.mcp_client.connected_server import SSEConnectedServer, HTTPConnectedServer
from llm_mas.logging.loggers import APP_LOGGER

class MCPClientScreen(QWidget):
    """PyQt6 MCP Client Info Screen."""

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

        # Server type dropdown
        type_label = QLabel("Server Type:")
        layout.addWidget(type_label)
        self.server_type = QComboBox()
        self.server_type.addItems(["SSE", "HTTP"])
        layout.addWidget(self.server_type)

        # Server URL input
        url_label = QLabel("Server URL:")
        layout.addWidget(url_label)
        self.server_input = QLineEdit()
        self.server_input.setPlaceholderText("Enter server URL")
        self.server_input.setText("http://localhost:8080/sse")
        layout.addWidget(self.server_input)

        # Auth token input
        token_label = QLabel("Auth Token (optional):")
        layout.addWidget(token_label)
        self.auth_token_input = QLineEdit()
        self.auth_token_input.setPlaceholderText("Enter auth token (leave empty if not needed)")
        layout.addWidget(self.auth_token_input)

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
            server_type = "SSE" if isinstance(server, SSEConnectedServer) else "HTTP"
            auth_status = "with auth" if server.headers.get("Authorization") else "no auth"
            content += f"- [{server_type}] {server.server_url} ({auth_status})\n"
        self.server_info.setText(content)

    def _on_add_server(self):
        url = self.server_input.text().strip()
        auth_token = self.auth_token_input.text().strip() or None
        server_type = self.server_type.currentText()
        
        if not url:
            self.error_label.setText("Enter a valid URL")
            return

        if any(s.server_url == url for s in self.client.mcp_client.connected_servers):
            self.error_label.setText("Server already added")
            return

        try:
            if server_type == "SSE":
                server = SSEConnectedServer(url, auth_token)
            else:  # HTTP
                server = HTTPConnectedServer(url, auth_token)
            
            self.client.mcp_client.add_connected_server(server)
            self.error_label.setText("")
            self._load_server_info()
            # Clear inputs after successful add
            self.server_input.clear()
            self.auth_token_input.clear()
        except Exception as e:
            self.error_label.setText(f"Error adding server: {e}")
            APP_LOGGER.exception(f"Failed to add server: {e}")
