from capabilities.tools import Tool
from core.query import Query


class UnderlyingModel:
    """The underlying LLM that the agent uses."""

    def generate(self, query: Query) -> str:
        """Generate a response from the model."""
        raise NotImplementedError("This method should be overridden by subclasses.")

    def register_tool(self, tool: Tool):
        """Register a tool with the model."""
        raise NotImplementedError("This method should be overridden by subclasses.")
