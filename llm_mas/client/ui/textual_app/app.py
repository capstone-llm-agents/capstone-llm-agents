"""The textual app entry point for rendering the UI in the terminal."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import App, ComposeResult
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Button, Footer, Header, Input, Static

if TYPE_CHECKING:
    from textual import events


class MessageBubble(Widget):
    """Base class for message bubble widgets."""

    def __init__(self, message: str) -> None:
        """Initialize the message bubble."""
        super().__init__()
        self.message = message


class UserMessage(MessageBubble):
    """A message bubble widget for user messages."""

    def compose(self) -> ComposeResult:
        """Compose the user message bubble."""
        with Horizontal(classes="user-message-container"):
            yield Static("", classes="spacer")  # Spacer to push message to right
            with Vertical(classes="user-message-bubble"):
                yield Static("You", classes="message-sender")
                yield Static(self.message, classes="message-content")


class AgentMessage(MessageBubble):
    """A message bubble widget for agent messages."""

    def compose(self) -> ComposeResult:
        """Compose the agent message bubble."""
        with Horizontal(classes="assistant-message-container"):
            with Vertical(classes="assistant-message-bubble"):
                yield Static("Assistant", classes="message-sender")
                yield Static(self.message, classes="message-content")
            yield Static("", classes="spacer")  # Spacer to push message to left


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

    CSS_PATH = "./styles/screen.tcss"

    chat_container: ScrollableContainer
    input: Input
    history: list[tuple[str, str]]

    def compose(self) -> ComposeResult:
        """Compose the chat layout."""
        yield Header(name="Chat with Assistant")

        self.chat_container = ScrollableContainer(id="chat-container")
        yield self.chat_container

        self.input = Input(placeholder="Type your message…", id="chat_input")
        yield self.input

        yield Footer()

    def on_mount(self) -> None:
        """Handle the mount event to initialize the chat screen."""
        self.history = []
        # focus the input so the user can start typing immediately
        self.input.focus()

        welcome_bubble = AgentMessage("Hello! I'm your assistant. How can I help you today?")
        self.chat_container.mount(welcome_bubble)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission from the chat box."""
        user_msg: str = event.value.strip()
        # clear the input early (robust to differing event shapes)
        event.input.value = ""
        self.input.value = ""

        if not user_msg:
            return

        user_bubble = UserMessage(user_msg)
        self.chat_container.mount(user_bubble)

        response: str = f"I heard '{user_msg}'."
        assistant_bubble = AgentMessage(response)
        self.chat_container.mount(assistant_bubble)

        self.history.append(("user", user_msg))
        self.history.append(("assistant", response))

        self.chat_container.scroll_end()

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
