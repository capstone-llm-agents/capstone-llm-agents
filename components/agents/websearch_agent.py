"""The example agent module demonstrates how to create a simple agent with actions and workflows."""

from components.actions.chat_history import RespondWithChatHistory
from components.actions.websearch import WebSearch
from components.actions.website_summary import SummariseURL
from llm_mas.action_system.base.actions.stop import StopAction
from llm_mas.action_system.base.narrowers.graph_narrower import GraphBasedNarrower
from llm_mas.action_system.base.selectors.llm_selector import LLMSelector
from llm_mas.action_system.core.action_space import ActionSpace
from llm_mas.mas.agent import Agent
from llm_mas.model_providers.ollama.call_llm import call_llm
from llm_mas.tools.tool_manager import ToolManager
from llm_mas.tools.tool_narrower import ToolNarrower

action_space = ActionSpace()
narrower = GraphBasedNarrower()
selector = LLMSelector(call_llm)
tool_narrower = ToolNarrower()
tool_manager = ToolManager(tool_narrower)

WEBSEARCH_AGENT = Agent(
    "WebSearchAgent",
    "An assistant that can perform web searches and summarize web content.",
    action_space,
    narrower,
    selector,
    tool_manager,
)


# add some actions
WEBSEARCH_AGENT.add_action(WebSearch())
WEBSEARCH_AGENT.add_action(RespondWithChatHistory())
WEBSEARCH_AGENT.add_action(StopAction())
WEBSEARCH_AGENT.add_action(SummariseURL())


narrower.add_default_action(WebSearch())
narrower.add_default_action(RespondWithChatHistory())
narrower.add_default_action(SummariseURL())

# add some edges
narrower.add_action_edge(SummariseURL(), [StopAction()])
narrower.add_action_edge(RespondWithChatHistory(), [StopAction()])
narrower.add_action_edge(WebSearch(), [StopAction()])
