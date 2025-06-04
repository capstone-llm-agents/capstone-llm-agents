from core.agent import Agent
from core.chat import ChatHistory, ChatMessage
from core.entity import HumanUser
from core.query import Query, QueryResponse
from core.communication_protocol import CommunicationProtocol
from core.space import MainSpace, Space, UserSpace
from core.task import AnswerQueryTask
from implementations.communication_interface import SimpleCommunicationInterface


class BasicCommunicationProtocol(CommunicationProtocol):
    """A basic Communication Protocol."""

    # A mapping of agents to their respective spaces.
    agent_space_dict: dict[Agent, list[Space]] = {}

    def __init__(self, user: HumanUser, user_space: UserSpace, main_space: MainSpace):
        super().__init__(user)

        self.user_space = user_space
        self.main_space = main_space

    def bind_user_space_history(self, chat_history: ChatHistory):
        """Bind the user space chat history to the provided chat history."""
        self.user_space.chat_history = chat_history

    def create_query(self, chat_history: ChatHistory, agents: list[Agent]) -> Query:
        """Create a new query from the chat history and available agents."""
        if len(agents) == 0:
            raise ValueError("No agents in the MAS. There must be at least one agent.")

        assistant_agent = self.get_assistant_agent()

        last_message = chat_history.get_last_message()

        # new chat, the agent can start the conversation
        if last_message is None:
            return Query(assistant_agent, self.user, "Hello, how can I help you?")

        assert last_message.who == self.user, "Last message must be from the user."

        # if the last message is from the user, we create a query for the assistant agent
        return Query(
            last_message.who,
            assistant_agent,
            last_message.content,
        )

    def get_most_suitable_agent_for_query(
        self, agents: list[Agent], query: Query
    ) -> Agent:
        """Get the most suitable agent from the list of agents."""
        if len(agents) == 0:
            raise ValueError("No agents available to handle the query.")

        best_agent = None
        best_score = float("-inf")

        task = AnswerQueryTask(query)

        for agent in agents:
            interface = agent.capabilties.communication

            # TODO hack
            assert isinstance(interface, SimpleCommunicationInterface)

            score = interface.task_is_suitable(task, agent)

            if score > best_score:
                best_score = score
                best_agent = agent

        assert best_agent is not None, "No suitable agent found for the query."

        return best_agent

    def handle_query(self, query: Query) -> QueryResponse:
        """Handle a query and return a response."""

        agent = query.recipient

        if not isinstance(agent, Agent):
            raise ValueError("Query recipient must be an Agent.")

        # If the recipient is not the assistant agent, we will send the query to the assistant agent

        # The variations are:
        # U -> As (us)
        # As -> U (us) * this is implicitly handled by the MAS
        # As -> Any (ms)
        # Any -> As (ms)

        assistant_agent = self.get_assistant_agent()
        other_agents = [
            agent for agent in self.main_space.get_agents() if agent != assistant_agent
        ]

        # for now we assume that sender is always the user, and recipient is always the assistant agent

        self.main_space.add_chat_message(
            ChatMessage(
                assistant_agent,
                f"Who is most suited to handle this query? {query.content}",
            )
        )

        # get the most suitable agent for the query
        suitable_agent = self.get_most_suitable_agent_for_query(other_agents, query)

        self.main_space.add_chat_message(
            ChatMessage(
                suitable_agent,
                "I will handle the task.",
            )
        )

        # suitable agent handles the query
        new_query = Query(assistant_agent, suitable_agent, query.content)

        response = suitable_agent.handle_query(new_query)

        # remap to assistant agent
        return QueryResponse(assistant_agent, response.content)

    def get_assistant_agent(self) -> Agent:
        """Get the default assistant agent from the list of agents."""
        if (
            self.main_space.assistant_agent is None
            or self.user_space.assistant_agent is None
        ):
            raise ValueError("No assistant agent set in the MAS.")

        return self.main_space.assistant_agent

    def get_task_from_message(
        self, chat_message: ChatMessage, recipient: Agent
    ) -> AnswerQueryTask:
        """Get a task from a chat message."""
        return AnswerQueryTask(Query(chat_message.who, recipient, chat_message.content))

    def add_agent(self, agent: Agent):
        """Add an agent to the communication protocol."""
        # add agent to dict
        if agent not in self.agent_space_dict:
            self.agent_space_dict[agent] = []

        if agent.is_assistant_agent():
            self.main_space.assistant_agent = agent
            self.user_space.assistant_agent = agent
            self.agent_space_dict[agent].append(self.user_space)

        self.main_space.add_entity(agent)
        self.agent_space_dict[agent].append(self.main_space)
