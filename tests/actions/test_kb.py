"""Test suite for agent knowledge base actions."""

import os
from pathlib import Path

import pytest

from components.actions.retrieve_knowledge import RetrieveKnowledge
from llm_mas.action_system.base.narrowers.graph_narrower import GraphBasedNarrower
from llm_mas.action_system.base.selectors.embedding_selector import EmbeddingSelector
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.action_system.core.action_space import ActionSpace
from llm_mas.knowledge_base.knowledge_base import GLOBAL_KB
from llm_mas.mas.agent import Agent
from llm_mas.mas.conversation import Conversation, ConversationManager
from llm_mas.mas.mas import MAS
from llm_mas.mas.user import User
from llm_mas.mcp_client.client import MCPClient
from llm_mas.model_providers.api import ModelsAPI
from llm_mas.tools.tool_manager import ToolManager
from llm_mas.tools.tool_narrower import DefaultToolNarrower


class TestKnowledgeBase:
    """Test suite for agent knowledge base actions."""

    def setup_method(self) -> None:
        """Set up the test environment."""
        mas = MAS()
        agent = Agent(
            name="KnowledgeBaseAgent",
            description="An agent for testing knowledge base actions.",
            action_space=ActionSpace(),
            narrower=GraphBasedNarrower(),
            selector=EmbeddingSelector(ModelsAPI.get_embedding),
            tool_manager=ToolManager(DefaultToolNarrower()),
        )
        mas.add_agent(agent)

        # agent adds the knowledge base action here
        agent.add_action(RetrieveKnowledge())

        # clear global KB
        GLOBAL_KB.clear()

        self.mas = mas

        path = Path("README.md")

        self.path = path

        self.agent = agent

    @pytest.mark.asyncio
    async def test_can_ingest_knowledge(self) -> None:
        """Test if the agent can ingest knowledge into the global KB."""
        try:
            await ModelsAPI.get_embedding("test")
        except ConnectionError:
            msg = "Skipping test_can_ingest_knowledge: Embedding model is not available."
            raise pytest.skip(msg) from None

        assert GLOBAL_KB.is_empty(), "Global KB should be empty at the start of the test."

        assert self.path.exists(), "README.md file should exist for this test."

        await GLOBAL_KB.index_path(self.path)

        assert not GLOBAL_KB.is_empty(), "Global KB should not be empty after indexing a file."

        # query the knowledge base
        results = GLOBAL_KB.query("test")

        assert len(results) > 0, "Knowledge base query should return some results."

    def test_agent_has_retrieve_knowledge_action(
        self,
    ) -> None:
        """Check if the agent has the RetrieveKnowledge action."""
        assert any(isinstance(action, RetrieveKnowledge) for action in self.agent.action_space.get_actions()), (
            "Agent should have RetrieveKnowledge action."
        )

    @pytest.mark.asyncio
    async def test_retrieve_knowledge_action(self) -> None:
        """Test the properties of the RetrieveKnowledge action."""
        retrieve_action = next(
            (action for action in self.agent.action_space.get_actions() if isinstance(action, RetrieveKnowledge)),
            None,
        )
        assert retrieve_action is not None, "RetrieveKnowledge action should be present in the agent's action space."
        assert retrieve_action.name == "RetrieveKnowledge", "RetrieveKnowledge action should have the correct name."

        # now we can test executing the action
        try:
            await ModelsAPI.get_embedding("test")
        except ConnectionError:
            msg = "Skipping test_retrieve_knowledge_action: Embedding model is not available."
            raise pytest.skip(msg) from None

        await GLOBAL_KB.index_path(self.path)

        conv = Conversation(name="TestConversation")
        user = User("TestUser", " A user for testing.")

        context = ActionContext(
            conv,
            ActionResult(),
            MCPClient(),
            self.agent,
            user,
            ConversationManager(),
        )

        results = await self.agent.do_selected_action(retrieve_action, context)

        # check it has "facts" and "sources"
        assert results.has_param("facts"), "RetrieveKnowledge action result should have 'facts' parameter."
        assert results.has_param("sources"), "RetrieveKnowledge action result should have 'sources' parameter."

        facts = results.get_param("facts")
        sources = results.get_param("sources")

        assert len(facts) == 0, "Facts should be empty because there is no user query in the conversation."
        assert len(sources) == 0, "Sources should be empty because there is no user query in the conversation."

        # now add a user message to the conversation
        conv.add_message(user, "Can you provide some information from the README?")

        results = await self.agent.do_selected_action(retrieve_action, context)

        facts = results.get_param("facts")
        sources = results.get_param("sources")

        assert len(facts) > 0, "Facts should contain results after adding a user query."
        assert len(sources) > 0, "Sources should contain results after adding a user."
