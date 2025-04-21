"""Module to define the MAS Agent class and its components."""

from mas.tool import Tool


class MASAgent:
    """A class representing an agent in the Multi-Agent System (MAS)."""

    def __init__(self, name: str, description: str):
        """
        Initialise the MASAgent with a name.

        Args:
            name (str): The name of the agent.
            description (str): The description of the agent.
        """
        self.name = name
        """The name of the agent."""
        self.description = description
        """The description of the agent."""

        self.tools: list[Tool] = []
        """A list of tools that the agent can use to perform tasks."""

        self.tool_lookup: dict[str, Tool] = {}
        """A dictionary to look up tools by their name."""

    def add_tool(self, tool: Tool):
        """Add a tool to the agent's list of tools.

        Args:
            tool (Tool): The tool to add.

        """
        # check if tool is already added
        if tool.name in self.tool_lookup:
            raise ValueError(f"Tool {tool.name} already added to agent {self.name}")

        self.tools.append(tool)
        self.tool_lookup[tool.name] = tool

    def register_tools(self):
        """Register multiple tools with the agent."""
        for tool in self.tools:
            self.register_tool(tool)

    def register_tool(self, tool: Tool):
        """Register a tool with the agent.

        Args:
            tool (Tool): The tool to register.

        """
        raise NotImplementedError(
            "This method should be implemented in a subclass of MASAgent."
        )

    def ask(self, prompt: str):
        """Prompt the agent.

        Args:
            prompt (str): The prompt to send to the agent.

        """
        raise NotImplementedError(
            "This method should be implemented in a subclass of MASAgent."
        )
