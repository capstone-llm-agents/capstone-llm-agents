"""The textual app entry point for rendering the UI in the terminal."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

from textual.app import App

from llm_mas.client.ui.textual_app.screens.main_menu import MainMenu
from llm_mas.logging.loggers import APP_LOGGER
from llm_mas.utils.background_tasks import BACKGROUND_TASKS

if TYPE_CHECKING:
    from collections.abc import Coroutine

    from llm_mas.client.account.client import Client


def run_async_in_thread(coroutine: Coroutine) -> Any:  # noqa: ANN401
    """Run an async coroutine in a thread and return its result."""
    return asyncio.run(coroutine)


class TextualApp(App):
    """Main application class with optimized async handling."""

    def __init__(self, client: Client) -> None:
        """Initialize the application with an optional client."""
        super().__init__()
        self.client = client
        self.title = f"Welcome Back - {self.client.get_username()}"

    def on_mount(self) -> None:
        """Mount the main menu screen on application start."""
        self.push_screen(MainMenu(self.client))

    # TODO: Doesn't actually get called yet, need to find a way to hook into shutdown properly  # noqa: TD003
    async def on_shutdown(self) -> None:
        """Handle graceful shutdown of background tasks."""
        # log
        APP_LOGGER.info("Shutting down application, cancelling background tasks...")

        # cancel all background tasks
        for task in list(BACKGROUND_TASKS):
            if not task.done():
                task.cancel()

        # wait for tasks to complete cancellation
        if BACKGROUND_TASKS:
            await asyncio.gather(*BACKGROUND_TASKS, return_exceptions=True)
