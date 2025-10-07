"""Actions that related to tools."""

import json
import logging
from typing import TYPE_CHECKING, override

import numpy as np
from mcp import Tool

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.logging.loggers import APP_LOGGER
from llm_mas.model_providers.api import ModelsAPI
from llm_mas.tools.tool_action_creator import ToolActionCreator
from llm_mas.utils.config.models_config import ModelType
from llm_mas.utils.embeddings import EmbeddingFunction, VectorSelector
from llm_mas.utils.json_parser import extract_json_from_response

if TYPE_CHECKING:
    from llm_mas.mcp_client.connected_server import ConnectedServer


class UpdateTools(Action):
    """An action that updates the list of available tools."""

    def __init__(self, tool_creator: ToolActionCreator) -> None:
        """Initialize the UpdateTools action."""
        super().__init__(description="Updates the list of available tools")
        self.tool_creator = tool_creator

    @override
    async def do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action by updating the list of tools."""
        servers = context.mcp_client.connected_servers

        tool_manager = context.agent.tool_manager

        new_servers: list[ConnectedServer] = [server for server in servers if not tool_manager.is_known_server(server)]

        if not new_servers:
            return ActionResult()

        new_tool_names: list[str] = []
        for server in new_servers:
            try:
                await tool_manager.init_tools_from_server(server)
            except ConnectionError as _:
                # TODO: log a warning or error  # noqa: TD003
                continue

            tools = tool_manager.get_tools_from_server(server)
            for tool in tools:
                new_tool_names.append(tool.name)
                actions = self.tool_creator.create_action(context.agent, tool, server)
                for action in actions:
                    context.agent.add_action_during_runtime(action)

        res = ActionResult()
        res.set_param("new_tools", new_tool_names)
        return res


class GetTools(Action):
    """An action that retrieves the list of available tools."""

    def __init__(self, tool_creator: ToolActionCreator) -> None:
        """Initialize the GetTools action."""
        super().__init__(description="Retrieves the list of available tools")
        self.tool_creator = tool_creator

    @override
    async def do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action by retrieving the list of tools."""
        tools = context.agent.tool_manager.get_all_tools()
        res = ActionResult()

        def convert_tool_to_dict(tool: Tool) -> dict:
            """Convert a Tool object to a dictionary."""
            return {
                "name": tool.name,
                "description": tool.description,
            }

        tools = [convert_tool_to_dict(tool) for tool in tools]

        res.set_param("tools", tools)

        APP_LOGGER.debug(f"Available tools: {tools}")

        return res


class GetRelevantTools(Action):
    """An action that retrieves tools relevant to the current context."""

    def __init__(
        self,
        tool_creator: ToolActionCreator,
        embedding_model: EmbeddingFunction,
        vector_selector: VectorSelector | None = None,
    ) -> None:
        """Initialize the GetRelevantTools action."""
        super().__init__(description="Retrieves tools relevant to the current context")
        self.tool_creator = tool_creator
        self.embedding_model = embedding_model
        self.vector_selector = vector_selector or VectorSelector()

    @override
    async def do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action by retrieving relevant tools."""
        # assumes that the context has a method to get relevant tools
        tools = context.last_result.get_param("tools")

        chat_history = context.conversation.get_chat_history()

        messages = chat_history.messages

        last_message = messages[-1] if messages else None

        if not last_message:
            msg = "No chat history available to respond to."
            raise ValueError(msg)

        embedding_target = f"{last_message.content}"

        logging.getLogger("textual_app").info("Finding relevant tools for: %s", embedding_target)

        user_embedding = np.array(await self.embedding_model(embedding_target, ModelType.EMBEDDING))

        tools = context.agent.tool_manager.get_all_tools()

        tool_embeddings: list[tuple[Tool, np.ndarray]] = [
            (tool, np.array(await self.embedding_model(f"{tool.name} {tool.description or ''}", ModelType.EMBEDDING)))
            for tool in tools
        ]

        # select best tool
        actual_tool, _ = self.vector_selector.select(user_embedding, tool_embeddings)

        def convert_tool_to_dict(tool: Tool) -> dict:
            """Convert a Tool object to a dictionary."""
            return {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.inputSchema,
            }

        tool_dict = convert_tool_to_dict(actual_tool)

        res = ActionResult()
        res.set_param("query", last_message.content)
        res.set_param("relevant_tools", [tool_dict])

        if not tool_dict:
            res.set_param("tool_name", None)
            return res

        res.set_param("tool_name", tool_dict["name"])

        return res


class GetParamsForToolCall(Action):
    """An action that retrieves parameters for calling a tool using an LLM."""

    def __init__(self, tool_creator: ToolActionCreator) -> None:
        """Initialize the GetParamsForToolCall action."""
        super().__init__(description="Retrieves parameters for calling a tool using an LLM")
        self.tool_creator = tool_creator

    @override
    async def do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action by retrieving parameters for calling a tool."""
        tool_name = context.last_result.get_param("tool_name")

        if not tool_name:
            msg = "No tool name provided in the last result."
            raise ValueError(msg)

        tool_manager = context.agent.tool_manager

        tools = tool_manager.get_all_tools()
        tool = next((t for t in tools if t.name == tool_name), None)

        if not tool:
            msg = f"Tool '{tool_name}' not found."
            raise ValueError(msg)

        # ask llm for parameters
        last_message = self.get_last_message_content(context)

        prompt = f"""You are an expert at using tools. Given the following prompt:
        {last_message}
        Generate the parameters for the tool '{tool.name}' with the following input schema:
        {json.dumps(tool.inputSchema, indent=4)}
        Respond ONLY with the parameters in JSON format, like this:
        ```json
        {{
            "param1": "value1",
            "param2": "value2"
        }}
        ```
        If no parameters are needed, respond with an empty object:
        ```json
        {{}}
        ```
        """

        response = await ModelsAPI.call_llm(prompt, ModelType.DEFAULT)

        content = extract_json_from_response(response)

        try:
            params_dict = json.loads(content)
        except json.JSONDecodeError as e:
            msg = f"Failed to parse JSON from response: {content}"
            raise ValueError(msg) from e

        # check if params match schema
        action_params = ActionParams()
        for key, value in params_dict.items():
            action_params.set_param(key, value)

        if not action_params.matches_schema(tool.inputSchema):
            msg = f"Parameters do not match the tool's input schema: {tool.name}"
            raise ValueError(msg)

        res = ActionResult()
        res.set_param("query", last_message)
        res.set_param("tool_name", tool.name)
        res.set_param("params", action_params.to_dict())
        return res
