from datetime import datetime
from capabilities.tools import Tool, ToolInput, ToolOutput


class CurrentDateTimeTool(Tool):
    def __init__(self):
        super().__init__(
            name="current_date_time",
            description="Returns the current date and time. Requires no input.",
        )

    def use(self, tool_input: ToolInput) -> ToolOutput:
        now = datetime.now().isoformat()
        return ToolOutput(self, now)


class WeekdayTool(Tool):
    def __init__(self):
        super().__init__(
            name="weekday",
            description="""
                Returns the day of the week.
                Requires the specific input of an ISO 8601 datetime string.
                (e.g., {'datetime': '2025-06-03T15:00:00'}).""",
        )

    def use(self, tool_input: ToolInput) -> ToolOutput:
        datetime_str = tool_input.args.get("datetime")
        if not datetime_str:
            return ToolOutput(self, "Error: 'datetime' argument is required.")

        try:
            dt = datetime.fromisoformat(datetime_str)
            weekday = dt.strftime("%A")
            return ToolOutput(self, weekday)
        except ValueError as e:
            return ToolOutput(self, f"Error parsing datetime: {e}")


class MathTool(Tool):
    def __init__(self):
        super().__init__(
            name="math_tool",
            description="""
            Evaluates a mathematical expression safely.
            Requires a valid mathematical 'expression' argument that can be executed by Python.
            (e.g., {'expression': }'2 + 2 * 3'}).
            Note: This tool uses Python's eval function, so be cautious with input to avoid security risks.
            """,
        )

    def use(self, tool_input: ToolInput) -> ToolOutput:
        expr = tool_input.args.get("expression", "")
        try:
            result = eval(expr, {"__builtins__": {}}, {})
        except Exception as e:
            result = str(e)
        return ToolOutput(self, result)
