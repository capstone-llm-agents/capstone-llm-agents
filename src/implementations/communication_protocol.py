from core.agent import Agent
from core.chat import ChatHistory, ChatMessage
from core.query import Query
from core.communication_protocol import CommunicationProtocol
from core.task import AnswerQueryTask


class BasicCommunicationProtocol(CommunicationProtocol):
    """A basic Communication Protocol."""

    def create_query(self, chat_history: ChatHistory, agents: list[Agent]) -> Query:
        """Create a new query from the chat history."""

        if len(agents) == 0:
            raise ValueError("No agents in the MAS. There must be at least one agent.")

        # last message
        last_message = chat_history.get_last_message()

        if last_message is None:
            # NOTE: Assumes that there is no chat, so the MAS should prompt the user

            # get the default assistant agent
            agent = self.get_assistant_agent(agents)

            return Query(agent, self.user, "Hello, how can I help you?")

        chosen_agent = None
        best_score: float = float("-inf")

        for agent in agents:

            # task
            task = self.get_task_from_message(last_message, agent)

            # agent interface
            comms_interface = agent.capabilties.communication

            score = comms_interface.task_is_suitable(task, agent)

            if score > best_score:
                best_score = score
                chosen_agent = agent

        assert chosen_agent is not None, "No suitable agent found for the task."

        return Query(last_message.who, chosen_agent, last_message.content)

    def get_assistant_agent(self, agents: list[Agent]) -> Agent:
        """Get the default assistant agent from the list of agents."""
        if len(agents) == 0:
            raise ValueError("No agents in the MAS. There must be at least one agent.")

        # TODO make sure that there is a way to specify the assistant agent and that it must exist

        # for now we get agent named "Assistant"
        for agent in agents:
            if agent.name == "Assistant":
                return agent

        # otherwise default to the first agent (arbitrary choice)
        return agents[0]

    def get_task_from_message(
        self, chat_message: ChatMessage, recipient: Agent
    ) -> AnswerQueryTask:
        """Get a task from a chat message."""
        return AnswerQueryTask(Query(chat_message.who, recipient, chat_message.content))
