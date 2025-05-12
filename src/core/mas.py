from core.agent import Agent
from core.chat import ChatHistory, ChatMessage, Query
from core.entity import HumanUser
from core.communication_protocol import CommunicationProtocol


class MAS:
    """A class representing a Multi-Agent System (MAS)."""

    agents: dict[str, Agent]
    chat_history: ChatHistory

    def __init__(self, communication_protocol: CommunicationProtocol):
        self.agents = {}
        self.communication_protocol = communication_protocol

        self.chat_history = ChatHistory()

        self.user = HumanUser("User", "The human user of the MAS")

        self.auto_run = True

        # the number of steps to run automatically before stopping
        self.max_auto_run_steps = 10

        self.step_count = 0

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

    def run_next_step(self):
        """Step through the MAS."""

        # increment the step count if auto running
        if self.auto_run:
            self.step_count += 1

        # check auto run max steps
        if self.auto_run and self.step_count >= self.max_auto_run_steps:
            # if we are auto running, we need to stop
            self.handle_auto_run_timeout()
            return

        # create a query
        query = self.communication_protocol.create_query(self.chat_history)

        # check if it needs human input (e.g. can't automatically run)
        if query.who == self.user:
            # if it is the user, we need to wait for input
            self.ask_user_query(query)
            return

        # if we are not auto running, we need to wait for input to confirm
        if not self.auto_run:
            # ask the user to confirm to continue
            self.wait_for_user_confirmation(query)

        # get agent from query
        agent = self.get_agent(query.who.name)

        # ask the agent
        response = agent.handle_query(query)

        # add the response to the chat history
        self.chat_history.add_message(response)

    def ask_user_query(self, query: Query):
        """Ask the user a query."""
        raise NotImplementedError("ask_user_query not implemented")

    def handle_auto_run_timeout(self):
        """Handle the auto run timeout."""
        raise NotImplementedError("handle_auto_run_timeout not implemented")

    def wait_for_user_confirmation(self, query: Query):
        """Wait for user confirmation to continue."""
        raise NotImplementedError("wait_for_user_confirmation not implemented")
