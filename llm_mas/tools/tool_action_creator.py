"""The tool action creator defines how an agent creates actions related to tools."""

from typing import override

from mcp import Tool

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.mas.agent import Agent
from llm_mas.mcp_client.connected_server import ConnectedServer


class ToolAction(Action):
    """An action that calls an external tool."""

    def __init__(self, tool: Tool, server: ConnectedServer) -> None:
        """Initialize the ToolAction with a specific tool."""
        name = tool.name.capitalize()
        description = tool.description or f"Calls the tool: {name}"
        params_schema = tool.inputSchema
        super().__init__(name=name, description=description, params_schema=params_schema)
        self.tool = tool
        self.server = server

    async def do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action by calling the tool."""
        # check params match schema
        if not params.matches_schema(self.params_schema):
            msg = f"Parameters do not match the tool's input schema: {self.tool.name}"
            raise ValueError(msg)

        # grab the tool manager from the context
        tool_manager = context.agent.tool_manager

        # find related server
        tool_res = await tool_manager.call_tool(self.tool.name, params.to_dict())

        # set the result
        result = ActionResult()
        result.set_param("tool_result", tool_res)
        result.set_param("tool_name", self.tool.name)
        return result


class ToolActionCreator:
    """A class to create actions related to tools based on the agent's context and needs."""

    def create_action(self, agent: Agent, tool: Tool, server: ConnectedServer) -> list[Action]:
        """Create an action for the given tool based on the agent's context."""
        msg = "Creating actions for tools is not implemented."
        raise NotImplementedError(msg)


class DefaultToolActionCreator(ToolActionCreator):
    """A default implementation of ToolActionCreator that creates a ToolAction for each tool."""

    @override
    def create_action(self, agent: Agent, tool: Tool, server: ConnectedServer) -> list[Action]:
        """Create a ToolAction for the given tool."""
        return [ToolAction(tool, server)]
