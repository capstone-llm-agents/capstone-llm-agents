"""Session manager to track the currently active user session.

This module provides a simple file-based session management system to ensure
only one user is logged in across all application instances.
"""

import json
import os
from pathlib import Path
from typing import Optional


class SessionManager:
    """Manages user sessions across multiple application instances."""

    def __init__(self, session_file: str = "db/active_session.json") -> None:
        """Initialize the session manager.
        
        Args:
            session_file: Path to the session file for tracking active user
        """
        self.session_file = Path(session_file)
        self.session_file.parent.mkdir(parents=True, exist_ok=True)

    def get_active_session(self) -> Optional[dict]:
        """Get the currently active session information.
        
        Returns:
            Dictionary with session info (username, token) or None if no active session
        """
        if not self.session_file.exists():
            return None

        try:
            with open(self.session_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def set_active_session(self, username: str, token: Optional[str] = None) -> None:
        """Set the active session.
        
        Args:
            username: Username of the logged-in user
            token: Authentication token (optional)
        """
        session_data = {
            "username": username,
            "token": token,
        }

        with open(self.session_file, "w") as f:
            json.dump(session_data, f, indent=2)

    def clear_session(self) -> None:
        """Clear the active session."""
        if self.session_file.exists():
            self.session_file.unlink()

    def is_user_logged_in(self, username: str) -> bool:
        """Check if a specific user is currently logged in.
        
        Args:
            username: Username to check
            
        Returns:
            True if this user is logged in, False otherwise
        """
        session = self.get_active_session()
        return session is not None and session.get("username") == username


# Global session manager instance
SESSION_MANAGER = SessionManager()
