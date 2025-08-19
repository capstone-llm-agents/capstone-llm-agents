"""Actions that related to tools."""

from typing import TYPE_CHECKING, override

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.tools.tool_action_creator import ToolActionCreator

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
