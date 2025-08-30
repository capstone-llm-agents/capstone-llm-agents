"""The test server to connect to the LLM MAS client."""

from datetime import datetime

import uvicorn

#####Weather imports#######
import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry
from autogen import ConversableAgent, GroupChat, GroupChatManager, UserProxyAgent
from pytz import timezone
from tzlocal import get_localzone
from datetime import datetime
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Mount, Route
from mcp.server import Server
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport

# functions file
from scripts.test_mcp_weather_functions import generate_weather_data, deduce_weather_result, break_down_result

#####Callender imports#######

########llm agent setup########
llm_config = {
    "api_type": "ollama",
    "model": "gemma3",
}

weather_agent = ConversableAgent(
    name="weather_agent",
    system_message="""Your Job is to assist the user with their tasks.
    """,
    llm_config=llm_config,
    human_input_mode="NEVER",
)
########llm agent setup########

# create the MCP server
mcp = FastMCP("SSE Example Server")


########## Weather agent tools ###############
@mcp.tool()
def obtain_weather_details(prompt):
    try:
        current_date = datetime.now().date()

        agent_prompt = f"""
        Break down the following tasks into the latitude and longitude of the given location as well as the date you would expect to find the weather information.

        Tasks: {prompt}
        Current Date: {current_date}

        If the date requested is not clear assume they are talking about today for both the beginning and the end dates.
        Remember if the user requests for tomorrows weather add a day to the current date.
        Always keep the start date and end date the same for each task.
        Directly and only answer with the follow format:
        Reading) 1
        Location) Paris
        Latitude) -10.6531
        Longitude) 14.2315
        Start date) 2025-02-27
        End date) 2025-02-27
        Time) 15:00

        Reading) 2
        Location) Paris
        Latitude) -10.6531
        Longitude) 14.2315
        Start date) 2025-02-28
        End date) 2025-02-28
        Time) 11:00

        Reading) 3
        Location) London
        Latitude) -20.2187
        Longitude) 27.9102
        Start date) 2025-02-28
        End date) 2025-02-28
        Time) 21:00
        """

        extracted_details = weather_agent.generate_reply(messages=[{"role": "user", "content": agent_prompt}])
        print("#####################################")
        print("Extracted location and date")
        print("#####################################")
        print(extracted_details["content"])

        for line in extracted_details["content"].splitlines():
            if "Latitude)" in line:
                latitude = line.split(") ")[1].strip()
            elif "Longitude)" in line:
                longitude = line.split(") ")[1].strip()
            elif "Start date)" in line:
                start_date = line.split(") ")[1].strip()
            elif "End date)" in line:
                end_date = line.split(") ")[1].strip()
            elif "Time)" in line:
                time = line.split(") ")[1].strip()

        print("\n\n\n")
        print("#####################################")
        print("Generated weather data")
        print("#####################################")
        weather_data = generate_weather_data(latitude, longitude, start_date, end_date)
        print(weather_data)
        print("\n\n\n")

        reformated_weather_data = break_down_result(weather_data, time)
        print(reformated_weather_data)

        result = deduce_weather_result(prompt, reformated_weather_data)
        #print(result)
    except:
        result = "An error has occurred. make sure the date range is no more than 16 days past today. If this is not the issue than it will likely be somewhere in the system"#temporary error catching

    return result
########## Weather agent tools ###############


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
