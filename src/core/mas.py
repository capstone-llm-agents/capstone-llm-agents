from enum import Enum
from core.agent import Agent
from core.chat import ChatHistory, ChatMessage
from core.query import Query
from core.entity import HumanUser
from core.communication_protocol import CommunicationProtocol


class MASResponse(Enum):
    """An enum representing the response of the MAS."""

    WAITING_FOR_USER_CONFIRMATION = "waiting_for_user_confirmation"
    AUTO_RUN_TIMEOUT = "auto_run_timeout"
    WAITING_FOR_USER_QUERY = "waiting_for_user_query"
    WAITING_FOR_USER_RESPONSE = "waiting_for_user_response"
    CONTINUE = "continue"


class MAS:
    """A class representing a Multi-Agent System (MAS)."""

    agents: dict[str, Agent]
    chat_history: ChatHistory

    def __init__(self, communication_protocol: CommunicationProtocol, user: HumanUser):
        self.agents = {}
        self.communication_protocol = communication_protocol

        self.chat_history = ChatHistory()

        self.user = user

        self.auto_run = True

        # the number of steps to run automatically before stopping
        self.max_auto_run_steps = 10

        self.step_count = 0

        # query to ask the user
        self.query_to_ask_user: Query | None = None

    def reset_steps(self):
        """Reset the step count."""
        self.step_count = 0

    def reset_chat_history(self):
        """Reset the chat history."""
        self.chat_history.clear()

    def reset(self):
        """Reset the MAS."""
        self.reset_steps()
        self.reset_chat_history()
        self.agents = {}

    def add_agent(self, agent: Agent):
        """Add an agent to the MAS."""
        self.agents[agent.name] = agent

    def get_agent(self, name: str) -> Agent:
        """Get an agent by name."""
        agent = self.agents.get(name)

        if agent is None:
            raise ValueError(f"Agent {name} not found in MAS.")
        return agent

    def get_agents(self) -> list[Agent]:
        """Get a list of agents in the MAS."""
        return list(self.agents.values())

    def handle_prompt_from_user(self, prompt: str):
        """Handle a prompt from the user."""
        message = ChatMessage(self.user, prompt)

        # add to chat history
        self.chat_history.add_message(message)

        # run the next step, executing the query
        self.run_next_step()

    def run_next_step(self) -> MASResponse:
        """Step through the MAS."""

        # clear the query to ask user
        self.clear_query_to_ask_user()

        # increment the step count if auto running
        if self.auto_run:
            self.step_count += 1

        # check auto run max steps
        if self.auto_run and self.step_count >= self.max_auto_run_steps:
            # if we are auto running, we need to stop
            return self.handle_auto_run_timeout()

        # create a query
        query = self.communication_protocol.create_query(
            self.chat_history, list(self.agents.values())
        )

        # check if it needs human input (e.g. can't automatically run)
        if query.who == self.user:
            # if it is the user, we need to wait for input
            self.set_query_to_ask_user(query)

            # reset auto run because we are waiting for user input
            self.reset_steps()

            return self.ask_user_query()

        # if we are not auto running, we need to wait for input to confirm
        if not self.auto_run:
            # ask the user to confirm to continue
            return self.wait_for_user_confirmation()

        # get agent from query
        agent = self.get_agent(query.who.name)

        # ask the agent
        response = agent.handle_query(query)

        # add the response to the chat history
        self.chat_history.add_message(response)

        # update the agent's memory
        agent.capabilties.memory.update_memory_from_chat_history(self.chat_history)

        # otherwise we can continue
        return self.continue_run()

    def resume_from_user_confirmation(self, query: Query):
        """Resume the MAS from user confirmation."""
        # get agent from query
        agent = self.get_agent(query.who.name)

        # ask the agent
        response = agent.handle_query(query)

        # add the response to the chat history
        self.chat_history.add_message(response)

    def set_query_to_ask_user(self, query: Query):
        """Set the query to ask the user."""
        self.query_to_ask_user = query

    def clear_query_to_ask_user(self):
        """Clear the query to ask the user."""
        self.query_to_ask_user = None

    def ask_user_query(self) -> MASResponse:
        """Ask the user a query."""
        return MASResponse.WAITING_FOR_USER_RESPONSE

    def wait_for_user_query(self) -> MASResponse:
        """Wait for the user to respond to a query."""
        return MASResponse.WAITING_FOR_USER_QUERY

    def handle_auto_run_timeout(self) -> MASResponse:
        """Handle the auto run timeout."""
        return MASResponse.AUTO_RUN_TIMEOUT

    def wait_for_user_confirmation(self) -> MASResponse:
        """Wait for user confirmation to continue."""
        return MASResponse.WAITING_FOR_USER_CONFIRMATION

    def continue_run(self) -> MASResponse:
        """Continue the run of the MAS."""
        return MASResponse.CONTINUE
