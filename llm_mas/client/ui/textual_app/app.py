"""The textual app entry point for rendering the UI in the terminal."""

from __future__ import annotations

import asyncio
import contextlib
import logging
import weakref
from pathlib import Path
from typing import TYPE_CHECKING

from textual.app import App, ComposeResult
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Button, Footer, Header, Input, Static

from components.actions.simple_response import SimpleResponse
from components.agents.example_agent import EXAMPLE_AGENT
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.agent.work_step import PerformingActionWorkStep, SelectingActionWorkStep, WorkStep
from llm_mas.mcp_client.connected_server import SSEConnectedServer

if TYPE_CHECKING:
    from textual import events

    from llm_mas.client.account.client import Client
    from llm_mas.mas.agent import Agent


def setup_file_only_logger(name: str, log_file: str, level: int = logging.INFO) -> logging.Logger:
    """Create a logger that only writes to file, no console output."""
    # ensure log directory exists
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # remove any existing handlers to start fresh
    logger.handlers.clear()

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    # prevent propagation to root logger (this prevents console output)
    logger.propagate = False

    return logger


app_logger = setup_file_only_logger("textual_app", "./logs/app.log", logging.DEBUG)

background_tasks: weakref.WeakSet[asyncio.Task] = weakref.WeakSet()


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


class WorkStepIndicator(Static):
    """A compact work step indicator that can be embedded in messages."""

    def __init__(self, work_step: WorkStep) -> None:
        """Initialize the work step indicator with a work step."""
        super().__init__(classes="work-step-indicator")
        self.work_step = work_step

    def compose(self) -> ComposeResult:
        """Compose the compact work step indicator."""
        with Horizontal(classes="work-step-row"):
            # Status indicator (tick or hourglass)
            if self.work_step.complete:
                self.status_widget = Static("✓", classes="step-complete")
            else:
                self.status_widget = Static("⏳", classes="step-in-progress")
            yield self.status_widget

            # Work step name
            self.text_widget = Static(self.work_step.name, classes="step-text")
            yield self.text_widget

    async def mark_complete(self) -> None:
        """Mark the work step as complete and update the UI."""
        self.work_step.mark_complete()
        if self.status_widget:
            self.status_widget.update("✓")
            self.status_widget.remove_class("step-in-progress")
            self.status_widget.add_class("step-complete")

    def mark_grey(self) -> None:
        """Mark the work step as grey (completed but not current focus)."""
        if self.status_widget and self.text_widget:
            self.status_widget.remove_class("step-complete")
            self.status_widget.add_class("step-complete-grey")
            self.text_widget.remove_class("step-text")
            self.text_widget.add_class("step-text-grey")

    def mark_current_green(self) -> None:
        """Mark the work step as current active green."""
        if self.status_widget and self.text_widget:
            self.status_widget.remove_class("step-complete-grey")
            self.status_widget.add_class("step-complete")
            self.text_widget.remove_class("step-text-grey")
            self.text_widget.add_class("step-text")


class AgentMessage(MessageBubble):
    """A message bubble widget for agent messages with integrated work steps."""

    def __init__(self, message: str = "", *, show_thinking: bool = False) -> None:
        """Initialize the agent message bubble."""
        super().__init__(message)
        self.show_thinking = show_thinking
        self.work_steps: list[WorkStepIndicator] = []
        self.thinking_container: Vertical | None = None
        self.thinking_header: Static | None = None
        self.thinking_content: Vertical | None = None
        self.message_bubble: Vertical | None = None
        self.is_thinking_expanded: bool = True
        self._is_processing: bool = True

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

                        self.thinking_content = Vertical(classes="thinking-content")
                        yield self.thinking_content

                    yield self.thinking_container

                if self.message:
                    yield Static(self.message, classes="message-content")
            yield self.message_bubble
            yield Static("", classes="spacer")

    async def add_work_step(self, work_step: WorkStep) -> WorkStepIndicator:
        """Add a work step to the thinking section."""
        # small delay to simulate processing time
        await asyncio.sleep(0.5)

        if not self.thinking_content:
            msg = "Thinking section is not initialized."
            app_logger.error(msg)
            raise RuntimeError(msg)

        # Make all previous completed steps grey
        for indicator in self.work_steps:
            if indicator.work_step.complete:
                indicator.mark_grey()

        # log
        msg = f"Adding work step: {work_step.name}"
        app_logger.debug(msg)

        indicator = WorkStepIndicator(work_step)
        self.work_steps.append(indicator)

        await self.thinking_content.mount(indicator)

        return indicator

    async def mark_step_complete(self, indicator: WorkStepIndicator) -> None:
        """Mark a work step as complete and manage the visual state."""
        await indicator.mark_complete()

    async def finalize_all_steps(self) -> None:
        """Mark the final step as green and keep previous ones grey."""
        # keep the last completed step green, others grey
        for i, indicator in enumerate(self.work_steps):
            if indicator.work_step.complete:
                if i == len(self.work_steps) - 1:
                    indicator.mark_current_green()
                else:
                    indicator.mark_grey()

    async def collapse_thinking_and_show_response(self, response_text: str) -> None:
        """Collapse the thinking section and show the final response."""
        self._is_processing = False

        if self.thinking_header and self.thinking_content:
            self.thinking_header.update("▶ Show thinking...")
            self.thinking_content.display = False
            self.is_thinking_expanded = False

        if self.message_bubble and response_text:
            response_widget = Static(response_text, classes="message-content")
            await self.message_bubble.mount(response_widget)

    def on_click(self, event: events.Click) -> None:
        """Handle clicks to toggle thinking section."""
        if (
            self.thinking_header
            and self.thinking_content
            and event.widget == self.thinking_header
            and not self._is_processing
        ):
            self.toggle_thinking_section()

    def toggle_thinking_section(self) -> None:
        """Toggle the visibility of the thinking section."""
        if not self.thinking_header or not self.thinking_content:
            return

        if self.is_thinking_expanded:
            self.thinking_header.update("▶ Show thinking...")
            self.thinking_content.display = False
            self.is_thinking_expanded = False
        else:
            self.thinking_header.update("▼ Hide thinking...")
            self.thinking_content.display = True
            self.is_thinking_expanded = True


class MainMenu(Screen):
    """Main menu screen of the application."""

    def __init__(self, client: Client) -> None:
        """Initialize the main menu with a client."""
        super().__init__()
        self.client = client

    def compose(self) -> ComposeResult:
        """Compose the main menu layout."""
        yield Header(show_clock=True)
        with Vertical():
            yield Button("Talk to Assistant Agent", id="talk_agent")
            yield Button("MCP Client Info", id="mcp_client_info")
            yield Button("List Agents", id="list_agents")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses to navigate to different screens."""
        if event.button.id == "list_agents":
            self.app.push_screen(AgentListScreen(self.client))
        elif event.button.id == "talk_agent":
            self.app.push_screen(ChatScreen(self.client))
        elif event.button.id == "mcp_client_info":
            self.app.push_screen(MCPClientScreen(self.client))


class MCPClientScreen(Screen):
    """Screen to display MCP client information."""

    CSS_PATH = "./styles/mcp.tcss"

    def __init__(self, client: Client) -> None:
        """Initialize the MCP client screen with a client."""
        super().__init__()
        self.client = client
        self.server_info_widget: Static | None = None
        self.error_display: Static | None = None

    def compose(self) -> ComposeResult:
        """Compose the MCP client layout."""
        yield Header(name="MCP Client Info")

        mcp_client = self.client.mcp_client
        initial_content = f"Connected Servers: {len(mcp_client.connected_servers)}\nLoading server details..."

        self.server_info_widget = Static(initial_content, classes="mcp-client-info")
        yield self.server_info_widget

        # text input and button to add a new server
        with Horizontal(classes="mcp-add-server"):
            value = "http://localhost:8080/sse"
            self.server_input = Input(value=value, placeholder="Enter server URL", id="server_input")
            yield self.server_input
        yield Button("Add Server", id="add_server_button")

        # error display widget
        self.error_display = Static("", classes="error-display")
        yield self.error_display

        yield Footer()

    async def on_mount(self) -> None:
        """Load server information after the screen is mounted."""
        await self._load_server_info()

    def _show_error(self, message: str) -> None:
        """Display an error message below the input."""
        if self.error_display:
            self.error_display.update(message)
            self.error_display.add_class("visible")

    def _clear_error(self) -> None:
        """Clear any displayed error message."""
        if self.error_display:
            self.error_display.update("")
            self.error_display.remove_class("visible")

    async def _load_server_info(self) -> None:
        """Load and display server information asynchronously."""
        if not self.server_info_widget:
            return

        mcp_client = self.client.mcp_client
        content = f"Connected Servers: {len(mcp_client.connected_servers)}\n"

        server_details = ""

        for server in mcp_client.connected_servers:
            try:
                async with server.connect() as session:
                    info = await server.initialize(session)
                    server_details += f"Server URL: {server.server_url}\nName: {info.name}\n\n"
            except Exception as e:
                msg = f"Error connecting to server {server.server_url}: {e!s}"
                app_logger.exception(msg)
                server_details += f"({server.server_url}) Error connecting to server. Please check the URL and make sure the server is running.\n\n"  # noqa: E501

        content += server_details
        self.server_info_widget.update(content)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses to add a new server."""
        if event.button.id == "add_server_button":
            server_url = self.server_input.value.strip()

            # already have a server with this URL
            if any(server.server_url == server_url for server in self.client.mcp_client.connected_servers):
                self._show_error("Server already added.")
                return

            if server_url:
                # clear any previous error
                self._clear_error()

                try:
                    new_server = SSEConnectedServer(server_url)
                    self.server_input.value = ""

                    async with new_server.connect() as session:
                        await new_server.initialize(session)

                    self.client.mcp_client.add_connected_server(new_server)

                    await self._load_server_info()

                except Exception as e:
                    msg = f"Failed to add server: {e}"
                    app_logger.exception(msg)
                    self._show_error("Could not add server. Please check the URL and make sure the server is running.")

    def on_key(self, event: events.Key) -> None:
        """Handle key events for navigation."""
        if event.key == "escape":
            self.app.pop_screen()


class AgentListScreen(Screen):
    """Screen to display a list of agents."""

    def __init__(self, client: Client) -> None:
        """Initialize the agent list screen with a client."""
        super().__init__()
        self.client = client

    def compose(self) -> ComposeResult:
        """Compose the agent list layout."""
        yield Header(name="Agent List")
        agents: list[str] = [agent.name for agent in self.client.get_mas().get_agents()]
        content: str = "\n".join(agents)
        yield Static(content)
        yield Footer()

    def on_key(self, event: events.Key) -> None:
        """Handle key events for navigation."""
        if event.key == "escape":
            self.app.pop_screen()


class ChatScreen(Screen):
    """Screen for chatting with an assistant agent with fully async workflow."""

    CSS_PATH = "./styles/screen.tcss"

    def __init__(self, client: Client) -> None:
        """Initialize the chat screen."""
        super().__init__()
        self.client = client
        self.chat_container: ScrollableContainer
        self.input: Input
        self.history: list[tuple[str, str]] = []
        self._current_task: asyncio.Task | None = None

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
        self.input.focus()

        welcome_bubble = AgentMessage("Hello! I'm your assistant. How can I help you today?")
        self.chat_container.mount(welcome_bubble)

    async def simulate_agent_workflow(self, user_msg: str, agent: Agent) -> None:  # noqa: PLR0915
        """Simulate the agent workflow with proper async handling and timeouts."""
        agent_bubble = AgentMessage(show_thinking=True)
        await self.chat_container.mount(agent_bubble)
        self.chat_container.scroll_end(animate=False)

        try:
            agent.workspace.action_history.clear()

            context = None
            step_count = 0

            while not agent.finished_working():
                step_count += 1
                msg = f"Step {step_count}: Processing your request..."
                app_logger.info(msg)

                selecting_step = SelectingActionWorkStep()
                selecting_indicator = await agent_bubble.add_work_step(selecting_step)

                try:
                    selected_action = await asyncio.wait_for(
                        asyncio.to_thread(agent.select_action, context),
                        timeout=30.0,  # 30 second timeout
                    )
                except TimeoutError:
                    msg = f"Action selection timed out on step {step_count}"
                    app_logger.exception(msg)
                    await agent_bubble.collapse_thinking_and_show_response(
                        "Sorry, the request timed out. Please try again.",
                    )
                    return

                selecting_step.mark_complete()
                if selecting_indicator:
                    await agent_bubble.mark_step_complete(selecting_indicator)

                performing_step = PerformingActionWorkStep(selected_action)
                performing_indicator = await agent_bubble.add_work_step(performing_step)

                params = ActionParams()
                params.set_param("prompt", user_msg)

                try:
                    context = await asyncio.wait_for(
                        asyncio.to_thread(agent.do_selected_action, selected_action, context, params),
                        timeout=60.0,  # 60 second timeout for action execution
                    )
                except TimeoutError:
                    msg = f"Action execution timed out on step {step_count}"
                    app_logger.exception(msg)
                    await agent_bubble.collapse_thinking_and_show_response(
                        "Sorry, the action took too long to complete. Please try again.",
                    )
                    return

                # mark execution complete
                performing_step.mark_complete()
                if performing_indicator:
                    await agent_bubble.mark_step_complete(performing_indicator)

                self.chat_container.scroll_end(animate=False)

                msg = f"Completed workflow step {step_count}"
                app_logger.info(msg)

                # finalize all steps to show proper completion state
                await agent_bubble.finalize_all_steps()

                # extract and display response
                response = await self._extract_response_safe(agent)

                self.chat_container.scroll_end(animate=False)

                msg = f"Completed workflow step {step_count}"
                app_logger.info(msg)

            # small delay to simulate processing time
            await asyncio.sleep(0.5)

            # extract and display response
            response = await self._extract_response_safe(agent)
            await agent_bubble.collapse_thinking_and_show_response(response)
            self.chat_container.scroll_end(animate=True)

            app_logger.info("Agent workflow completed successfully")

        except Exception as e:
            msg = f"Error in agent workflow: {e}"
            app_logger.exception(msg)
            await agent_bubble.collapse_thinking_and_show_response(f"Sorry, an error occurred: {e!s}")

    async def _extract_response_safe(self, agent: Agent) -> str:
        """Safely extract response from agent history with proper error handling."""

        def extract_response() -> str:
            try:
                action_res_tuple = agent.workspace.action_history.get_history_at_index(-2)
                if action_res_tuple is None:
                    return "I apologize, but I couldn't generate a response. Please try again."

                action, result = action_res_tuple
                if isinstance(action, SimpleResponse):
                    response = result.get_param("response")
                    return (
                        response if response else "I generated an empty response. Please try rephrasing your question."
                    )
                # NOTE: Don't really understand TRY300
                return "I completed the task but couldn't extract a readable response."  # noqa: TRY300
            except Exception as e:
                msg = f"Error extracting response: {e}"
                app_logger.exception(msg)
                return f"Sorry, there was an error processing your request: {e!s}"

        return await asyncio.to_thread(extract_response)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission with proper task management and cancellation."""
        user_msg: str = event.value.strip()
        event.input.value = ""
        self.input.value = ""

        if not user_msg:
            return

        # cancel any existing workflow
        if self._current_task and not self._current_task.done():
            app_logger.info("Cancelling previous workflow task")
            self._current_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._current_task

        # add user message
        user_bubble = UserMessage(user_msg)
        await self.chat_container.mount(user_bubble)
        self.chat_container.scroll_end(animate=True)

        # update history
        self.history.append(("user", user_msg))

        # create and track new workflow task
        self._current_task = asyncio.create_task(
            self.simulate_agent_workflow(user_msg, EXAMPLE_AGENT),
            name=f"agent_workflow_{len(self.history)}",
        )
        background_tasks.add(self._current_task)

        def task_done_callback(task: asyncio.Task) -> None:
            background_tasks.discard(task)
            if task.cancelled():
                app_logger.info("Agent workflow task was cancelled")
            elif task.exception():
                msg = f"Agent workflow task failed: {task.exception()}"
                app_logger.error(msg)

        self._current_task.add_done_callback(task_done_callback)

    def on_key(self, event: events.Key) -> None:
        """Handle key events for navigation and workflow control."""
        if event.key == "escape":
            # cancel current workflow if running
            if self._current_task and not self._current_task.done():
                self._current_task.cancel()
            self.app.pop_screen()

        elif event.key == "ctrl+c":
            # allow users to cancel current operation
            if self._current_task and not self._current_task.done():
                app_logger.info("User cancelled current workflow")
                self._current_task.cancel()

    async def on_unmount(self) -> None:
        """Clean up when screen is unmounted."""
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._current_task


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
        app_logger.info("Shutting down application, cancelling background tasks...")

        # cancel all background tasks
        for task in list(background_tasks):
            if not task.done():
                task.cancel()

        # wait for tasks to complete cancellation
        if background_tasks:
            await asyncio.gather(*background_tasks, return_exceptions=True)
