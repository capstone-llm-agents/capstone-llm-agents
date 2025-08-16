"""Actions that related to tools."""

from typing import override

from mcp import Tool

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult


class GetTools(Action):
    """An action that retrieves the available tools."""

    def __init__(self) -> None:
        """Initialize the GetTools action."""
        super().__init__(description="Retrieves the available tools.")

    @override
    async def do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action by retrieving the tools."""
        servers = context.mcp_client.connected_servers

        tools: list[Tool] = []
        for server in servers:
            async with server.connect() as session:
                tools.extend(await server.list_tools(session))

        res = ActionResult()
        res.set_param("tools", tools)

        return res
