"""The calendar agent module demonstrates how to create a simple agent with actions and workflows."""

from components.actions.chat_history import RespondWithChatHistory
from components.actions.retrieve_knowledge import RetrieveKnowledge
from components.actions.simple_response import SimpleResponse
from components.actions.tools import GetParamsForToolCall, GetRelevantTools, GetTools, UpdateTools
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

WEATHER_AGENT = Agent(
    "WeatherAgent",
    "An assistant that helps manage and provide weather information.",
    action_space,
    narrower,
    selector,
    tool_manager,
)


# add some actions
WEATHER_AGENT.add_action(RespondWithChatHistory())
WEATHER_AGENT.add_action(StopAction())
WEATHER_AGENT.add_action(UpdateTools(tool_creator))
WEATHER_AGENT.add_action(GetTools(tool_creator))
WEATHER_AGENT.add_action(GetRelevantTools(tool_creator, embedding_model=ModelsAPI.get_embedding))
WEATHER_AGENT.add_action(GetParamsForToolCall(tool_creator))


narrower.add_default_action(UpdateTools(tool_creator))

# add some edges
narrower.add_action_edge(RetrieveKnowledge(), [RespondWithChatHistory(), SimpleResponse()])
narrower.add_action_edge(RespondWithChatHistory(), [StopAction()])
narrower.add_action_edge(SimpleResponse(), [StopAction()])
narrower.add_action_edge(UpdateTools(tool_creator), [GetTools(tool_creator)])
narrower.add_action_edge(
    GetTools(tool_creator), [GetRelevantTools(tool_creator, embedding_model=ModelsAPI.get_embedding)]
)
narrower.add_action_edge(
    GetRelevantTools(tool_creator, embedding_model=ModelsAPI.get_embedding), [GetParamsForToolCall(tool_creator)]
)
narrower.add_action_edge(GetParamsForToolCall(tool_creator), [])
