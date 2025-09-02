"""The tool action creator defines how an agent creates actions related to tools."""

import logging
from typing import Any, override

from mcp import Tool
from mcp.types import ContentBlock, TextContent

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
        name = tool.name
        description = tool.description or f"Calls the tool: {name}"
        params_schema = tool.inputSchema
        super().__init__(name=name, description=description, params_schema=params_schema)
        self.tool = tool
        self.server = server

    async def do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action by calling the tool."""
        # TODO: Move to a different logger  # noqa: TD003
        logging.getLogger("textual_app").info("Calling tool: %s with params: %s", self.tool.name, params.to_dict())
        logging.getLogger("textual_app").info("Context: %s", context.last_result.as_json_pretty())

        passed_in: dict = context.last_result.get_param("params")

        if not passed_in:
            msg = "No parameters passed in for the tool action."
            raise ValueError(msg)

        params = ActionParams()
        for key, value in passed_in.items():
            params.set_param(key, value)

        # check params match schema
        if not params.matches_schema(self.params_schema):
            msg = f"Parameters do not match the tool's input schema: {self.tool.name}"
            raise ValueError(msg)

        # grab the tool manager from the context
        tool_manager = context.agent.tool_manager

        # find related server
        tool_res = await tool_manager.call_tool(self.tool.name, params.to_dict())

        serializable = [self.serialize_content(content) for content in tool_res]

        # set the result
        result = ActionResult()

        result.set_param("query", context.last_result.get_param("query"))
        result.set_param("tool_result", serializable)
        result.set_param("tool_name", self.tool.name)
        return result

    def serialize_content(self, content: ContentBlock) -> Any:  # noqa: ANN401
        """Serialize the content of the action."""
        # TextContent | ImageContent | AudioContent | ResourceLink | EmbeddedResource

        if isinstance(content, TextContent):
            return content.text

        msg = f"Serializing content of type {type(content)} is not supported."
        raise NotImplementedError(msg)


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
