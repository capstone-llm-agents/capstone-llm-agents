"""Discovery agent for finding other users in the network."""

from components.actions.send_to_friend import SendToFriend
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

DISCOVERY_AGENT = Agent(
    "CalendarAgent",
    "An assistant that helps manage and schedule calendar events.",
    action_space,
    narrower,
    selector,
    tool_manager,
)


narrower.add_default_action(SendToFriend())

# add some edges
narrower.add_action_edge(SendToFriend(), [SimpleResponse()])
narrower.add_action_edge(SimpleResponse(), [StopAction()])
