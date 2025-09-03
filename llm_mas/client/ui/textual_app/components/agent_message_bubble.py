"""A message bubble widget for agent messages with work steps."""

import asyncio

from textual import events
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static

from llm_mas.agent.work_step import WorkStep
from llm_mas.client.ui.textual_app.components.message_bubble import MessageBubble
from llm_mas.client.ui.textual_app.components.work_step_indicator import WorkStepIndicator
from llm_mas.logging.loggers import APP_LOGGER
from llm_mas.mas.agent import Agent


class AgentMessage(MessageBubble):
    """A message bubble widget for agent messages with integrated work steps."""

    def __init__(
        self,
        agent: Agent,
        message: str = "",
        *,
        show_thinking: bool = False,
        artificial_delay: float | None = None,
    ) -> None:
        """Initialize the agent message bubble."""
        super().__init__(message)
        self.agent = agent
        self.show_thinking = show_thinking
        self.work_steps: list[WorkStepIndicator] = []
        self.thinking_container: Vertical | None = None
        self.thinking_header: Static | None = None
        self.thinking_content: Vertical | None = None
        self.message_bubble: Vertical | None = None
        self.is_thinking_expanded: bool = True
        self._is_processing: bool = True
        self.artificial_delay = artificial_delay or 0.1

    def compose(self) -> ComposeResult:
        """Compose the agent message bubble."""
        with Horizontal(classes="assistant-message-container"):
            self.message_bubble = Vertical(classes="assistant-message-bubble")
            with self.message_bubble:
                yield Static(self.agent.name, classes="message-sender")

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
        if self.artificial_delay:
            await asyncio.sleep(self.artificial_delay)

        if not self.thinking_content:
            msg = "Thinking section is not initialized."
            APP_LOGGER.error(msg)
            raise RuntimeError(msg)

        # Make all previous completed steps grey
        for indicator in self.work_steps:
            if indicator.work_step.complete:
                indicator.mark_grey()

        # log
        msg = f"Adding work step: {work_step.name}"
        APP_LOGGER.debug(msg)

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
