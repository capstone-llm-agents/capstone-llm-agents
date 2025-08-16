"""The example agent module demonstrates how to create a simple agent with actions and workflows."""

from components.actions.chat_history import RespondWithChatHistory
from components.actions.retrieve_knowledge import RetrieveKnowledge
from components.actions.simple_response import SimpleResponse
from llm_mas.action_system.base.actions.stop import StopAction
from llm_mas.action_system.base.narrowers.graph_narrower import GraphBasedNarrower
from llm_mas.action_system.base.selectors.llm_selector import LLMSelector
from llm_mas.action_system.core.action_space import ActionSpace
from llm_mas.mas.agent import Agent
from llm_mas.model_providers.ollama.call_llm import call_llm

action_space = ActionSpace()
narrower = GraphBasedNarrower()
selector = LLMSelector(call_llm)

EXAMPLE_AGENT = Agent("Assistant", action_space, narrower, selector)


# add some actions
# EXAMPLE_AGENT.add_action(SimpleResponse())
EXAMPLE_AGENT.add_action(RespondWithChatHistory())
EXAMPLE_AGENT.add_action(StopAction())
EXAMPLE_AGENT.add_action(RetrieveKnowledge())


narrower.add_default_action(RespondWithChatHistory())
narrower.add_default_action(RetrieveKnowledge())

# add some edges
narrower.add_action_edge(RetrieveKnowledge(), [RespondWithChatHistory()])
narrower.add_action_edge(RespondWithChatHistory(), [StopAction()])
