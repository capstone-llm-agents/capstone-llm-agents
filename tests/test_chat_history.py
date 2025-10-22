"""Test suite for chat history functionalities."""

import pytest

from components.actions.chat_history import RespondWithChatHistory
from llm_mas.action_system.base.narrowers.graph_narrower import GraphBasedNarrower
from llm_mas.action_system.base.selectors.embedding_selector import EmbeddingSelector
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.action_system.core.action_space import ActionSpace
from llm_mas.mas.agent import Agent
from llm_mas.mas.conversation import ConversationManager
from llm_mas.mas.mas import MAS
from llm_mas.mas.user import User
from llm_mas.mcp_client.client import MCPClient
from llm_mas.model_providers.api import ModelsAPI
from llm_mas.tools.tool_manager import ToolManager
from llm_mas.tools.tool_narrower import DefaultToolNarrower


class TestChatHistory:
    """Test suite for chat history functionalities."""

    def setup_method(self) -> None:
        """Set up the test environment."""
        mas = MAS()
        agent = Agent(
            name="ChatHistoryAgent",
            description="An agent for testing chat history functionalities.",
            action_space=ActionSpace(),
            narrower=GraphBasedNarrower(),
            selector=EmbeddingSelector(ModelsAPI.get_embedding),
            tool_manager=ToolManager(DefaultToolNarrower()),
        )
        mas.add_agent(agent)

        # agent adds the knowledge base action here
        agent.add_action(RespondWithChatHistory())

        self.mas = mas

        self.agent = agent

        self.user = User(name="TestUser", description="A user for testing chat history functionalities.")

    @pytest.mark.asyncio
    async def test_remembers_prev_messages(self) -> None:
        """Test if the agent remembers previous messages in chat history."""
        try:
            await ModelsAPI.call_llm("RESPOND WITH THE LETTER A AND NOTHING ELSE.")
        except ConnectionError:
            msg = "LLM model is not available. Skipping test_remembers_prev_messages."
            raise pytest.skip(msg) from None

        conv = self.mas.conversation_manager.start_conversation("TestConversation")

        conv.add_message(self.user, "Hello, my name is Ned?")
        conv.add_message(self.agent, "Hi there, Ned! How can I help you today?")
        conv.add_message(self.user, "Do you remember my name?")

        # check chat history has 3 messages
        chat_history = conv.get_chat_history()
        assert len(chat_history.messages) == 3  # noqa: PLR2004

        # check last message content
        assert chat_history.messages[-1].content == "Do you remember my name?"

        context = ActionContext(
            conv,
            ActionResult(),
            MCPClient(),
            self.agent,
            self.user,
            ConversationManager(),
        )

        respond_with_chat_history = next(
            (action for action in self.agent.action_space.get_actions() if isinstance(action, RespondWithChatHistory)),
            None,
        )
        assert respond_with_chat_history is not None, (
            "RespondWithChatHistory action should be present in the agent's action space."
        )

        # agent should act
        response = await self.agent.do_selected_action(respond_with_chat_history, context)

        # has param
        assert response.has_param("response"), "Agent response should have 'response' param."

        context = response.get_param("response")

        assert "Ned" in context, "Agent should remember the user's name from chat history."
