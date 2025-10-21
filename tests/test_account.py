"""Test account-related functionalities like login and friends."""

import pytest

from network_server.client import NetworkClient


class TestAccount:
    """Test suite for account-related functionalities like login and friends."""

    def setup_method(self) -> None:
        """Set up test environment for account tests."""
        self.network_client = NetworkClient()

        self.username = "alice"
        self.password = "password123"  # noqa: S105

    @pytest.mark.asyncio
    async def test_login_successful(self) -> None:
        """Test successful login with valid credentials."""
        # skip if server is not running
        result = await self.network_client.ping()
        if result["status"] == "unreachable":
            pytest.skip("Network server is not running. Skipping login test.")

        result = await self.network_client.login(self.username, self.password)
        assert result, "Login should be successful with valid credentials."

    @pytest.mark.asyncio
    async def test_login_failure(self) -> None:
        """Test login failure with invalid credentials."""
        # skip if server is not running
        result = await self.network_client.ping()

        if result["status"] == "unreachable":
            pytest.skip("Network server is not running. Skipping login test.")

        result = await self.network_client.login("invalid_user", "wrong_password")
        assert not result, "Login should fail with invalid credentials."

    @pytest.mark.asyncio
    async def test_get_friends(self) -> None:
        """Test retrieving friends list after login."""
        # skip if server is not running
        result = await self.network_client.ping()
        if result["status"] == "unreachable":
            pytest.skip("Network server is not running. Skipping login test.")

        result = await self.network_client.login(self.username, self.password)

        friends = await self.network_client.get_friends()

        assert isinstance(friends, list), "Friends should be returned as a list."

        # alice should have at least one friend (bob) in test setup
        assert any(friend["username"] == "bob" for friend in friends), "Alice should have Bob as a friend."
