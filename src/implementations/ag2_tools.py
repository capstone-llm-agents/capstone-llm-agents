from datetime import datetime
from capabilities.tools import Tool, ToolInput, ToolOutput, ToolOutputError


class CurrentDateTimeTool(Tool):
    def __init__(self):
        super().__init__(
            name="current_date_time",
            description="Returns the current date and time.",
            input_description="This tool does not require any input.",
        )

    def use(self, tool_input: ToolInput) -> ToolOutput:
        now = datetime.now().isoformat()
        return ToolOutput(self, now, tool_input)


class WeekdayTool(Tool):
    def __init__(self):
        super().__init__(
            name="weekday",
            description="""Returns the day of the week.""",
            input_description="""Requires the specific input of an ISO 8601 datetime string. (e.g., {'datetime': '2025-06-03T15:00:00'}).""",
        )

    def use(self, tool_input: ToolInput) -> ToolOutput:
        datetime_str = tool_input.args.get("datetime")
        if not datetime_str:
            return ToolOutputError(
                self, "Missing 'datetime' argument in input.", tool_input
            )

        try:
            dt = datetime.fromisoformat(datetime_str)
            weekday = dt.strftime("%A")
            return ToolOutput(self, weekday, tool_input)
        except ValueError as e:
            return ToolOutputError(self, f"Error parsing datetime: {e}", tool_input)


class MathTool(Tool):
    def __init__(self):
        super().__init__(
            name="math_tool",
            description="""Evaluates a mathematical expression and returns the result.""",
            input_description="""
            Requires a valid mathematical 'expression' argument that can be executed by Python.
            (e.g., {'expression': '2 + 2 * 3'}).
            Note: This tool uses Python's eval function, so be cautious with input to avoid security risks.""",
        )

    def use(self, tool_input: ToolInput) -> ToolOutput:
        expr = tool_input.args.get("expression", "")
        try:
            result = eval(expr, {"__builtins__": {}}, {})
        except Exception as e:
            result = str(e)
        return ToolOutput(self, result, tool_input)
