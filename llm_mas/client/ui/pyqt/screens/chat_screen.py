# chat_screen.py
import asyncio
import contextlib
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit,
    QScrollArea, QFrame, QVBoxLayout
)
from PyQt6.QtCore import Qt
from qasync import asyncSlot

from llm_mas.logging.loggers import APP_LOGGER
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.agent.work_step import PerformingActionWorkStep, SelectingActionWorkStep
from llm_mas.utils.background_tasks import BACKGROUND_TASKS


class ChatScreen(QWidget):
    """Chat with assistant agent (async workflow)."""

    def __init__(self, client, artificial_delay: float | None = 0.1, on_back=None):
        super().__init__()
        self.client = client
        self.on_back = on_back
        self.artificial_delay = artificial_delay

        layout = QVBoxLayout(self)

        header = QLabel("Chat with Assistant")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # scrollable chat
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.scroll_area.setWidget(self.chat_widget)
        layout.addWidget(self.scroll_area)

        # input field
        self.input = QLineEdit()
        self.input.setPlaceholderText("Type your message…")
        self.input.returnPressed.connect(self._on_input_submitted)
        layout.addWidget(self.input)

        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self._back_clicked)
        layout.addWidget(back_btn)

        self.history = []
        self._current_task: asyncio.Task | None = None

        conversation = self.client.get_mas().conversation_manager.get_conversation("General")
        if not conversation:
            raise RuntimeError("No conversation found")
        self.conversation = conversation

        self._load_history()

    def _load_history(self):
        for msg in self.conversation.chat_history.messages:
            self.chat_layout.addWidget(self._bubble(msg.role, msg.content))

    def _bubble(self, role, text):
        lbl = QLabel(text)
        if role == "user":
            lbl.setStyleSheet("background:#cce5ff; padding:5px; border-radius:6px;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        else:
            lbl.setStyleSheet("background:#e2e3e5; padding:5px; border-radius:6px;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)
        return lbl

    @asyncSlot()
    async def _on_input_submitted(self):
        user_msg = self.input.text().strip()
        self.input.clear()
        if not user_msg:
            return

        self.chat_layout.addWidget(self._bubble("user", user_msg))
        self.conversation.add_message(self.client.user, user_msg)

        agent = self.client.get_mas().get_assistant_agent()
        if not agent:
            self.chat_layout.addWidget(QLabel("No assistant agent available."))
            return

        if self._current_task and not self._current_task.done():
            self._current_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._current_task

        self._current_task = asyncio.create_task(self._simulate_agent(agent))
        BACKGROUND_TASKS.add(self._current_task)

    async def _simulate_agent(self, agent):
        """Simplified async workflow simulation."""
        bubble = QLabel(f"{agent.name} is thinking...")
        self.chat_layout.addWidget(bubble)

        await asyncio.sleep(self.artificial_delay)
        response = "This is a placeholder response."
        self.conversation.add_message(agent, response)

        bubble.setText(f"{agent.name}: {response}")

    def _back_clicked(self):
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()
        if self.on_back:
            self.on_back()
