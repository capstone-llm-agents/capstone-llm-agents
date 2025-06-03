import random
from capabilities.communication import CommunicationInterface
from core.task import Task
from core.agent import Agent


class SimpleCommunicationInterface(CommunicationInterface):
    """A simple CommunicationInterface capability."""

    def task_is_suitable(self, task: Task, agent: Agent) -> float:
        """Returns a value betwene 0 and 1 indicating how well the agent can perform the task."""

        # Generate a random suitability score between 0 and 1
        score = random.uniform(0, 1)

        print(f"Agent {agent.name} scored {score:.2f} for task: {task.description}")

        return score
