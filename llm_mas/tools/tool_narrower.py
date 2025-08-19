"""The tool narrower module defines how an context decides which tools are relevant."""

from typing import override

from mcp import Tool

from llm_mas.action_system.core.action_context import ActionContext


class ToolNarrower:
    """A class to narrow down the available tools based on the context's context and needs."""

    def narrow(self, context: ActionContext, tools: list[Tool]) -> list[Tool]:
        """Narrow down the tools based on the context's context."""
        msg = "Narrowing tools based on context's context is not implemented."
        raise NotImplementedError(msg)


class DefaultToolNarrower(ToolNarrower):
    """A default implementation of ToolNarrower that returns all tools."""

    @override
    def narrow(self, context: ActionContext, tools: list[Tool]) -> list[Tool]:
        """Return all tools without narrowing."""
        return tools


class SetToolNarrower(ToolNarrower):
    """A tool narrower that sets the tools to a specific list."""

    def __init__(self, tool_names: set[str]) -> None:
        """Initialize with a list of tool names to narrow down to."""
        self.tool_names = tool_names

    @override
    def narrow(self, context: ActionContext, tools: list[Tool]) -> list[Tool]:
        """Return only the tools that match the specified names."""
        return [tool for tool in tools if tool.name in self.tool_names]
