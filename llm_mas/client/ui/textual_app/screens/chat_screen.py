"""The chat screen of the textual app."""

from __future__ import annotations

import asyncio
import contextlib
import time
from typing import TYPE_CHECKING

from textual.containers import ScrollableContainer
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Static

from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.agent.work_step import PerformingActionWorkStep, SelectingActionWorkStep
from llm_mas.client.ui.textual_app.components.agent_message_bubble import AgentMessage
from llm_mas.client.ui.textual_app.components.user_message_bubble import UserMessage
from llm_mas.logging.loggers import APP_LOGGER
from llm_mas.utils.background_tasks import BACKGROUND_TASKS

if TYPE_CHECKING:
    from textual import events
    from textual.app import ComposeResult

    from llm_mas.client.account.client import Client
    from llm_mas.mas.agent import Agent
    from llm_mas.mas.conversation import Conversation


class ChatScreen(Screen):
    """Screen for chatting with an assistant agent with fully async workflow."""

    CSS_PATH = "../styles/screen.tcss"

    def __init__(self, client: Client, *, artificial_delay: float | None = None) -> None:
        """Initialize the chat screen."""
        super().__init__()
        self.client = client
        self.chat_container: ScrollableContainer
        self.input: Input
        self.history: list[tuple[str, str]] = []
        self._current_task: asyncio.Task | None = None
        self.artificial_delay = artificial_delay or 0.1

        conversation = self.client.get_mas().conversation_manager.get_conversation("General")

        if not conversation:
            APP_LOGGER.error("No conversation found, cannot proceed with chat")
            msg = "No conversation available to chat with."
            raise RuntimeError(msg)

        self.conversation: Conversation = conversation

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

        agent = self.client.get_mas().get_assistant_agent()
        if not agent:
            APP_LOGGER.error("No assistant agent found in MAS, cannot proceed with chat")
            self.chat_container.mount(Static("No assistant agent available to respond."))
            return

        # check length
        if not self.conversation.chat_history.messages:
            # add initial message
            message = "Hello! I'm your assistant. How can I help you today?"
            self.conversation.add_message(agent, message)

        # display chat history
        for message in self.conversation.chat_history.messages:
            if message.role == "user":
                bubble = UserMessage(message.content)
            elif message.role == "assistant":
                bubble = AgentMessage(agent, message.content)
            else:
                msg = f"Unknown message role: {message.role}, skipping display"
                APP_LOGGER.warning(msg)
                continue

            self.chat_container.mount(bubble)

    async def simulate_agent_workflow(self, agent: Agent) -> None:  # noqa: PLR0915
        """Simulate the agent workflow with proper async handling and timeouts."""
        agent_bubble = AgentMessage(show_thinking=True, agent=agent)
        await self.chat_container.mount(agent_bubble)
        self.chat_container.scroll_end(animate=False)

        try:
            agent.workspace.action_history.clear()

            context = ActionContext(
                self.conversation,
                ActionResult(),
                self.client.mcp_client,
                agent,
                self.client.user,
                self.client.get_mas().conversation_manager,
                plan={}
            )
            step_count = 0

            while not agent.finished_working():
                step_count += 1
                msg = f"Step {step_count}: Processing your request..."
                APP_LOGGER.info(msg)

                selecting_step = SelectingActionWorkStep()
                selecting_indicator = await agent_bubble.add_work_step(selecting_step)

                start_time = time.time()

                try:
                    selected_action = await agent.select_action(context)
                except TimeoutError:
                    msg = f"Action selection timed out on step {step_count}"
                    APP_LOGGER.exception(msg)
                    await agent_bubble.collapse_thinking_and_show_response(
                        "Sorry, the request timed out. Please try again.",
                    )
                    return

                end_time = time.time()
                time_taken = end_time - start_time
                APP_LOGGER.debug(f"Action selection took {time_taken:.2f}s to complete")

                selecting_step.mark_complete()
                if selecting_indicator:
                    await agent_bubble.mark_step_complete(selecting_indicator, time_taken)

                performing_step = PerformingActionWorkStep(selected_action)
                performing_indicator = await agent_bubble.add_work_step(performing_step)

                params = ActionParams()

                start_time = time.time()

                try:
                    res = await agent.do_selected_action(selected_action, context, params)

                    # TODO: Wrap the context properly  # noqa: TD003
                    context = ActionContext.from_action_result(res, context)

                except TimeoutError:
                    msg = f"Action execution timed out on step {step_count}"
                    APP_LOGGER.exception(msg)
                    await agent_bubble.collapse_thinking_and_show_response(
                        "Sorry, the action took too long to complete. Please try again.",
                    )
                    return

                end_time = time.time()
                time_taken = end_time - start_time
                APP_LOGGER.debug(f"Action took {time_taken:.2f}s to complete")

                # mark execution complete
                performing_step.mark_complete()
                if performing_indicator:
                    await agent_bubble.mark_step_complete(performing_indicator, time_taken)

                self.chat_container.scroll_end(animate=False)

                msg = f"Completed workflow step {step_count}"
                APP_LOGGER.info(msg)

                # finalize all steps to show proper completion state
                await agent_bubble.finalize_all_steps()

                self.chat_container.scroll_end(animate=False)

                msg = f"Completed workflow step {step_count}"
                APP_LOGGER.info(msg)

            # small delay to simulate processing time
            if self.artificial_delay:
                await asyncio.sleep(self.artificial_delay)

            # extract and display response
            response = await self._extract_response_safe(agent)

            # add to conversation
            self.conversation.add_message(agent, response)

            await agent_bubble.collapse_thinking_and_show_response(response)
            self.chat_container.scroll_end(animate=True)

            APP_LOGGER.info("Agent workflow completed successfully")

        # TODO: More specific exception handling  # noqa: TD003
        except Exception as e:  # noqa: BLE001
            msg = f"Error in agent workflow: {e}"
            APP_LOGGER.exception(msg)
            await agent_bubble.collapse_thinking_and_show_response(f"Sorry, an error occurred: {e!s}")

    async def _extract_response_safe(self, agent: Agent) -> str:
        """Safely extract response from agent history with proper error handling."""

        def extract_response() -> str:
            try:
                action_res_tuple = agent.workspace.action_history.get_history_at_index(-2)
                if action_res_tuple is None:
                    return "I apologize, but I couldn't generate a response. Please try again."

                action, result, _ = action_res_tuple

                response = result.get_param("response")

                if not isinstance(response, str):
                    msg = "Response is not a string, cannot extract readable response."
                    APP_LOGGER.error(msg)
                    return "I completed the task but couldn't extract a readable response."

                # NOTE: I don't really understand TRY300
                return response  # noqa: TRY300

            # TODO: More specific exception handling  # noqa: TD003
            except Exception as e:  # noqa: BLE001
                msg = f"Error extracting response: {e}"
                APP_LOGGER.exception(msg)
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
            APP_LOGGER.info("Cancelling previous workflow task")
            self._current_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._current_task

        # add user message
        user_bubble = UserMessage(user_msg)
        await self.chat_container.mount(user_bubble)

        self.chat_container.scroll_end(animate=True)

        # update history
        self.history.append(("user", user_msg))
        self.conversation.add_message(self.client.user, user_msg)

        agent = self.client.get_mas().get_assistant_agent()

        if not agent:
            APP_LOGGER.error("No assistant agent found in MAS, cannot proceed with chat")
            await self.chat_container.mount(Static("No assistant agent available to respond."))
            return

        # create and track new workflow task
        self._current_task = asyncio.create_task(
            self.simulate_agent_workflow(agent),
            name=f"agent_workflow_{len(self.history)}",
        )
        BACKGROUND_TASKS.add(self._current_task)

        def task_done_callback(task: asyncio.Task) -> None:
            BACKGROUND_TASKS.discard(task)
            if task.cancelled():
                APP_LOGGER.info("Agent workflow task was cancelled")
            elif task.exception():
                msg = f"Agent workflow task failed: {task.exception()}"
                APP_LOGGER.error(msg)

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
                APP_LOGGER.info("User cancelled current workflow")
                self._current_task.cancel()

    async def on_unmount(self) -> None:
        """Clean up when screen is unmounted."""
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._current_task
