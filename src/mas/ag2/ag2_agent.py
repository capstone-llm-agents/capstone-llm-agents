"""Module for an agent in a MAS using the Autogen2 framework."""

import json
from autogen import ConversableAgent, LLMConfig, register_function
from pydantic import BaseModel

from mas.tool import Tool
from mas.agent import MASAgent


class AG2MASAgent(MASAgent):
    """A class representing an agent in a Multi-Agent System (MAS) using the Autogen2 framework."""

    def __init__(
        self,
        # TODO use AG2Template to build agent, group chat with agents, or swarm
        name: str,
        description: str,
        llm_config: LLMConfig,
        system_message: str | None = None,
    ):
        """
        Initialise the AG2MASAgent with a name.

        Args:
            name (str): The name of the agent.
            description (str): The description of the agent.
            llm_config (LLMConfig): The LLM configuration for the agent.
            system_message (str | None): The system message for the agent. Defaults to description if None.
        """
        super().__init__(name, description)

        # default to description
        if system_message is None:
            system_message = description

        # copy llm_config
        copy_llm_config: LLMConfig = llm_config.copy()

        response_format: None | type[BaseModel] = None

        # set response format
        copy_llm_config["response_format"] = response_format

        self.llm_config = copy_llm_config
        """The LLM configuration for the agent."""

        self.response_format = response_format
        """The response format for the agent."""

        self.response_format = response_format
        """The response format for the agent."""

        self.system_message = system_message
        """The system message for the agent."""

        # create ag2 agent
        self.ag2_agent = ConversableAgent(
            name=name,
            description=description,
            system_message=system_message,
            llm_config=copy_llm_config,
        )

    def recreate_llm_config(self):
        """Recreate the LLM configuration for the agent."""
        # copy llm_config
        copy_llm_config = self.llm_config.copy()

        # set response format
        copy_llm_config["response_format"] = self.response_format

        self.llm_config = copy_llm_config

    def recreate_agent(self):
        """Recreate the agent with the current LLM configuration."""

        # recreate llm config
        self.recreate_llm_config()

        self.ag2_agent = ConversableAgent(
            name=self.name,
            description=self.description,
            system_message=self.system_message,
            llm_config=self.llm_config,
        )

    # TODO: This is a hack. It recreates the agent with the new response format.
    # This may have unintended consequences which we are currently unaware of.
    def set_response_format(self, response_format: type[BaseModel]):
        """Set the response format for the agent.

        Args:
            response_format (BaseModel): The response format for the agent.

        """
        self.response_format = response_format

        # recreate agent
        self.recreate_agent()

    def register_tool(self, tool: Tool):
        """Register a tool with the agent.

        Args:
            tool (Tool): The tool to register.
        Raises:
            ValueError: If the tool executor is not an AG2MASAgent.

        """

        executor = tool.get_executor()

        # check if is AG2MASAgent
        if not isinstance(executor, AG2MASAgent):
            raise ValueError(f"Tool executor must be AG2MASAgent, got {type(executor)}")

        register_function(
            f=tool.func,
            caller=self.ag2_agent,
            executor=executor.ag2_agent,
            name=tool.name,
            description=tool.description,
        )

    # TODO you can do multiple prompts in a single call
    # so we need to change it to be a list of prompts
    # and a Prompt obj cause there are settings ({ message: "", role: "user/system" })
    # and a Chat obj cause there are other settings (max_turns, recipient)
    def ask(self, prompt: str):
        """Prompt the agent.

        Args:
            prompt (str): The prompt to send to the agent.

        """
        # TODO abstract out details

        chat_result = self.ag2_agent.initiate_chat(
            recipient=self.ag2_agent,
            max_turns=1,
            message={
                "role": "user",
                "content": prompt,
            },
        )

        # TODO refactor out to get_last_message() not necessarily .summary
        last_message = chat_result.summary

        # load JSON
        json_data = json.loads(last_message)

        # TODO refactor out response_format

        # convert to pydantic model
        return self.ag2_agent.llm_config["response_format"](**json_data)
