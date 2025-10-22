"""Test suite for agent communication actions."""

import pytest

from components.actions.communicate import Communicate
from components.actions.dummy_weather import GetWeather
from components.actions.secret import GetSecret
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


class TestCommunication:
    """Test suite for agent communication actions."""

    def setup_method(self) -> None:
        """Set up the test environment."""
        mas = MAS()

        # init a MAS with 3 agents
        # the assistant agent that will use the communicate action
        # the secret agent that holds secret information
        # the weather agent that provides weather information

        assistant_narrower = GraphBasedNarrower()
        agent = Agent(
            name="AssistantAgent",
            description="An agent for testing communication actions.",
            action_space=ActionSpace(),
            narrower=assistant_narrower,
            selector=EmbeddingSelector(ModelsAPI.get_embedding),
            tool_manager=ToolManager(DefaultToolNarrower()),
        )

        agent.add_action(Communicate(ModelsAPI.get_embedding))
        agent.add_action(StopAction())
        assistant_narrower.add_default_action(Communicate(ModelsAPI.get_embedding))
        assistant_narrower.add_action_edge(Communicate(ModelsAPI.get_embedding), [StopAction()])

        secret_narrower = GraphBasedNarrower()
        agent_with_secret = Agent(
            name="SecretAgent",
            description="An agent that holds secret information.",
            action_space=ActionSpace(),
            narrower=secret_narrower,
            selector=EmbeddingSelector(ModelsAPI.get_embedding),
            tool_manager=ToolManager(DefaultToolNarrower()),
        )

        secret_narrower.add_default_action(GetSecret())
        agent_with_secret.add_action(GetSecret())
        agent_with_secret.add_action(StopAction())
        secret_narrower.add_action_edge(GetSecret(), [StopAction()])

        weather_narrower = GraphBasedNarrower()
        weather_agent = Agent(
            name="WeatherAgent",
            description="An agent that provides weather information.",
            action_space=ActionSpace(),
            narrower=weather_narrower,
            selector=EmbeddingSelector(ModelsAPI.get_embedding),
            tool_manager=ToolManager(DefaultToolNarrower()),
        )

        weather_narrower.add_default_action(GetWeather())
        weather_agent.add_action(GetWeather())
        weather_agent.add_action(StopAction())
        weather_narrower.add_action_edge(GetWeather(), [StopAction()])

        mas.add_agent(agent)
        mas.add_agent(agent_with_secret)
        mas.add_agent(weather_agent)

        mas.set_assistant_agent(agent)

        self.assistant_agent = agent
        self.secret_agent = agent_with_secret
        self.weather_agent = weather_agent

        self.user = User(name="TestUser", description="A user for testing communication actions.")
        self.mas = mas

    @pytest.mark.asyncio
    async def test_communicate_action_present(self) -> None:
        """Communicate action should be present in the assistant agent's action space."""
        communicate_action = next(
            (action for action in self.assistant_agent.action_space.get_actions() if isinstance(action, Communicate)),
            None,
        )
        assert communicate_action is not None, (
            "Communicate action should be present in the assistant agent's action space."
        )

    async def _ensure_llm_available(self) -> None:
        try:
            await ModelsAPI.call_llm("RESPOND WITH THE LETTER A AND NOTHING ELSE.")
        except ConnectionError:
            pytest.skip("LLM model is not available. Skipping test.")

    def _create_default_action_context(self, conv: Conversation, agent: Agent) -> ActionContext:
        """Create a default ActionContext for testing."""
        return ActionContext(
            conv,
            ActionResult(),
            MCPClient(),
            agent,
            self.user,
            self.mas.conversation_manager,
        )

    @pytest.mark.asyncio
    async def test_communicate_action_functionality(self) -> None:
        """Test the functionality of the Communicate action."""
        communicate_action = next(
            (action for action in self.assistant_agent.action_space.get_actions() if isinstance(action, Communicate)),
            None,
        )
        assert communicate_action is not None, "Communicate action should be present."

    @pytest.mark.asyncio
    async def test_communicate_no_friends(self) -> None:
        """Test Communicate action when no friends are available."""
        await self._ensure_llm_available()

        conv = self.mas.conversation_manager.start_conversation("TestCommunicationNoFriends")
        conv.add_message(self.user, "Can you help me with something?")

        context = self._create_default_action_context(conv, self.assistant_agent)

        communicate_action = next(
            (action for action in self.assistant_agent.action_space.get_actions() if isinstance(action, Communicate)),
            None,
        )
        assert communicate_action is not None, "Communicate action should be present."

        result = await self.assistant_agent.do_selected_action(communicate_action, context)

        response = result.get_param("response")
        assert response == "No friends available to ask for help.", "Response should indicate no friends are available."

    @pytest.mark.asyncio
    async def test_communicate_with_friends(self) -> None:
        """Test Communicate action when friends are available."""
        await self._ensure_llm_available()

        # set up friends
        self.assistant_agent.add_friend(self.secret_agent)
        self.assistant_agent.add_friend(self.weather_agent)

        conv = self.mas.conversation_manager.start_conversation("TestCommunicationWithFriends")
        conv.add_message(self.user, "Can you help me with something?")

        context = self._create_default_action_context(conv, self.assistant_agent)
        communicate_action = next(
            (action for action in self.assistant_agent.action_space.get_actions() if isinstance(action, Communicate)),
            None,
        )
        assert communicate_action is not None, "Communicate action should be present."
        result = await self.assistant_agent.do_selected_action(communicate_action, context)
        response = result.get_param("response")

        # the embedding function is deterministic but we don't know which friend will be selected
        # and this isn't what we're testing here, so just check that the response is from one of the friends
        expected_responses = [
            "AMOGUS",
            "The weather is sunny with a temperature of 25.3 degrees Celsius.",
        ]

        assert response in expected_responses, (
            "Response should be from one of the friends: secret or weather information."
        )

    @pytest.mark.asyncio
    async def test_communicate_action_with_non_agent_friends(self) -> None:
        """Test Communicate action when friends include non-agent entities."""
        await self._ensure_llm_available()

        # create a non-agent friend
        non_agent_friend = User(name="NonAgentFriend", description="A helpful non-agent friend.")

        # set up friends
        self.assistant_agent.add_friend(non_agent_friend)

        conv = self.mas.conversation_manager.start_conversation("TestCommunicationWithNonAgentFriends")
        conv.add_message(self.user, "Can you help me with something?")

        context = self._create_default_action_context(conv, self.assistant_agent)
        communicate_action = next(
            (action for action in self.assistant_agent.action_space.get_actions() if isinstance(action, Communicate)),
            None,
        )
        assert communicate_action is not None, "Communicate action should be present."
        result = await self.assistant_agent.do_selected_action(communicate_action, context)
        response = result.get_param("response")
        assert response == "No agent friends available to ask for help.", (
            "Response should indicate no agent friends are available."
        )
