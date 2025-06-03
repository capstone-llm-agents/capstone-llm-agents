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
        """Use LLM to select relevant tools based on a user query using k-shot prompting."""
        tool_descriptions = [f"{tool.name}: {tool.description}" for tool in self.tools]

        examples = """
    Example 1:
    User Query: "Translate this text from English to French"
    Available Tools:
    - translator: Translates text between languages
    - calculator: Solves math expressions
    Relevant Tools: ["translator"]

    Example 2:
    User Query: "What is 5 + 7?"
    Available Tools:
    - translator: Translates text between languages
    - calculator: Solves math expressions
    Relevant Tools: ["calculator"]

    Example 3:
    User Query: "How do I cook pasta?"
    Available Tools:
    - translator: Translates text between languages
    - calculator: Solves math expressions
    Relevant Tools: []

    Example 4:
    User Query: "Translate 'What is 8 times 7?' into Spanish and then solve it."
    Available Tools:
    - translator: Translates text between languages
    - calculator: Solves math expressions
    Relevant Tools: ["translator", "calculator"]

    Be precise. Do not include tools unless they are obviously required to answer the query.
    Only include multiple tools if the query explicitly requires more than one type of action.
        """

        prompt = (
            examples + f"\n\nUser Query: {query}\n"
            "Available Tools:\n" + "\n".join(tool_descriptions) + "\n\n"
            'Which tools are relevant to the query? Return only a list of tool names as JSON, e.g. ["tool_name_1", "tool_name_2"]\n'
            "If no tools are relevant, return an empty list: []\n"
            "Be specific and avoid guessing. Only include tools if they are necessary for answering the query."
        )

        messages = [{"role": "user", "content": prompt}]
        response = self.selector_agent.generate_reply(messages)

        tool_names = self.extract_json_from_response(response["content"])

        return [tool for tool in self.tools if tool.name in tool_names]

    def get_input_for_tool(self, tool: Tool, query: str) -> ToolInput:
        """Use LLM to generate input args for a tool based on a user query, using k-shot prompting."""

        # You can tailor these examples to match your real tools
        examples = """
    Example 1:
    Tool Name: weather_lookup
    Tool Description: Returns the current weather for a given city.
    User Query: What's the weather in Tokyo?
    Tool Input: { "city": "Tokyo" }

    Example 2:
    Tool Name: define_word
    Tool Description: Looks up the dictionary definition of a word.
    User Query: Define the word 'serendipity'.
    Tool Input: { "word": "serendipity" }

    Example 3:
    Tool Name: calculator
    Tool Description: Solves simple math expressions.
    User Query: What is 12 * 8 + 3?
    Tool Input: { "expression": "12 * 8 + 3" }

    Instructions:
    - ONLY return a raw JSON object.
    - Do NOT include any markdown, backticks, or explanation.
    - If you’re unsure about the correct arguments, make a best guess based on the query.
    - Only use fields that are documented or obvious from the description.
    """

        prompt = (
            examples + f"\n\nTool Name: {tool.name}\n"
            f"Tool Description: {tool.description} {tool.input_description}\n"
            f"User Query: {query}\n"
            "Tool Input: "
        )

        messages = [{"role": "user", "content": prompt}]
        response = self.input_agent.generate_reply(messages)
        print(f"Tool input response: {response['content']}")
        args = self.extract_json_from_response(response["content"])

        return ToolInput(tool=tool, args=args)
