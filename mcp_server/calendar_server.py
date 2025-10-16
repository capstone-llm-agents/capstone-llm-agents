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

from dotenv import load_dotenv

load_dotenv()
from server_llm_config import Model_type, llm_config

print("Using this LLM model:")
print(llm_config["model"])

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


@mcp.tool(name="Create_ICS_Calendar/Schedule")
@safe_tool
def create_ics_calendar(prompt: str, ics_file: str = "./calendars/my_calendar.ics") -> str:
    """Generate a calendar schedule from a task prompt and write it to an ICS file."""
    print("###Using CreateCalendar###")
    current_date = datetime.now().date()

    prompt = f"""
    Break down the following tasks into realistic time frames, using the provided start time as a reference.

    Tasks: {prompt}
    Current Date: {current_date}

    Respond with a schedule in a structured format suitable for creating a calendar file (e.g., Task Name, Description, Start Time, End Time).
    Use 24 hour notation for times to make it unambiguous.
    Only give a date if specified by either the Tasks or Preferences otherwise use the current date instead
    Do not add any additional tasks the user has not asked for.
    Directly and only answer with the follow format:
    1. Task: Research for Report
    Date: 2022-07-13
    Description: Research reliable details online
    Start: 09:00
    End: 09:30

    2. Task: Write Draft
    Date: 2022-07-13
    Description: Handwritten research report about computers
    Start: 09:30
    End: 10:00
    ...
    """

    plan = file_handler_agent.generate_reply(messages=[{"role": "user", "content": prompt}])
    #different formats depending on which LLM is used
    if Model_type == 1:
        LLM_result = plan["content"]
        print(LLM_result)
        creation_result = create_ics_file(LLM_result, ics_file)
        if creation_result[0] == 1:#checks if there has been an issue within the create ics file function
            LLM_result = "There has been an error within the create ics file function. This could be due to using the wrong format or some other issue found within the calender server/functions."
            print(LLM_result)
    elif Model_type == 2:
        LLM_result = plan
        print(LLM_result)
        creation_result = create_ics_file(LLM_result, ics_file)
        if creation_result[0] == 1:#checks if there has been an issue within the create ics file function
            LLM_result = "There has been an error within the create ics file function. This could be due to using the wrong format or some other issue found within the calender server/functions."
            print(LLM_result)
    else:
        print("Error with which model has been selected. please check the server_llm_config.py file to ensure correct LLM configuration")
        LLM_result = "Error with which model has been selected. please check the server_llm_config.py file to ensure correct LLM configuration"
    return LLM_result


@mcp.tool(name="Read_ICS_Calendar/Schedule")
@safe_tool
def read_calendar(file_name: str = "./calendars/my_calendar.ics") -> str:
    """Read an ICS file and return a human-readable task list."""
    print("###Using ReadCalendar###")
    calendar_content = convert_ics_to_text(file_name)
    if calendar_content[0] == 1:
        LLM_result = "There has been an error with converting the ics calendar file to text. this either means a calendar file does not exist or is misconfigured."
        print(LLM_result)
    else:
        prompt = f"""
        You are to explain what the date, tasks and times are based off this ics calender.

        calender content: {calendar_content}

        Respond with a list of each task and their related time for the date provided. also convert the time to 24 hour format such as 16:15 pm.
        Make sure to convert these times from UCD to the provided timezone.
        Follow the example format bellow and do not add anything else.
        EXAMPLE:
        1. Task: Research for Report
        Date: 2022-07-13
        Description: Research reliable details online
        Start: 09:00
        End: 09:30

        2. Task: Write Draft
        Date: 2022-07-13
        Description: Handwritten research report about computers
        Start: 09:30
        End: 10:00
        """

        result = file_handler_agent.generate_reply(messages=[{"role": "user", "content": prompt}])
        #different formats depending on which LLM is used
        if Model_type == 1:
            LLM_result = result["content"]
            print(LLM_result)
        elif Model_type == 2:
            LLM_result = result
            print(LLM_result)
        else:
            print("Error with which model has been selected. please check the server_llm_config.py file to ensure correct LLM configuration")
            LLM_result = "Error with which model has been selected. please check the server_llm_config.py file to ensure correct LLM configuration"
    return LLM_result


@mcp.tool(name="Update_ICS_Calendar/Schedule")
def create_ics_calendar_with_context(
    prompt: str,
    file_name_read: str = "./calendars/my_calendar.ics",
    file_name_write: str = "./calendars/my_calendar.ics",
) -> str:
    """Create a new calendar schedule considering existing events."""
    print("###Using UpdateCalendar###")
    current_date = datetime.now().date()
    existing_events = convert_ics_to_text(file_name_read)
    if existing_events[0] == 1:
        LLM_result = "There was an error converting the ics file to text. this means either the ics file is misconfigured or does not exist. To fix this issue try using the create calendar tool first to reset or create your calendar."
        print(LLM_result)
    else:
        extracted_prompt = f"""
        Break down the following tasks into realistic time frames, using the provided start time as a reference.

        Tasks: {prompt}
        Current Date: {current_date}
        Pre Existing Plans: {existing_events}

        Respond with a schedule in a structured format suitable for creating a calendar file (e.g., Task Name, Description, Start Time, End Time).
        Use 24 hour notation for times to make it unambiguous.
        Only give a date if specified by either the Tasks or Preferences otherwise use the current date instead
        Do not clash any new schedules with pre existing plans.
        Make sure to add all pre existing plans to this new schedule.
        Directly and only answer with the follow format:
        1. Task: Research for Report
        Date: 2022-07-13
        Description: Research reliable details online
        Start: 09:00
        End: 09:30

        2. Task: Write Draft
        Date: 2022-07-13
        Description: Handwritten research report about computers
        Start: 09:30
        End: 10:00
        ...
        """
        #print("made it here for the update calendar")
        result = file_handler_agent.generate_reply(messages=[{"role": "user", "content": extracted_prompt}])
        if Model_type == 1:
            LLM_result = result["content"]
            print(LLM_result)
            creation_result = create_ics_file(LLM_result, file_name_write)
            if creation_result[0] == 1:
                LLM_result = "There has been an error within the create ics file function. This could be due to using the wrong format or some other issue found within the calender server/functions."
                print(LLM_result)
        elif Model_type == 2:
            LLM_result = result
            print(LLM_result)
            creation_result = create_ics_file(LLM_result, file_name_write)
            if creation_result[0] == 1:
                LLM_result = "There has been an error within the create ics file function. This could be due to using the wrong format or some other issue found within the calender server/functions."
                print(LLM_result)
        else:
            print("Error with which model has been selected. please check the server_llm_config.py file to ensure correct LLM configuration")
            LLM_result = "Error with which model has been selected. please check the server_llm_config.py file to ensure correct LLM configuration"
    return LLM_result


def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that serves the MCP server with SSE."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> Response:
        async with sse.connect_sse(request.scope, request.receive, request._send) as (read_stream, write_stream):  # noqa: SLF001
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
