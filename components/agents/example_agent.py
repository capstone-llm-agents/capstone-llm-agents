"""The example agent module demonstrates how to create a simple agent with actions and workflows."""

from components.actions.retrieve_knowledge import RetrieveKnowledge
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

EXAMPLE_AGENT = Agent(
    "Assistant",
    "An assistant that can interacts with the user to handle their requests.",
    action_space,
    narrower,
    selector,
    tool_manager,
)


# add some actions
EXAMPLE_AGENT.add_action(SimpleResponse())
# ASSISTANT_AGENT.add_action(RespondWithChatHistory())
EXAMPLE_AGENT.add_action(StopAction())
EXAMPLE_AGENT.add_action(RetrieveKnowledge())
# ASSISTANT_AGENT.add_action(UpdateTools(tool_creator))
# ASSISTANT_AGENT.add_action(GetTools(tool_creator))
# ASSISTANT_AGENT.add_action(GetRelevantTools(tool_creator))
# ASSISTANT_AGENT.add_action(GetParamsForToolCall(tool_creator))
# ASSISTANT_AGENT.add_action(ListFriends())

# narrower.add_default_action(AskFriendForHelp(embedding_model=get_embedding))
narrower.add_default_action(RetrieveKnowledge())

# add some edges
narrower.add_action_edge(RetrieveKnowledge(), [SimpleResponse()])
# narrower.add_action_edge(RespondWithChatHistory(), [StopAction()])
narrower.add_action_edge(SimpleResponse(), [StopAction()])
# narrower.add_action_edge(UpdateTools(tool_creator), [GetTools(tool_creator)])
# narrower.add_action_edge(GetTools(tool_creator), [GetRelevantTools(tool_creator)])
# narrower.add_action_edge(GetRelevantTools(tool_creator), [GetParamsForToolCall(tool_creator)])
# narrower.add_action_edge(GetParamsForToolCall(tool_creator), [])
# narrower.add_action_edge(ListFriends(), [SimpleResponse()])
# narrower.add_action_edge(AskFriendForHelp(embedding_model=get_embedding), [SimpleResponse()])
