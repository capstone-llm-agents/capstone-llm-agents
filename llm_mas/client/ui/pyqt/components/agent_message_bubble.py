"""Agent message bubble with thinking/work steps for PyQt6."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from .message_bubble import MessageBubble
from .work_step_indicator import WorkStepIndicator
from llm_mas.agent.work_step import WorkStep
from llm_mas.mas.agent import Agent
import asyncio

class AgentMessage(MessageBubble):
    """Message bubble for agent messages, supports thinking steps."""

    def __init__(
        self,
        agent: Agent,
        message: str = "",
        *,
        show_thinking: bool = False,
        artificial_delay: float | None = None,
    ) -> None:
        super().__init__(message)
        self.agent = agent
        self.show_thinking = show_thinking
        self.work_steps: list[WorkStepIndicator] = []

        self.sender_label = QLabel(agent.name)
        self.layout.addWidget(self.sender_label)

        if show_thinking:
            self.thinking_label = QLabel("Thinking...")
            self.layout.addWidget(self.thinking_label)
            self.thinking_container = QVBoxLayout()
            self.layout.addLayout(self.thinking_container)

        if message:
            self.content_label = QLabel(message)
            self.layout.addWidget(self.content_label)

    async def add_work_step(self, work_step: WorkStep) -> WorkStepIndicator:
        """Add a work step to the agent bubble."""
        indicator = WorkStepIndicator(work_step)
        self.work_steps.append(indicator)
        if hasattr(self, "thinking_container"):
            self.thinking_container.addWidget(indicator)
        await asyncio.sleep(0.05)  # simulate async processing
        return indicator

    async def mark_step_complete(self, indicator: WorkStepIndicator):
        indicator.mark_complete()

    async def finalize_all_steps(self):
        for i, indicator in enumerate(self.work_steps):
            if i == len(self.work_steps) - 1:
                indicator.mark_current_green()
            else:
                indicator.mark_grey()

    async def collapse_thinking_and_show_response(self, response_text: str):
        if hasattr(self, "thinking_label"):
            self.thinking_label.setText("Thinking collapsed")
        if response_text:
            self.content_label = QLabel(response_text)
            self.layout.addWidget(self.content_label)

    def mark_as_error(self): # I WANNA MAKE ERROR MESSAGES RED but idk how to do it, ill do it later
        self.setStyleSheet("background-color: #bf1f1f; color: #ffffff;")
