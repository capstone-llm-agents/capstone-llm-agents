from core.capability import Capability


class Tool:
    """A class representing a tool that can be used by the agent."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def use(self):
        """Use the tool."""
        raise NotImplementedError("This method should be overridden by subclasses.")


class ToolsManager(Capability):
    """A class to manage tools for the agent."""

    tools: list[Tool]

    def __init__(self):
        super().__init__("tools_manager")
        self.tools = []

    def add_tool(self, tool: Tool):
        """Add a tool to the manager."""
        self.tools.append(tool)

    def get_all_tools(self) -> list[Tool]:
        """Get all tools."""
        return self.tools
