"""Test suite for agent context management."""

import pytest

from components.actions.say_hello import SayHello
from llm_mas.action_system.base.actions.stop import StopAction
from llm_mas.action_system.base.narrowers.graph_narrower import GraphBasedNarrower
from llm_mas.action_system.base.selectors.embedding_selector import EmbeddingSelector
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.action_system.core.action_space import ActionSpace
from llm_mas.mas.agent import Agent
from llm_mas.mas.conversation import Conversation
from llm_mas.mas.mas import MAS
from llm_mas.mas.user import User
from llm_mas.mcp_client.client import MCPClient
from llm_mas.model_providers.api import ModelsAPI
from llm_mas.tools.tool_manager import ToolManager
from llm_mas.tools.tool_narrower import DefaultToolNarrower
from llm_mas.utils.config.general_config import GENERAL_CONFIG


class TestContext:
    """Test suite for agent context management."""

    def setup_method(self) -> None:
        """Set up the test environment."""
        mas = MAS()
        narrower = GraphBasedNarrower()
        agent = Agent(
            name="ChatHistoryAgent",
            description="An agent for testing chat history functionalities.",
            action_space=ActionSpace(),
            narrower=narrower,
            selector=EmbeddingSelector(ModelsAPI.get_embedding),
            tool_manager=ToolManager(DefaultToolNarrower()),
        )
        mas.add_agent(agent)

        agent.add_action(SayHello())
        agent.add_action(StopAction())
        narrower.add_default_action(SayHello())
        narrower.add_action_edge(SayHello(), [StopAction()])

        # we don't want to use memory in these tests
        # 1. it would take longer
        # 2. it might affect the results
        GENERAL_CONFIG.app.config.use_memory = False

        self.mas = mas
        self.agent = agent
        self.user = User(name="TestUser", description="A user for testing chat history functionalities.")

    def _create_default_action_context(self, conv: Conversation) -> ActionContext:
        """Create a default ActionContext for testing."""
        return ActionContext(
            conv,
            ActionResult(),
            MCPClient(),
            self.agent,
            self.user,
            self.mas.conversation_manager,
        )

    @pytest.mark.asyncio
    async def test_say_hello_action(self) -> None:
        """Test the SayHello action."""
        conv = self.mas.conversation_manager.start_conversation("TestConversation")
        conv.add_message(self.user, "Please greet me.")

        context = self._create_default_action_context(conv)

        action = self.agent.action_space.get_action_with_name("SayHello")

        assert action is not None, "SayHello action should be available."

        result = await self.agent.do_selected_action(action, context)

        assert result.get_param("greeting") == "Hello, world!"

    @pytest.mark.asyncio
    async def test_context_retained_between_actions(self) -> None:
        """Test that the context is retained between actions."""
        conv = self.mas.conversation_manager.start_conversation("TestConversation")
        conv.add_message(self.user, "Please greet me and then stop.")

        context = self._create_default_action_context(conv)

        say_hello_action = self.agent.action_space.get_action_with_name("SayHello")
        stop_action = self.agent.action_space.get_action_with_name("StopAction")

        assert say_hello_action is not None, "SayHello action should be available."
        assert stop_action is not None, "StopAction should be available."

        # agent can just do work now
        response = await self.agent.work(context)

        # get the action history
        result, context = response

        assert context.last_result is not None, "Context should retain the last action result."
        assert not context.last_result.has_param("greeting"), (
            "Last action result should not have greeting because StopAction was last."
        )
        assert context.last_result.as_json_pretty() == "{}", "Last action result should be empty after StopAction."

        workspace = self.agent.workspace

        # workspace should have both actions recorded
        assert len(workspace.action_history.get_history()) == 2, "Workspace should have two actions in history."  # noqa: PLR2004

        say_hello_record = workspace.action_history.get_history_at_index(0)
        stop_action_record = workspace.action_history.get_history_at_index(1)

        assert say_hello_record is not None, "SayHello action record should be present."
        assert stop_action_record is not None, "StopAction action record should be present."

        assert say_hello_record[0].name == "SayHello", "First action should be SayHello."
        assert stop_action_record[0].name == "StopAction", "Second action should be StopAction."

        # assert that the stop action record has the context of say hello
        assert stop_action_record[2].last_result is not None, "StopAction context should have last result."
        assert stop_action_record[2].last_result.get_param("greeting") == "Hello, world!", (
            "StopAction context's last result should have greeting from SayHello action."
        )
