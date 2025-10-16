"""Interactive chat screen for user to assistant conversations."""

import asyncio
import contextlib
import time

from textual import events
from textual.app import ComposeResult
from textual.widgets import Input, Static

from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.agent.work_step import PerformingActionWorkStep, SelectingActionWorkStep
from llm_mas.client.account.client import Client
from llm_mas.client.ui.textual_app.components.agent_message_bubble import AgentMessage
from llm_mas.client.ui.textual_app.components.user_message_bubble import UserMessage
from llm_mas.client.ui.textual_app.screens.base_chat_screen import BaseChatScreen
from llm_mas.logging.loggers import APP_LOGGER
from llm_mas.mas.agent import Agent
from llm_mas.mas.conversation import Conversation
from llm_mas.utils.background_tasks import BACKGROUND_TASKS


class UserChatScreen(BaseChatScreen):
    """Interactive chat screen for user to assistant conversations."""

    def __init__(self, client: Client, conversation: Conversation, *, artificial_delay: float | None = None) -> None:
        """Initialize with client and conversation."""
        super().__init__(client, conversation, title="Chat with Assistant")
        self.input: Input
        self.history: list[tuple[str, str]] = []
        self._current_task: asyncio.Task | None = None
        self.artificial_delay = artificial_delay or 0.1

    def compose(self) -> ComposeResult:
        """Compose the chat screen layout with input field."""
        yield from super().compose()
        self.input = Input(placeholder="Type your message…", id="chat_input")
        yield self.input

    def on_mount(self) -> None:
        """Focus input and add initial assistant message if needed."""
        self.input.focus()

        agent = self.client.get_mas().get_assistant_agent()
        if not agent:
            APP_LOGGER.error("No assistant agent found in MAS, cannot proceed with chat")
            self.chat_container.mount(Static("No assistant agent available to respond."))
            return

        if not self.conversation.chat_history.messages:
            # add initial message
            message = "Hello! I'm your assistant. How can I help you today?"
            self.conversation.add_message(agent, message)

    async def simulate_agent_workflow(self, agent: Agent) -> None:
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
                ""
            )
            step_count = 0

            while not agent.finished_working():
                step_count += 1
                APP_LOGGER.info(f"Step {step_count}: Processing request...")

                selecting_step = SelectingActionWorkStep()
                selecting_indicator = await agent_bubble.add_work_step(selecting_step)

                start_time = time.time()

                try:
                    selected_action = await agent.select_action(context)
                except TimeoutError:
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
                    context = ActionContext.from_action_result(res, context)
                except TimeoutError:
                    await agent_bubble.collapse_thinking_and_show_response(
                        "Sorry, the action took too long to complete. Please try again.",
                    )
                    return

                end_time = time.time()
                time_taken = end_time - start_time
                APP_LOGGER.debug(f"Action took {time_taken:.2f}s to complete")

                # add fragments from result to the step
                for fragment in res.fragments:
                    await performing_indicator.add_fragment(fragment)

                performing_step.mark_complete()
                if performing_indicator:
                    await agent_bubble.mark_step_complete(performing_indicator, time_taken)

                self.chat_container.scroll_end(animate=False)
                await agent_bubble.finalize_all_steps()
                self.chat_container.scroll_end(animate=False)

            if self.artificial_delay:
                await asyncio.sleep(self.artificial_delay)

            response = await self._extract_response_safe(agent)
            self.conversation.add_message(agent, response)
            await agent_bubble.collapse_thinking_and_show_response(response)
            self.chat_container.scroll_end(animate=True)

            APP_LOGGER.info("Agent workflow completed successfully")

        except Exception as e:  # noqa: BLE001
            APP_LOGGER.exception(f"Error in agent workflow: {e}")
            await agent_bubble.collapse_thinking_and_show_response(f"Sorry, an error occurred: {e!s}")

    async def _extract_response_safe(self, agent: Agent) -> str:
        """Safely extract response from agent history."""

        def extract_response() -> str:
            try:
                action_res_tuple = agent.workspace.action_history.get_history_at_index(-2)
                if action_res_tuple is None:
                    return "I couldn't generate a response. Please try again."

                _, result, _ = action_res_tuple
                response = result.get_param("response")

                if not isinstance(response, str):
                    return "I completed the task but couldn't extract a readable response."

                return response  # noqa: TRY300
            except Exception as e:  # noqa: BLE001
                APP_LOGGER.exception(f"Error extracting response: {e}")
                return f"Error processing your request: {e!s}"

        return await asyncio.to_thread(extract_response)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle user message submission."""
        user_msg: str = event.value.strip()
        event.input.value = ""
        self.input.value = ""

        if not user_msg:
            return

        if self._current_task and not self._current_task.done():
            self._current_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._current_task

        user_bubble = UserMessage(user_msg)
        await self.chat_container.mount(user_bubble)
        self.chat_container.scroll_end(animate=True)

        self.history.append(("user", user_msg))
        self.conversation.add_message(self.client.user, user_msg)

        agent = self.client.get_mas().get_assistant_agent()
        if not agent:
            await self.chat_container.mount(Static("No assistant agent available to respond."))
            return

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
                APP_LOGGER.error(f"Agent workflow task failed: {task.exception()}")

        self._current_task.add_done_callback(task_done_callback)

    def on_key(self, event: events.Key) -> None:
        """Keyboard shortcuts for back/cancel."""
        if event.key == "escape":
            if self._current_task and not self._current_task.done():
                self._current_task.cancel()
            self.app.pop_screen()
        elif event.key == "ctrl+c":
            if self._current_task and not self._current_task.done():
                self._current_task.cancel()

    async def on_unmount(self) -> None:
        """Cancel any ongoing agent task on screen unmount."""
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._current_task
