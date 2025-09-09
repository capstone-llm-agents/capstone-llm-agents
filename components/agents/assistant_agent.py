"""The assistant agent module defines the main assistant that talks to the user and handles their requests."""

from components.actions.assess_response import AssessResponse
from components.actions.list_friends import AskFriendForHelp
from components.actions.retrieve_knowledge import RetrieveKnowledge
from components.actions.simple_reflect import SimpleReflect
from components.actions.simple_response import SimpleResponse
from llm_mas.action_system.base.actions.stop import StopAction
from llm_mas.action_system.base.narrowers.graph_narrower import GraphBasedNarrower
from llm_mas.action_system.base.selectors.embedding_selector import EmbeddingSelector
from llm_mas.action_system.core.action_space import ActionSpace
from llm_mas.mas.agent import Agent
from llm_mas.model_providers.ollama.call_llm import get_embedding
from llm_mas.tools.tool_action_creator import DefaultToolActionCreator
from llm_mas.tools.tool_manager import ToolManager
from llm_mas.tools.tool_narrower import DefaultToolNarrower

action_space = ActionSpace()
narrower = GraphBasedNarrower()
selector = EmbeddingSelector(get_embedding)

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

narrower.add_default_action(SimpleResponse())
narrower.add_default_action(RetrieveKnowledge())
narrower.add_default_action(AskFriendForHelp(embedding_model=get_embedding))

# add some edges
narrower.add_action_edge(AssessResponse(), [SimpleReflect()])
narrower.add_action_edge(SimpleReflect(), [StopAction()])
narrower.add_action_edge(RetrieveKnowledge(), [SimpleResponse()])
narrower.add_action_edge(SimpleResponse(), [AssessResponse()])
narrower.add_action_edge(AskFriendForHelp(embedding_model=get_embedding), [AssessResponse()])
