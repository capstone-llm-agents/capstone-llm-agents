"""The test server to connect to the LLM MAS client."""

import uvicorn
from mcp.server import Server
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Mount, Route


#####Callender imports#######
from autogen import ConversableAgent, UserProxyAgent
from autogen import GroupChat
from autogen import GroupChatManager

from pydantic import BaseModel

from openai import OpenAI
from ics import Calendar, Event
from datetime import datetime
from dotenv import load_dotenv
from pytz import timezone
from tzlocal import get_localzone

from icalendar import Calendar as Calendar2

#functions file
from scripts.test_callender_functions import convert_ics_to_text, create_ics_file
#####Callender imports#######

########llm agent setup########
llm_config = {
    "api_type": "ollama",
    "model": "gemma3",
}

file_handler_agent = ConversableAgent(
    name="file_handler",
    system_message="""Your Job is to assist the user with their tasks.
    """,
    llm_config=llm_config,
    human_input_mode="NEVER",
)
########llm agent setup########

# create the MCP server
mcp = FastMCP("SSE Example Server")

########## Callender agent tools ###############
@mcp.tool()
#Takes in a users request or potentialy a formated request by another LLM agent and then the file_handeler agent converts it into what it belives would be the best names, descriptions times etc.
def create_ics_callender(tasks: str, ics_file) -> str:
    current_date = datetime.now().date()

    prompt = f"""
    Break down the following tasks into realistic time frames, using the provided start time as a reference.

    Tasks: {tasks}
    Current Date: {current_date}

    Respond with a schedule in a structured format suitable for creating a calendar file (e.g., Task Name, Description, Start Time, End Time).
    Use 24 hour notation for times to make it unambiguous.
    Only give a date if specified by either the Tasks or Preferences otherwise use the current date instead
    Directly and only answer with the follow format:
    1. Task: Research for Report
    Date: 2022-07-13
    Description: Research reliable details online
    Start: 09:00
    End: 09:30

    2. Task: Write Draft
    Date: 2022-07-13
    Description: Handwriten reaserch report about computers
    Start: 09:30
    End: 10:00
    ...
    """

    formated_plan = file_handler_agent.generate_reply(messages=[{"role": "user", "content": prompt}])
    print("#####################################")
    print("New callender dates content")
    print("#####################################")
    print(formated_plan["content"])

    create_ics_file(formated_plan["content"], ics_file)

    return formated_plan["content"]

@mcp.tool()
#This function first converts a specified ics file to text from which the LLM agent formats its content into readable text
def read_calender(file_name) -> str:
    calender_content = convert_ics_to_text(file_name)

    prompt = f"""
    You are to explain what the date, tasks and times are based off this ics calender.

    calender content: {calender_content}

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
    Description: Handwriten reaserch report about computers
    Start: 09:30
    End: 10:00
    """

    result = file_handler_agent.generate_reply(messages=[{"role": "user", "content": prompt}])
    print("#####################################")
    print("Read calender interpretation")
    print("#####################################")
    print(result["content"])
    return result["content"]

@mcp.tool()
#this function takes in a user/agent task creation request as well as a ics file to consider when making a new scedual and a new one to write an updated scedual to.
def create_ics_callender_with_context(tasks: str, file_name_read, file_name_write):
    current_date = datetime.now().date()
    calender_dates = convert_ics_to_text(file_name_read)

    #uses the extracted calender dates to create a new scedual.
    extracted_prompt = f"""
    Break down the following tasks into realistic time frames, using the provided start time as a reference.

    Tasks: {tasks}
    Current Date: {current_date}
    Pre Existing Plans: {calender_dates}

    Respond with a schedule in a structured format suitable for creating a calendar file (e.g., Task Name, Description, Start Time, End Time).
    Use 24 hour notation for times to make it unambiguous.
    Only give a date if specified by either the Tasks or Preferences otherwise use the current date instead
    Do not clash any new sceduals with pre existing plans.
    Make sure to add all pre existing plans to this new scedual.
    Directly and only answer with the follow format:
    1. Task: Research for Report
    Date: 2022-07-13
    Description: Research reliable details online
    Start: 09:00
    End: 09:30

    2. Task: Write Draft
    Date: 2022-07-13
    Description: Handwriten reaserch report about computers
    Start: 09:30
    End: 10:00
    ...
    """
    result = file_handler_agent.generate_reply(messages=[{"role": "user", "content": extracted_prompt}])
    print("#####################################")
    print("New callender dates content")
    print("#####################################")
    print(result["content"])

    #creates new scedual here
    create_ics_file(result["content"], file_name_write)


    return result["content"]
########## Callender agent tools ###############

@mcp.tool()
def greet(name: str) -> str:
    """Greet a user by name."""
    return f"Hello, {name}! Welcome to the SSE server."


@mcp.tool()
def add(a: int, b: int) -> str:
    """Add two numbers and return the result."""
    return f"The sum of {a} and {b} is {a + b}."


# example resource
@mcp.resource(uri="resource://hello")
def hello_resource() -> str:
    """Return a greeting."""
    return "Hello from the resource!"


def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that can serve the MCP server with SSE."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> Response:
        async with sse.connect_sse(
            request.scope,
            request.receive,
            request._send,  # noqa: SLF001 (request._send is a private method, but needed for Starlette's internal use)
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

        # 204 - No Content response
        # This is to indicate that the SSE connection is established and no immediate response is needed.
        return Response(status_code=204)

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )


if __name__ == "__main__":
    # get the underlying MCP server so we can give it to Starlette
    mcp_server = mcp._mcp_server  # noqa: SLF001

    # create Starlette app with SSE support
    starlette_app = create_starlette_app(mcp_server, debug=True)

    port = 8080

    # run the server using uvicorn
    uvicorn.run(starlette_app, host="localhost", port=port)
