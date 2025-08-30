"""Test server to connect to the LLM MAS client."""

import functools
import logging
import traceback
from collections.abc import Callable
from datetime import datetime
from typing import Any, TypeVar, cast

import uvicorn
from autogen import ConversableAgent
from calendar_functions import convert_ics_to_text, create_ics_file
from mcp.server import Server
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Mount, Route

llm_config = {
    "api_type": "ollama",
    "model": "gemma3",
}

file_handler_agent = ConversableAgent(
    name="file_handler",
    system_message="Your job is to assist the user with their tasks.",
    llm_config=llm_config,
    human_input_mode="NEVER",
)

mcp = FastMCP("SSE - Calendar Tools Server")


F = TypeVar("F", bound=Callable[..., Any])


logger = logging.getLogger("mcp.tools")


def safe_tool[F: Callable[..., Any]](func: F) -> F:
    """Wrap MCP tool functions with error handling."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        try:
            return func(*args, **kwargs)
        except Exception as e:
            tb = traceback.format_exc()
            msg = f"Error in tool {func.__name__}: {e}\n{tb}"
            logger.exception(msg)
            raise

    return cast("F", wrapper)


@mcp.tool(name="CreateCalendar")
@safe_tool
def create_ics_calendar(prompt: str, ics_file: str = "./calendars/test_calendar.ics") -> str:
    """Generate a calendar schedule from a task prompt and write it to an ICS file."""
    current_date = datetime.now().date()

    prompt_template = f"""
    Break down the following tasks into realistic time frames, using the provided start time as a reference.

    Tasks: {prompt}
    Current Date: {current_date}

    Respond with a structured schedule for a calendar file:
    - Task
    - Date
    - Description
    - Start
    - End

    Use 24-hour notation. If no date is specified, use the current date.
    Example:
    1. Task: Research for Report
       Date: 2022-07-13
       Description: Research reliable details online
       Start: 09:00
       End: 09:30
    """

    plan = file_handler_agent.generate_reply(messages=[{"role": "user", "content": prompt_template}])
    print("### New Calendar Content ###")
    print(plan["content"])

    create_ics_file(plan["content"], ics_file)
    return plan["content"]


@mcp.tool(name="ReadCalendar")
@safe_tool
def read_calendar(file_name: str = "./calendars/test_calendar.ics") -> str:
    """Read an ICS file and return a human-readable task list."""
    calendar_content = convert_ics_to_text(file_name)

    prompt = f"""
    Explain the tasks, dates, and times in the following ICS calendar:

    {calendar_content}

    - Convert all times to 24-hour format
    - Convert from UTC to the local timezone
    - Use this format:
      1. Task: Example Task
         Date: 2022-07-13
         Description: Example description
         Start: 09:00
         End: 09:30
    """

    result = file_handler_agent.generate_reply(messages=[{"role": "user", "content": prompt}])
    print("### Calendar Interpretation ###")
    print(result["content"])
    return result["content"]


@mcp.tool(name="UpdateCalendar")
def create_ics_calendar_with_context(
    prompt: str,
    file_name_read: str = "./calendars/test_calendar.ics",
    file_name_write: str = "./calendars/test_calendar.ics",
) -> str:
    """Create a new calendar schedule considering existing events."""
    current_date = datetime.now().date()
    existing_events = convert_ics_to_text(file_name_read)

    extracted_prompt = f"""
    Break down the following tasks into realistic time frames, using the provided start time as a reference.

    Tasks: {prompt}
    Current Date: {current_date}
    Existing Plans: {existing_events}

    Requirements:
    - Do not overlap with existing plans
    - Include all existing plans in the new schedule
    - Use 24-hour time
    - Only specify a date if explicitly mentioned, otherwise use the current date
    """

    result = file_handler_agent.generate_reply(messages=[{"role": "user", "content": extracted_prompt}])
    print("### Updated Calendar Content ###")
    print(result["content"])

    create_ics_file(result["content"], file_name_write)
    return result["content"]


@mcp.tool(name="Greet")
@safe_tool
def greet(name: str) -> str:
    """Greet a user by name."""
    return f"Hello, {name}! Welcome to the SSE server."


@mcp.tool(name="Add")
@safe_tool
def add(a: int, b: int) -> str:
    """Add two numbers and return the result."""
    return f"The sum of {a} and {b} is {a + b}."


@mcp.resource(uri="resource://hello")
def hello_resource() -> str:
    """Return a greeting resource."""
    return "Hello from the resource!"


def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that serves the MCP server with SSE."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> Response:
        async with sse.connect_sse(request.scope, request.receive, request._send) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )
        return Response(status_code=204)

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )


if __name__ == "__main__":
    mcp_server = mcp._mcp_server  # noqa: SLF001
    starlette_app = create_starlette_app(mcp_server, debug=True)

    uvicorn.run(starlette_app, host="localhost", port=8081)
