"""The example agent module demonstrates how to create a simple agent with actions and workflows."""

from components.actions.chat_history import RespondWithChatHistory
from components.actions.retrieve_knowledge import RetrieveKnowledge
from components.actions.websearch import WebSearch
from components.actions.website_summary import SummariseURL
from components.actions.tools import GetTools
from llm_mas.action_system.base.actions.stop import StopAction
from llm_mas.action_system.base.narrowers.graph_narrower import GraphBasedNarrower
from llm_mas.action_system.base.selectors.llm_selector import LLMSelector
from llm_mas.action_system.core.action_space import ActionSpace
from llm_mas.mas.agent import Agent
from llm_mas.model_providers.ollama.call_llm import call_llm



action_space = ActionSpace()
narrower = GraphBasedNarrower()
selector = LLMSelector(call_llm)

WEBSEARCH_AGENT = Agent("WebSearch Agent", action_space, narrower, selector)


# add some actions
WEBSEARCH_AGENT.add_action(WebSearch())
WEBSEARCH_AGENT.add_action(RespondWithChatHistory())
WEBSEARCH_AGENT.add_action(StopAction())
WEBSEARCH_AGENT.add_action(SummariseURL())
WEBSEARCH_AGENT.add_action(GetTools())


narrower.add_default_action(WebSearch())
narrower.add_default_action(GetTools())
narrower.add_default_action(RespondWithChatHistory())
narrower.add_default_action(SummariseURL())

# add some edges
narrower.add_action_edge(SummariseURL(), [StopAction()])
#narrower.add_action_edge(RetrieveKnowledge(), [RespondWithChatHistory(), WebSearch()])
narrower.add_action_edge(RespondWithChatHistory(), [StopAction()])
narrower.add_action_edge(WebSearch(), [StopAction()])
narrower.add_action_edge(GetTools(), [WebSearch()])
