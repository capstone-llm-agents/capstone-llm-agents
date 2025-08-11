"""The textual app entry point for rendering the UI in the terminal."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, RichLog, Static

if TYPE_CHECKING:
    from textual import events


class MainMenu(Screen):
    """Main menu screen of the application."""

    def compose(self) -> ComposeResult:
        """Compose the main menu layout."""
        yield Header(show_clock=True)
        with Vertical():
            yield Button("List Agents", id="list_agents")
            yield Button("Talk to Assistant Agent", id="talk_agent")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses to navigate to different screens."""
        if event.button.id == "list_agents":
            self.app.push_screen(AgentListScreen())
        elif event.button.id == "talk_agent":
            self.app.push_screen(ChatScreen())


class AgentListScreen(Screen):
    """Screen to display a list of agents."""

    def compose(self) -> ComposeResult:
        """Compose the agent list layout."""
        yield Header(name="Agent List")
        agents: list[str] = ["Assistant Agent", "Research Agent", "Data Analysis Agent"]
        content: str = "\n".join(agents)
        yield Static(content)
        yield Footer()

    def on_key(self, event: events.Key) -> None:
        """Handle key events for navigation."""
        if event.key == "escape":
            self.app.pop_screen()


class ChatScreen(Screen):
    """Screen for chatting with an assistant agent."""

    chat_view: RichLog
    input: Input
    history: list[tuple[str, str]]

    def compose(self) -> ComposeResult:
        """Compose the chat layout."""
        yield Header(name="Chat with Assistant")
        # RichLog is a scrollable log widget that supports appending lines.
        self.chat_view = RichLog()
        yield self.chat_view

        self.input = Input(placeholder="Type your message…", id="chat_input")
        yield self.input

        yield Footer()

    def on_mount(self) -> None:
        """Handle the mount event to initialize the chat screen."""
        self.history = []
        # Focus the input so the user can start typing immediately
        self.input.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission from the chat box.

        This app simply echoes the user's message. Use `RichLog.write(...)`
        to append lines; `scroll_end=True` keeps the view scrolled to the bottom.
        """
        user_msg: str = event.value.strip()
        # clear the input early (robust to differing event shapes)
        event.input.value = ""
        self.input.value = ""

        if not user_msg:
            return

        # Append user message
        self.chat_view.write(f"You: {user_msg}", scroll_end=True)

        # Placeholder assistant response
        response: str = f"Assistant: I heard '{user_msg}'"
        self.chat_view.write(response, scroll_end=True)

        # Persist in local history (optional)
        self.history.append(("user", user_msg))
        self.history.append(("assistant", response))

    def on_key(self, event: events.Key) -> None:
        """Handle key events for navigation."""
        if event.key == "escape":
            self.app.pop_screen()


class TextualApp(App):
    """Main application class for the Textual UI."""

    def on_mount(self) -> None:
        """Mount the main menu screen on application start."""
        self.push_screen(MainMenu())


if __name__ == "__main__":
    TextualApp().run()
