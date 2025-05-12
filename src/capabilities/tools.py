from core.capability import Capability


class Tool:
    """A class representing a tool that can be used by the agent."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def use(self):
        """Use the tool."""
        raise NotImplementedError("This method should be overridden by subclasses.")


class ToolRegister:
    """A class to register tools."""

    def register_tool(self, tool: Tool):
        """Register a tool."""
        raise NotImplementedError("This method should be overridden by subclasses.")


class ToolsManager(Capability):
    """A class to manage tools for the agent."""

    tools: list[Tool]

    def __init__(self, tool_register: ToolRegister):
        super().__init__("tools_manager")
        self.tools = []
        self.tool_register = tool_register

    def add_tool(self, tool: Tool):
        """Add a tool to the manager."""
        self.tools.append(tool)

    def get_all_tools(self) -> list[Tool]:
        """Get all tools."""
        return self.tools

    def register_tools(self):
        """Register all tools."""
        for tool in self.tools:
            self.tool_register.register_tool(tool)
