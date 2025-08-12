"""The textual app entry point for rendering the UI in the terminal."""

from __future__ import annotations

import asyncio
import random
from typing import TYPE_CHECKING

from textual.app import App, ComposeResult
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Button, Footer, Header, Input, LoadingIndicator, Static

from components.agents.example_agent import EXAMPLE_AGENT
from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.agent.work_step import PerformingActionWorkStep, SelectingActionWorkStep, Work, WorkStep

if TYPE_CHECKING:
    from textual import events

background_tasks = set()


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


class WorkStepIndicator(Widget):
    """A compact work step indicator that can be embedded in messages."""

    def __init__(self, work_step: WorkStep) -> None:
        """Initialize the work step indicator."""
        super().__init__()
        self.work_step = work_step

    def compose(self) -> ComposeResult:
        """Compose the compact work step indicator."""
        with Horizontal(classes="work-step-indicator"):
            if not self.work_step.complete:
                yield LoadingIndicator(classes="mini-spinner")
            else:
                yield Static("✓", classes="step-complete")

            step_text = self.work_step.name
            if self.work_step.work:
                step_text += f": {self.work_step.work.name}"
            yield Static(step_text, classes="step-text")

    async def mark_complete(self) -> None:
        """Mark the work step as complete and update the UI."""
        self.work_step.mark_complete()
        await self.recompose()


class AgentMessage(MessageBubble):
    """A message bubble widget for agent messages with integrated work steps."""

    def __init__(self, message: str = "", show_thinking: bool = False) -> None:
        """Initialize the agent message bubble."""
        super().__init__(message)
        self.show_thinking = show_thinking
        self.work_steps: list[WorkStepIndicator] = []
        self.thinking_container: Vertical | None = None
        self.thinking_header: Static | None = None
        self.thinking_content: Vertical | None = None
        self.message_bubble: Vertical | None = None
        self.is_thinking_expanded: bool = True

    def compose(self) -> ComposeResult:
        """Compose the agent message bubble."""
        with Horizontal(classes="assistant-message-container"):
            self.message_bubble = Vertical(classes="assistant-message-bubble")
            with self.message_bubble:
                yield Static("Assistant", classes="message-sender")

                if self.show_thinking:
                    self.thinking_container = Vertical(classes="thinking-section")
                    with self.thinking_container:
                        self.thinking_header = Static("▼ Thinking...", classes="thinking-header clickable")
                        yield self.thinking_header

                        # Create the thinking content container with unique ID
                        self.thinking_content = Vertical(classes="thinking-content")
                        with self.thinking_content:
                            pass

                        yield self.thinking_content

                    yield self.thinking_container

                if self.message:
                    yield Static(self.message, classes="message-content")
            yield self.message_bubble
            yield Static("", classes="spacer")

    async def add_work_step(self, work_step: WorkStep) -> WorkStepIndicator:
        """Add a work step to the thinking section."""
        if not self.thinking_content:
            return None

        indicator = WorkStepIndicator(work_step)
        static = Static(indicator.work_step.name, classes="work-step-text")
        await self.thinking_content.mount(static)

        # TODO figure out why the indicator doesn't show up
        # await self.thinking_content.mount(indicator)

        self.work_steps.append(indicator)

        self.thinking_content.refresh()
        return indicator

    async def collapse_thinking_and_show_response(self, response_text: str) -> None:
        """Collapse the thinking section and show the final response."""
        if self.thinking_header and self.thinking_content:
            # Update header to show collapsed state
            self.thinking_header.update("▶ Show thinking...")
            # Hide the thinking content
            self.thinking_content.display = False
            self.is_thinking_expanded = False

        # Add the response content to the message bubble
        if self.message_bubble:
            response_widget = Static(response_text, classes="message-content")
            await self.message_bubble.mount(response_widget)

    def on_click(self, event: events.Click) -> None:
        """Handle clicks to toggle thinking section."""
        if self.thinking_header and self.thinking_content and event.widget == self.thinking_header:
            self.toggle_thinking_section()

    def toggle_thinking_section(self) -> None:
        """Toggle the visibility of the thinking section."""
        if not self.thinking_header or not self.thinking_content:
            return

        if self.is_thinking_expanded:
            # Collapse
            self.thinking_header.update("▶ Show thinking...")
            self.thinking_content.display = False
            self.is_thinking_expanded = False
        else:
            # Expand
            self.thinking_header.update("▼ Hide thinking...")
            self.thinking_content.display = True
            self.is_thinking_expanded = True


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
        self.input.focus()

        welcome_bubble = AgentMessage("Hello! I'm your assistant. How can I help you today?")
        self.chat_container.mount(welcome_bubble)

    async def simulate_agent_workflow(self, user_msg: str) -> None:
        """Simulate an agent workflow using the ExampleAgent with compact work steps."""
        agent_bubble = AgentMessage(show_thinking=True)
        await self.chat_container.mount(agent_bubble)
        self.chat_container.scroll_end()

        # clear history
        EXAMPLE_AGENT.workspace.action_history.clear()

        while not EXAMPLE_AGENT.finished_working():
            selecting_step = SelectingActionWorkStep()

            selecting_indicator = await agent_bubble.add_work_step(selecting_step)

            selected_action = EXAMPLE_AGENT.select_action()

            await asyncio.sleep(random.uniform(1.2, 2.0))  # Simulate selection duration

            # actual selecting action step
            selecting_step.mark_complete()

            # ui
            if selecting_indicator:
                await selecting_indicator.mark_complete()

            # Show performing action step
            performing_step = PerformingActionWorkStep(selected_action)
            performing_indicator = await agent_bubble.add_work_step(performing_step)

            EXAMPLE_AGENT.do_selected_action(selected_action)

            await asyncio.sleep(random.uniform(1.2, 2.0))  # Simulate action duration

            # actual work step
            performing_step.mark_complete()

            # ui
            if performing_indicator:
                await performing_indicator.mark_complete()

        response = "who ask"

        await asyncio.sleep(0.3)
        await agent_bubble.collapse_thinking_and_show_response(response)
        self.chat_container.scroll_end()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission from the chat box."""
        user_msg: str = event.value.strip()
        event.input.value = ""
        self.input.value = ""

        if not user_msg:
            return

        user_bubble = UserMessage(user_msg)
        self.chat_container.mount(user_bubble)
        self.chat_container.scroll_end()

        self.history.append(("user", user_msg))

        task = asyncio.create_task(self.simulate_agent_workflow(user_msg))
        background_tasks.add(task)
        task.add_done_callback(background_tasks.discard)

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
