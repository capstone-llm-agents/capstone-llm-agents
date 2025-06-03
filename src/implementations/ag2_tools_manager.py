from autogen import ConversableAgent
from app import App
from capabilities.tools import Tool, ToolInput, ToolsManager
import json
import re


class AG2ToolsManager(ToolsManager):
    """Tool manager that uses an LLM agent to select tools and generate inputs."""

    def __init__(self, app: App):
        super().__init__()
        self.app = app
        self.selector_agent = ConversableAgent(
            name="ToolSelectorAgent",
            system_message="You are an expert assistant that selects which tools are most relevant to a user query.",
            llm_config=app.config.get_llm_config(),
        )
        self.input_agent = ConversableAgent(
            name="ToolInputGeneratorAgent",
            system_message="You are a tool input generator. Given a tool's name, description, and a user query, produce a JSON object of arguments suitable for that tool.",
            llm_config=app.config.get_llm_config(),
        )

    def extract_json_from_response(self, response: str):
        """Extract and parse JSON from a string, removing markdown formatting if needed."""
        # Remove ```json ... ``` or ``` ... ``` blocks
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            json_str = response.strip()

        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return {}  # or raise/log error

    def get_relevant_tools_for_query(self, query: str) -> list[Tool]:
        """Use LLM to select relevant tools based on a user query."""
        tool_descriptions = [f"{tool.name}: {tool.description}" for tool in self.tools]

        prompt = (
            "User Query:\n"
            f"{query}\n\n"
            "Available Tools:\n" + "\n".join(tool_descriptions) + "\n\n"
            'Which tools are relevant to the query? Return only a list of tool names as JSON, e.g. ["tool_name_1", "tool_name_2"]\n'
            "If no tools are relevant, return an empty list: []\n"
            "Be very specific and only include tools that are directly relevant to the query.\n"
        )

        # Must wrap prompt in a message dict
        messages = [{"role": "user", "content": prompt}]

        response = self.selector_agent.generate_reply(messages)
        tool_names = self.extract_json_from_response(response["content"])

        return [tool for tool in self.tools if tool.name in tool_names]

    def get_input_for_tool(self, tool: Tool, query: str) -> ToolInput:
        """Use LLM to generate input args for a tool based on a user query."""
        prompt = (
            f"Tool Name: {tool.name}\n"
            f"Tool Description: {tool.description}\n"
            f"User Query: {query}\n\n"
            "Return a JSON object with the input arguments for this tool. "
            "NEVER under ANY circumstances include markdown formatting, backticks, or labels like 'json'. "
            "Output only raw JSON. For example:\n"
            "{ 'property': 'value' }"
        )

        # Must wrap prompt in a message dict
        messages = [{"role": "user", "content": prompt}]

        response = self.input_agent.generate_reply(messages)
        args = self.extract_json_from_response(response["content"])

        return ToolInput(tool=tool, args=args)
