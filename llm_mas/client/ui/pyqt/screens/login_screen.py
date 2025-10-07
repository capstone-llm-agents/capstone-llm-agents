"""Login/Signup screen for network authentication."""

import asyncio

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from network_server.client import NetworkClient


class LoginScreen(QWidget):
    """Login and signup screen for network authentication."""

    login_successful = pyqtSignal(object)  # Emits NetworkClient on success

    def __init__(self) -> None:
        """Initialize the login screen."""
        super().__init__()
        self.network_client = NetworkClient()
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the UI components."""
        layout = QVBoxLayout()
        layout.addStretch(2)

        # Title
        title = QLabel("LLM Multi-Agent System")
        title.setStyleSheet(
            "font-size: 28px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;"
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Sign in to continue")
        subtitle.setStyleSheet("font-size: 14px; color: #7f8c8d; margin-bottom: 30px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(
            "color: #666; font-size: 13px; margin-bottom: 15px; min-height: 20px;"
        )
        layout.addWidget(self.status_label)

        # Username field
        username_label = QLabel("Username:")
        username_label.setStyleSheet("font-size: 13px; margin-bottom: 5px;")
        layout.addWidget(username_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.setMaximumWidth(320)
        self.username_input.setMinimumHeight(35)
        self.username_input.setStyleSheet(
            "padding: 8px; font-size: 13px; border: 1px solid #bdc3c7; border-radius: 4px;"
        )
        layout.addWidget(self.username_input, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(15)

        # Password field
        password_label = QLabel("Password:")
        password_label.setStyleSheet("font-size: 13px; margin-bottom: 5px;")
        layout.addWidget(password_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMaximumWidth(320)
        self.password_input.setMinimumHeight(35)
        self.password_input.setStyleSheet(
            "padding: 8px; font-size: 13px; border: 1px solid #bdc3c7; border-radius: 4px;"
        )
        layout.addWidget(self.password_input, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(25)

        # Buttons
        self.login_btn = QPushButton("Login")
        self.login_btn.setMaximumWidth(320)
        self.login_btn.setMinimumHeight(38)
        self.login_btn.setStyleSheet(
            "font-size: 14px; font-weight: bold; padding: 8px; "
            "background-color: #3498db; color: white; border: none; border-radius: 4px;"
        )
        layout.addWidget(self.login_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(10)

        self.signup_btn = QPushButton("Sign Up")
        self.signup_btn.setMaximumWidth(320)
        self.signup_btn.setMinimumHeight(38)
        self.signup_btn.setStyleSheet(
            "font-size: 14px; padding: 8px; "
            "background-color: #2ecc71; color: white; border: none; border-radius: 4px;"
        )
        layout.addWidget(self.signup_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(20)

        # Skip button (for development/offline mode)
        self.skip_btn = QPushButton("Skip (Offline Mode)")
        self.skip_btn.setMaximumWidth(320)
        self.skip_btn.setMinimumHeight(32)
        self.skip_btn.setStyleSheet(
            "font-size: 12px; padding: 6px; "
            "background-color: #95a5a6; color: white; border: none; border-radius: 4px;"
        )
        layout.addWidget(self.skip_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        layout.addStretch(3)

        self.setLayout(layout)

        # Connect signals
        self.login_btn.clicked.connect(self._on_login)
        self.signup_btn.clicked.connect(self._on_signup)
        self.skip_btn.clicked.connect(self._on_skip)
        self.password_input.returnPressed.connect(self._on_login)

    def _on_login(self) -> None:
        """Handle login button click."""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self._show_error("Please enter both username and password")
            return

        self._set_loading(True)
        self.status_label.setText("Logging in...")

        async def do_login():
            try:
                success = await self.network_client.login(username, password)
                if success:
                    self.status_label.setText(f"✓ Successfully logged in as {username}")
                    self.status_label.setStyleSheet(
                        "color: #27ae60; font-size: 14px; font-weight: bold; "
                        "margin-bottom: 15px; min-height: 20px;"
                    )
                    # Brief delay to show success message
                    await asyncio.sleep(0.8)
                    self.login_successful.emit(self.network_client)
                else:
                    self._show_error("Invalid username or password")
                    self._set_loading(False)
            except Exception as e:
                error_msg = str(e)
                if "Connection" in error_msg or "connection" in error_msg:
                    self._show_error(
                        "Cannot connect to server.\n\n"
                        "Please start the network server first:\n"
                        "python -m network_server.run_network"
                    )
                elif "already logged in" in error_msg or "409" in error_msg:
                    self._show_error(
                        "User is already logged in from another location.\n\n"
                        "Please logout from the other location first, or use a different account."
                    )
                else:
                    self._show_error(f"Login failed: {error_msg}")
                self._set_loading(False)

        asyncio.create_task(do_login())

    def _on_signup(self) -> None:
        """Handle signup button click."""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self._show_error("Please enter both username and password")
            return

        if len(password) < 6:
            self._show_error("Password must be at least 6 characters")
            return

        self._set_loading(True)
        self.status_label.setText("Creating account...")

        async def do_signup():
            try:
                success = await self.network_client.signup(username, password)
                if success:
                    self.status_label.setText(f"✓ Account created! Welcome, {username}")
                    self.status_label.setStyleSheet(
                        "color: #27ae60; font-size: 14px; font-weight: bold; "
                        "margin-bottom: 15px; min-height: 20px;"
                    )
                    # Brief delay to show success message
                    await asyncio.sleep(0.8)
                    self.login_successful.emit(self.network_client)
                else:
                    self._show_error("Username already exists or signup failed")
                    self._set_loading(False)
            except Exception as e:
                error_msg = str(e)
                if "Connection" in error_msg or "connection" in error_msg:
                    self._show_error(
                        "Cannot connect to server.\n\n"
                        "Please start the network server first:\n"
                        "python -m network_server.run_network"
                    )
                else:
                    self._show_error(f"Signup failed: {error_msg}")
                self._set_loading(False)

        asyncio.create_task(do_signup())

    def _on_skip(self) -> None:
        """Handle skip button - continue without network connection."""
        reply = QMessageBox.question(
            self,
            "Offline Mode",
            "Continue without network connection?\n\n"
            "You won't be able to use network features.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.login_successful.emit(None)  # None indicates offline mode

    def _set_loading(self, loading: bool) -> None:
        """Enable/disable buttons during loading."""
        self.login_btn.setEnabled(not loading)
        self.signup_btn.setEnabled(not loading)
        self.skip_btn.setEnabled(not loading)
        self.username_input.setEnabled(not loading)
        self.password_input.setEnabled(not loading)

    def _show_error(self, message: str) -> None:
        """Show an error message dialog."""
        self.status_label.setText("")
        QMessageBox.critical(self, "Error", message)
