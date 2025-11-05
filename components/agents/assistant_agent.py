"""The assistant agent module defines the main assistant that talks to the user and handles their requests."""

from components.actions.assess_input import AssessInput
from components.actions.assess_response import AssessResponse
from components.actions.chat_history import RespondWithChatHistory
from components.actions.communicate import Communicate
from components.actions.contextualise import Contextualise
from components.actions.entry import Entry
from components.actions.reason import Reason
from components.actions.retrieve_knowledge import RetrieveKnowledge
from components.actions.simple_reflect import SimpleReflect
from components.actions.simple_response import SimpleResponse
from llm_mas.action_system.base.actions.stop import StopAction
from llm_mas.action_system.base.narrowers.graph_narrower import GraphBasedNarrower
from llm_mas.action_system.base.selectors.embedding_selector import EmbeddingSelector
from llm_mas.action_system.core.action_space import ActionSpace
from llm_mas.mas.agent import Agent
from llm_mas.model_providers.api import ModelsAPI
from llm_mas.tools.tool_action_creator import DefaultToolActionCreator
from llm_mas.tools.tool_manager import ToolManager
from llm_mas.tools.tool_narrower import DefaultToolNarrower

action_space = ActionSpace()
narrower = GraphBasedNarrower()
selector = EmbeddingSelector(ModelsAPI.get_embedding)

# tools
tool_narrower = DefaultToolNarrower()
tool_creator = DefaultToolActionCreator()
tool_manager = ToolManager(
    tool_narrower,
)

ASSISTANT_AGENT = Agent(
    "Assistant",
    "An assistant that can interacts with the user to handle their requests.",
    action_space,
    narrower,
    selector,
    tool_manager,
)


# add some actions
ASSISTANT_AGENT.add_action(SimpleResponse())
ASSISTANT_AGENT.add_action(StopAction())
ASSISTANT_AGENT.add_action(AssessResponse())
ASSISTANT_AGENT.add_action(SimpleReflect())
ASSISTANT_AGENT.add_action(RetrieveKnowledge())
ASSISTANT_AGENT.add_action(Communicate(embedding_model=ModelsAPI.get_embedding))
ASSISTANT_AGENT.add_action(AssessInput())
ASSISTANT_AGENT.add_action(Reason())
ASSISTANT_AGENT.add_action(Entry())
ASSISTANT_AGENT.add_action(RespondWithChatHistory())
ASSISTANT_AGENT.add_action(Contextualise())

narrower.add_default_action(AssessInput())

# add some edges

narrower.add_action_edge(AssessInput(), [Reason()])
narrower.add_action_edge(Entry(), [Communicate(embedding_model=ModelsAPI.get_embedding)])

narrower.add_action_edge(AssessResponse(), [SimpleReflect()])
narrower.add_action_edge(SimpleReflect(), [StopAction()])

narrower.add_action_edge(RetrieveKnowledge(), [SimpleResponse()])
narrower.add_action_edge(SimpleResponse(), [AssessResponse()])

narrower.add_action_edge(RespondWithChatHistory(), [AssessResponse()])

narrower.add_action_edge(Communicate(embedding_model=ModelsAPI.get_embedding), [AssessResponse()])
