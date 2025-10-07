"""Friends screen for PyQt6 app - manage friends and friend requests."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from llm_mas.logging.loggers import APP_LOGGER

if TYPE_CHECKING:
    from llm_mas.client.account.client import Client
    from llm_mas.client.ui.pyqt.app import NavigationManager
    from network_server.client import NetworkClient


class FriendRequestWorker(QThread):
    """Background worker thread for handling friend requests."""

    success = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, network_client: NetworkClient, action: str, username: str) -> None:
        """Initialize the worker.

        Args:
            network_client: The NetworkClient instance for network operations
            action: Either 'send' or 'accept'
            username: The username to send/accept request to/from

        """
        super().__init__()
        self.network_client = network_client
        self.action = action
        self.username = username

    def run(self) -> None:
        """Run the friend request action in a background thread."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            if self.action == "send":
                result = loop.run_until_complete(self.network_client.send_friend_request(self.username))
                if result:
                    self.success.emit(f"Friend request sent to {self.username}")
                else:
                    self.error.emit(f"Failed to send friend request to {self.username}")
            elif self.action == "accept":
                result = loop.run_until_complete(self.network_client.accept_friend_request(self.username))
                if result:
                    self.success.emit(f"Friend request from {self.username} accepted")
                else:
                    self.error.emit(f"Failed to accept friend request from {self.username}")

            loop.close()
        except Exception as exc:
            APP_LOGGER.exception("Friend request operation failed")
            self.error.emit(f"Error: {exc!s}")


class FriendsDataWorker(QThread):
    """Background worker thread for fetching friends data."""

    data_ready = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, network_client: NetworkClient) -> None:
        """Initialize the worker.

        Args:
            network_client: The NetworkClient instance for network operations

        """
        super().__init__()
        self.network_client = network_client

    def run(self) -> None:
        """Fetch friends and pending requests in a background thread."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            friends = loop.run_until_complete(self.network_client.get_friends())
            pending_requests = loop.run_until_complete(self.network_client.get_pending_friend_requests())

            self.data_ready.emit({"friends": friends, "pending_requests": pending_requests})

            loop.close()
        except Exception as exc:
            APP_LOGGER.exception("Failed to fetch friends data")
            self.error.emit(f"Error loading data: {exc!s}")


class FriendsScreen(QWidget):
    """PyQt6 screen for managing friends and friend requests."""

    def __init__(self, client: Client, nav: NavigationManager) -> None:
        """Initialize the friends screen.

        Args:
            client: The Client instance containing user and MAS
            nav: The NavigationManager for screen navigation

        """
        super().__init__()
        self.client = client
        self.nav = nav
        self.network_client: NetworkClient | None = getattr(client, "network_client", None)
        self._worker: FriendRequestWorker | None = None
        self._data_worker: FriendsDataWorker | None = None
        self._init_ui()

        if self.network_client:
            self._load_data()
        else:
            self._show_offline_mode()

    def _init_ui(self) -> None:
        """Initialize the PyQt6 UI."""
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Header
        header_layout = QHBoxLayout()

        self.back_btn = QPushButton("← Back to Menu")
        self.back_btn.clicked.connect(self._on_back)
        self.back_btn.setStyleSheet("padding: 8px 15px;")
        header_layout.addWidget(self.back_btn)

        header_layout.addStretch()

        title = QLabel("👥 Friends")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2196F3;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self._load_data)
        self.refresh_btn.setStyleSheet("padding: 8px 15px;")
        header_layout.addWidget(self.refresh_btn)

        main_layout.addLayout(header_layout)

        # Send friend request section
        request_section = QWidget()
        request_layout = QVBoxLayout()
        request_section.setLayout(request_layout)
        request_section.setStyleSheet(
            """
            QWidget {
                background-color: #2a2a2a;
                border-radius: 10px;
                padding: 15px;
            }
        """
        )

        request_title = QLabel("📤 Send Friend Request")
        request_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        request_layout.addWidget(request_title)

        input_layout = QHBoxLayout()
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username...")
        self.username_input.setStyleSheet(
            """
            QLineEdit {
                background-color: #3a3a3a;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
        """
        )
        input_layout.addWidget(self.username_input)

        self.send_request_btn = QPushButton("Send Request")
        self.send_request_btn.clicked.connect(self._on_send_request)
        self.send_request_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """
        )
        input_layout.addWidget(self.send_request_btn)
        request_layout.addLayout(input_layout)

        main_layout.addWidget(request_section)

        # Content area with two columns
        content_layout = QHBoxLayout()

        # Pending requests section
        pending_section = QWidget()
        pending_layout = QVBoxLayout()
        pending_section.setLayout(pending_layout)
        pending_section.setStyleSheet(
            """
            QWidget {
                background-color: #2a2a2a;
                border-radius: 10px;
                padding: 15px;
            }
        """
        )

        pending_title = QLabel("📥 Pending Friend Requests")
        pending_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #FF9800;")
        pending_layout.addWidget(pending_title)

        self.pending_list = QListWidget()
        self.pending_list.setStyleSheet(
            """
            QListWidget {
                background-color: #1e1e1e;
                border: 1px solid #444;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 5px;
                margin: 2px;
            }
            QListWidget::item:hover {
                background-color: #3a3a3a;
            }
        """
        )
        pending_layout.addWidget(self.pending_list)

        content_layout.addWidget(pending_section)

        # Current friends section
        friends_section = QWidget()
        friends_layout = QVBoxLayout()
        friends_section.setLayout(friends_layout)
        friends_section.setStyleSheet(
            """
            QWidget {
                background-color: #2a2a2a;
                border-radius: 10px;
                padding: 15px;
            }
        """
        )

        friends_title = QLabel("✅ Current Friends")
        friends_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2196F3;")
        friends_layout.addWidget(friends_title)

        self.friends_list = QListWidget()
        self.friends_list.setStyleSheet(
            """
            QListWidget {
                background-color: #1e1e1e;
                border: 1px solid #444;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 5px;
                margin: 2px;
            }
            QListWidget::item:hover {
                background-color: #3a3a3a;
            }
        """
        )
        friends_layout.addWidget(self.friends_list)

        content_layout.addWidget(friends_section)

        main_layout.addLayout(content_layout)

    def _show_offline_mode(self) -> None:
        """Show message when in offline mode."""
        msg = QLabel("⚠️ Network features are not available in offline mode")
        msg.setStyleSheet("color: #FF9800; font-size: 14px; padding: 20px;")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout().addWidget(msg)

        self.send_request_btn.setEnabled(False)
        self.refresh_btn.setEnabled(False)
        self.username_input.setEnabled(False)

    def _load_data(self) -> None:
        """Load friends and pending requests data."""
        if not self.network_client:
            return

        # Disable controls while loading
        self.send_request_btn.setEnabled(False)
        self.refresh_btn.setEnabled(False)

        self._data_worker = FriendsDataWorker(self.network_client)
        self._data_worker.data_ready.connect(self._on_data_loaded)
        self._data_worker.error.connect(self._on_error)
        self._data_worker.start()

    def _on_data_loaded(self, data: dict[str, Any]) -> None:
        """Handle loaded data."""
        self._populate_friends(data.get("friends", []))
        self._populate_pending_requests(data.get("pending_requests", []))

        # Re-enable controls
        self.send_request_btn.setEnabled(True)
        self.refresh_btn.setEnabled(True)

    def _populate_friends(self, friends: list[dict[str, Any]]) -> None:
        """Populate the friends list."""
        self.friends_list.clear()

        if not friends:
            item = QListWidgetItem("No friends yet. Send a friend request to connect!")
            item.setForeground(Qt.GlobalColor.gray)
            self.friends_list.addItem(item)
            return

        for friend in friends:
            username = friend.get("username", "Unknown")
            friend_id = friend.get("id", "")

            item = QListWidgetItem(f"👤 {username}")
            item.setData(Qt.ItemDataRole.UserRole, friend_id)
            self.friends_list.addItem(item)

    def _populate_pending_requests(self, requests: list[dict[str, Any]]) -> None:
        """Populate the pending requests list."""
        self.pending_list.clear()

        if not requests:
            item = QListWidgetItem("No pending friend requests")
            item.setForeground(Qt.GlobalColor.gray)
            self.pending_list.addItem(item)
            return

        for request in requests:
            username = request.get("username", "Unknown")

            # Simple text item with the username
            item = QListWidgetItem(f"👤 {username}")
            self.pending_list.addItem(item)

            # Simple accept button item right after
            button_item = QListWidgetItem()
            self.pending_list.addItem(button_item)

            accept_btn = QPushButton("✓ Accept")
            accept_btn.setStyleSheet(
                """
                QPushButton {
                    height: 45px;
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 8px 15px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """,
            )
            accept_btn.clicked.connect(lambda checked=False, u=username: self._on_accept_request(u))

            button_item.setSizeHint(accept_btn.sizeHint())
            self.pending_list.setItemWidget(button_item, accept_btn)

    def _on_send_request(self) -> None:
        """Handle sending a friend request."""
        username = self.username_input.text().strip()

        if not username:
            QMessageBox.warning(self, "Input Required", "Please enter a username")
            return

        if not self.network_client:
            QMessageBox.warning(self, "Offline Mode", "Network features are not available in offline mode")
            return

        # Disable button while processing
        self.send_request_btn.setEnabled(False)
        self.username_input.setEnabled(False)

        self._worker = FriendRequestWorker(self.network_client, "send", username)
        self._worker.success.connect(self._on_request_success)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_accept_request(self, username: str) -> None:
        """Handle accepting a friend request."""
        if not self.network_client:
            return

        self._worker = FriendRequestWorker(self.network_client, "accept", username)
        self._worker.success.connect(self._on_request_success)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_request_success(self, message: str) -> None:
        """Handle successful friend request operation."""
        QMessageBox.information(self, "Success", message)

        # Clear input and reload data
        self.username_input.clear()
        self.username_input.setEnabled(True)
        self.send_request_btn.setEnabled(True)
        self._load_data()

    def _on_error(self, message: str) -> None:
        """Handle error in friend request operation."""
        QMessageBox.critical(self, "Error", message)

        # Re-enable controls
        self.username_input.setEnabled(True)
        self.send_request_btn.setEnabled(True)

    def _on_back(self) -> None:
        """Navigate back to main menu."""
        self.nav.navigate.emit("main_menu", None)
