import random

from autogen import ConversableAgent
from pydantic import BaseModel
from capabilities.communication import CommunicationInterface
from core.task import AnswerQueryTask, Task
from core.agent import Agent
from models.ag2_model import AG2Model


class SuitabilityScore(BaseModel):
    """A suitability score for a task."""

    score: float


class SimpleCommunicationInterface(CommunicationInterface):
    """A simple CommunicationInterface capability."""

    def task_is_suitable(self, task: Task, agent: Agent) -> float:
        """Returns a value betwene 0 and 1 indicating how well the agent can perform the task."""

        # instead ask another agent to evaluate the suitability of the task for the agent

        llm_config = {
            "api_type": "ollama",
            "model": "gemma3",
            "response_format": SuitabilityScore,
        }

        evaluator_agent = ConversableAgent(
            name="Evaluator",
            description="evaluates the suitability of tasks for other agents",
            llm_config=llm_config,
        )

        # TODO hack
        assert isinstance(task, AnswerQueryTask), "Task must be an AnswerQueryTask."

        prompt = f"""
        Evaluate the suitability of the following task for the agent:

        '{task.query.content}'

        Agent Name: {agent.name}
        Agent Description: {agent.description}

        Score them a scale from 1 to 10, where 1 means not suitable at all and 10 means perfectly suitable.
        Any queries that any agent could do should be scored around 2.
        To score high the agent must have specific knowledge or skills that are relevant to the task.
        """

        reply = evaluator_agent.generate_reply([{"role": "user", "content": prompt}])

        content = reply["content"]

        # convert to model
        suitability_score = SuitabilityScore.model_validate_json(content)

        score = suitability_score.score

        print(f"Agent {agent.name} scored {score:.2f} for task: {task.description}")

        return score
