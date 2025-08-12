"""The example agent module demonstrates how to create a simple agent with actions and workflows."""

from components.actions.say_hello import SayHello
from llm_mas.action_system.base.actions.stop import StopAction
from llm_mas.action_system.base.actions.workflow import Workflow
from llm_mas.action_system.base.narrowers.graph_narrower import GraphBasedNarrower
from llm_mas.action_system.base.selectors.random import RandomSelector
from llm_mas.action_system.core.action_space import ActionSpace
from llm_mas.mas.agent import Agent

action_space = ActionSpace()
narrower = GraphBasedNarrower()
selector = RandomSelector()

EXAMPLE_AGENT = Agent("ExampleAgent", action_space, narrower, selector)

# add some actions
EXAMPLE_AGENT.add_action(SayHello())
EXAMPLE_AGENT.add_action(StopAction())

# workflow to say hello 3 times
workflow = Workflow("SayHelloWorkflow")
for _ in range(3):
    workflow.add_action(SayHello())
EXAMPLE_AGENT.add_action(workflow)

# default action
narrower.add_default_action(SayHello())
narrower.add_default_action(workflow)

# add some edges
narrower.add_action_edge(SayHello(), [StopAction()])
narrower.add_action_edge(workflow, [StopAction()])
