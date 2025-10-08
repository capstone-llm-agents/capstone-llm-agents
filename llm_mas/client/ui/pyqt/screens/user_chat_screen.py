# user_chat_screen.py (PyQt6 fully MAS-integrated)
import asyncio

from PyQt6.QtWidgets import QHBoxLayout, QLineEdit, QPushButton, QScrollArea, QVBoxLayout, QWidget

from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.agent.work_step import PerformingActionWorkStep, SelectingActionWorkStep
from llm_mas.client.account.client import Client
from llm_mas.client.ui.pyqt.components.agent_message_bubble import AgentMessage
from llm_mas.client.ui.pyqt.components.user_message_bubble import UserMessage
from llm_mas.logging.loggers import APP_LOGGER
from llm_mas.mas.agent import Agent
from llm_mas.mas.agentstate import State
from llm_mas.mas.checkpointer import CheckPointer
from llm_mas.mas.conversation import Conversation, Message
from llm_mas.utils.background_tasks import BACKGROUND_TASKS


class UserChatScreen(QWidget):
    """PyQt6 chat screen with real MAS agent workflow."""

    def __init__(
        self,
        client: Client,
        conversation: Conversation,
        checkpoint: CheckPointer,
        nav: QWidget,
        artificial_delay: float | None = 0.1,
    ):
        super().__init__()
        self.client = client
        self.conversation = conversation
        self.checkpoint = checkpoint
        self.nav = nav
        self.artificial_delay = artificial_delay
        self._current_task: asyncio.Task | None = None

        self._init_ui()
        self._add_initial_assistant_message()

    def _init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Top bar with back button
        top_bar = QHBoxLayout()
        self.back_btn = QPushButton("← Back")
        self.back_btn.clicked.connect(lambda: (self._save_on_exit(), self.nav.navigate.emit("main_menu", None)))
        top_bar.addWidget(self.back_btn)
        top_bar.addStretch()
        layout.addLayout(top_bar)

        # Scrollable chat area
        self.chat_area = QScrollArea()
        self.chat_area.setWidgetResizable(True)
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout()
        self.chat_layout.addStretch()
        self.chat_container.setLayout(self.chat_layout)
        self.chat_area.setWidget(self.chat_container)
        layout.addWidget(self.chat_area)

        # Input line and send button
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Type your message…")
        layout.addWidget(self.input_line)

        self.send_btn = QPushButton("Send")
        layout.addWidget(self.send_btn)
        self.send_btn.clicked.connect(self._on_send)
        self.input_line.returnPressed.connect(self._on_send)

    def _save_on_exit(self):
        # Save conversation state to checkpoint
        message = self.conversation.get_chat_history()
        state: State = {"messages": message.as_dicts()}
        self.checkpoint.save(state)

    def _add_initial_assistant_message(self):
        agent = self.client.get_mas().get_assistant_agent()
        # check if conversation is empty, then load from checkpoint
        if agent and not self.conversation.chat_history.messages:
            state = self.checkpoint.fetch()
            # load conversation if it exists
            if state:
                for message in state:
                    message_to_save = Message(role=message["role"], content=message["content"], sender=agent)
                    self.conversation.chat_history.add_message(message_to_save)
                    if message_to_save.role == "user":
                        self._add_user_message(message_to_save.content)
                    elif message_to_save.role == "assistant":
                        self._add_agent_message(agent, message_to_save.content)

            else:
                # add default initial message
                msg = "Hello! I'm your assistant. How can I help you today?"
                self._add_agent_message(agent, msg)
                self.conversation.add_message(agent, msg)

    def _add_user_message(self, text: str):
        bubble = UserMessage(text)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble)
        self.chat_area.verticalScrollBar().setValue(self.chat_area.verticalScrollBar().maximum())

    def _add_agent_message(self, agent: Agent, text: str):
        bubble = AgentMessage(agent, text)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble)
        self.chat_area.verticalScrollBar().setValue(self.chat_area.verticalScrollBar().maximum())

    def _on_send(self):
        text = self.input_line.text().strip()
        if not text:
            return
        self.input_line.clear()
        self._add_user_message(text)
        self.conversation.add_message(self.client.user, text)

        agent = self.client.get_mas().get_assistant_agent()
        if agent:
            if self._current_task and not self._current_task.done():
                self._current_task.cancel()
            self._current_task = asyncio.create_task(self._run_agent_workflow(agent, text))
            BACKGROUND_TASKS.add(self._current_task)
            self._current_task.add_done_callback(lambda t: BACKGROUND_TASKS.discard(t))

    async def _run_agent_workflow(self, agent: Agent, user_msg: str):
        try:
            # Create context
            context = ActionContext(
                self.conversation,
                ActionResult(),
                self.client.mcp_client,
                agent,
                self.client.user,
                self.client.get_mas().conversation_manager,
                self.client,
            )

            agent.workspace.action_history.clear()

            # just as one
            agent_bubble = AgentMessage(agent, "[Processing…]", show_thinking=True)
            self.chat_layout.insertWidget(self.chat_layout.count() - 1, agent_bubble)
            self.chat_area.verticalScrollBar().setValue(self.chat_area.verticalScrollBar().maximum())

            while not agent.finished_working():
                # Selecting step
                selecting_step = SelectingActionWorkStep()
                selecting_indicator = await agent_bubble.add_work_step(selecting_step)

                selected_action = await agent.select_action(context)
                await agent_bubble.mark_step_complete(selecting_indicator)

                # Performing step
                performing_step = PerformingActionWorkStep(selected_action)
                performing_indicator = await agent_bubble.add_work_step(performing_step)

                params = ActionParams()
                result = await agent.do_selected_action(selected_action, context, params)
                context = ActionContext.from_action_result(result, context)

                await agent_bubble.mark_step_complete(performing_indicator)

            # Extract final response
            response = await asyncio.to_thread(self._extract_response_safe, agent)
            self.conversation.add_message(agent, response)
            await agent_bubble.collapse_thinking_and_show_response(response)

        except Exception as e:
            APP_LOGGER.exception(f"Error running agent workflow: {e}")
            agent_bubble.mark_as_error()  # looks a bit funny
            agent_bubble.content_label.setText(f"[Error: {e}]")

    async def _add_step_indicator(self, agent: Agent, step):
        """Add a placeholder step indicator in UI (optional)."""
        bubble = AgentMessage(agent, "[Processing…]")
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble)
        self.chat_area.verticalScrollBar().setValue(self.chat_area.verticalScrollBar().maximum())
        await asyncio.sleep(0.05)  # tiny delay to render
        return step  # no async methods required; just for step logic

    def _extract_response_safe(self, agent: Agent) -> str:
        try:
            action_res_tuple = agent.workspace.action_history.get_history_at_index(-2)
            if action_res_tuple is None:
                return "I couldn't generate a response. Please try again."
            _, result, _ = action_res_tuple
            response = result.get_param("response")
            return str(response) if isinstance(response, str) else "Agent completed task but no readable response."
        except Exception as e:
            APP_LOGGER.exception(f"Error extracting response: {e}")
            return f"Error processing your request: {e}"
