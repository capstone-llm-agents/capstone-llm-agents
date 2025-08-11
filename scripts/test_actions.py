"""The main entry point for the multi-agent system."""

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

agent = Agent("ExampleAgent", action_space, narrower, selector)

# add some actions
agent.add_action(SayHello())
agent.add_action(StopAction())

# workflow to say hello 3 times
workflow = Workflow("SayHelloWorkflow")
for _ in range(3):
    workflow.add_action(SayHello())
agent.add_action(workflow)

# default action
narrower.add_default_action(SayHello())
narrower.add_default_action(workflow)

# add some edges
narrower.add_action_edge(SayHello(), [StopAction()])
narrower.add_action_edge(workflow, [StopAction()])

# run the agent
agent.work()
