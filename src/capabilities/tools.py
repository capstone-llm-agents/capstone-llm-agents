from __future__ import annotations

from typing import Any
from core.capability import Capability


class ToolInput:
    """A class representing the input for a tool."""

    def __init__(self, tool: Tool, args: dict[str, Any]):
        self.tool = tool
        self.args = args


class ToolOutput:
    """A class representing the output from a tool."""

    def __init__(self, tool: Tool, result: Any):
        self.tool = tool
        self.result = result


class Tool:
    """A class representing a tool that can be used by the agent."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def use(self, tool_input: ToolInput) -> ToolOutput:
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

    def get_tool_for_name(self, name: str) -> Tool | None:
        """Get a tool by its name."""
        for tool in self.tools:
            if tool.name == name:
                return tool

        return None

    def use_tool(self, tool: Tool, tool_input: ToolInput) -> ToolOutput:
        """Use a specific tool with the provided input."""
        return tool.use(tool_input)

    def get_tool_responses_for_query(self, query: str) -> list[ToolOutput]:
        """Get responses from all tools for a specific query."""
        relevant_tools = self.get_relevant_tools_for_query(query)
        print(
            f"Relevant tools for query '{query}': {[tool.name for tool in relevant_tools]}"
        )

        tool_outputs: list[ToolOutput] = []

        for tool in relevant_tools:
            tool_input = self.get_input_for_tool(tool, query)
            print(f"Tool '{tool.name}' input for query '{query}': {tool_input.args}")
            tool_output = self.use_tool(tool, tool_input)
            print(
                f"Tool '{tool.name}' output for query '{query}': {tool_output.result}"
            )
            tool_outputs.append(tool_output)

        return tool_outputs

    def get_relevant_tools_for_query(self, query: str) -> list[Tool]:
        """Get tools relevant to a specific query."""

        raise NotImplementedError(
            "This method should be implemented by subclasses to filter tools based on the query."
        )

    def get_input_for_tool(self, tool: Tool, query: str) -> ToolInput:
        """Get the input for a specific tool based on the query."""

        raise NotImplementedError(
            "This method should be implemented by subclasses to generate input for the tool."
        )
