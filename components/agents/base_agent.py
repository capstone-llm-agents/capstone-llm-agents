"""The assistant agent module defines the main assistant that talks to the user and handles their requests."""

from components.actions.assess_input import AssessInput
from components.actions.assess_response import AssessResponse
from components.actions.chat_history import RespondWithChatHistory
from components.actions.communicate import Communicate
from components.actions.contextualise import Contextualise
from components.actions.long_think import LongThink
from components.actions.reason import Reason
from components.actions.retrieve_knowledge import RetrieveKnowledge
from components.actions.short_think import ShortThink
from components.actions.simple_reflect import SimpleReflect
from components.actions.simple_response import SimpleResponse
from llm_mas.action_system.base.actions.stop import StopAction
from llm_mas.action_system.base.narrowers.graph_narrower import GraphBasedNarrower
from llm_mas.action_system.base.selectors.embedding_selector import EmbeddingSelector
from llm_mas.action_system.core.action_space import ActionSpace
from llm_mas.mas.agent import Agent
from llm_mas.model_providers.api import ModelsAPI
from llm_mas.tools.tool_manager import ToolManager
from llm_mas.tools.tool_narrower import DefaultToolNarrower


def create_base_agent(name: str, description: str) -> Agent:
    """Create a base assistant agent with a predefined set of actions and configurations."""
    action_space = ActionSpace()
    narrower = GraphBasedNarrower()
    selector = EmbeddingSelector(ModelsAPI.get_embedding)

    # tools
    tool_narrower = DefaultToolNarrower()
    tool_manager = ToolManager(
        tool_narrower,
    )

    agent = Agent(
        name,
        description,
        action_space,
        narrower,
        selector,
        tool_manager,
    )

    # add some actions
    agent.add_action(SimpleResponse())
    agent.add_action(StopAction())
    agent.add_action(AssessResponse())
    agent.add_action(SimpleReflect())
    agent.add_action(RetrieveKnowledge())
    agent.add_action(Communicate(embedding_model=ModelsAPI.get_embedding))
    agent.add_action(AssessInput())
    agent.add_action(Reason())
    agent.add_action(ShortThink())
    agent.add_action(LongThink())
    agent.add_action(RespondWithChatHistory())
    agent.add_action(Contextualise())

    # basic
    narrower.add_default_action(AssessInput())

    # add some edges
    narrower.add_action_edge(ShortThink(), [RespondWithChatHistory()])

    narrower.add_action_edge(AssessInput(), [Reason()])
    narrower.add_action_edge(LongThink(), [Contextualise()])
    narrower.add_action_edge(Contextualise(), [Communicate(embedding_model=ModelsAPI.get_embedding)])

    narrower.add_action_edge(AssessResponse(), [SimpleReflect()])
    narrower.add_action_edge(SimpleReflect(), [StopAction()])

    narrower.add_action_edge(RetrieveKnowledge(), [SimpleResponse()])
    narrower.add_action_edge(SimpleResponse(), [AssessResponse()])

    narrower.add_action_edge(RespondWithChatHistory(), [AssessResponse()])

    narrower.add_action_edge(Communicate(embedding_model=ModelsAPI.get_embedding), [AssessResponse()])

    return agent
