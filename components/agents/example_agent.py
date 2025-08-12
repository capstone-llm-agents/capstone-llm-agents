"""The example agent module demonstrates how to create a simple agent with actions and workflows."""

from components.actions.retrieve_knowledge import RetrieveKnowledge
from components.actions.simple_response import SimpleResponse
from llm_mas.action_system.base.actions.stop import StopAction
from llm_mas.action_system.base.narrowers.graph_narrower import GraphBasedNarrower
from llm_mas.action_system.base.selectors.random import RandomSelector
from llm_mas.action_system.core.action_space import ActionSpace
from llm_mas.mas.agent import Agent

action_space = ActionSpace()
narrower = GraphBasedNarrower()
selector = RandomSelector()

EXAMPLE_AGENT = Agent("ExampleAgent", action_space, narrower, selector)


# add some actions
EXAMPLE_AGENT.add_action(SimpleResponse())
EXAMPLE_AGENT.add_action(StopAction())
EXAMPLE_AGENT.add_action(RetrieveKnowledge())

narrower.add_default_action(RetrieveKnowledge())

# add some edges
narrower.add_action_edge(RetrieveKnowledge(), [SimpleResponse()])
narrower.add_action_edge(SimpleResponse(), [StopAction()])
