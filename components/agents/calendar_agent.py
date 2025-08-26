"""Calendar agent"""

from components.actions.chat_history import RespondWithChatHistory
from components.actions.retrieve_knowledge import RetrieveKnowledge
from components.actions.simple_response import SimpleResponse
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

CALENDAR_AGENT = Agent("Calendar Agent", action_space, narrower, selector)


# add some actions
CALENDAR_AGENT.add_action(StopAction())
CALENDAR_AGENT.add_action(GetTools())


narrower.add_default_action(GetTools())

# add some edges
narrower.add_action_edge(RetrieveKnowledge(), [RespondWithChatHistory()])
narrower.add_action_edge(RespondWithChatHistory(), [StopAction()])
narrower.add_action_edge(GetTools(), [SimpleResponse()])
