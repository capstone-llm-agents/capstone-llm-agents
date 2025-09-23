"""The test server to connect to the LLM MAS client."""

from datetime import datetime

import uvicorn
from autogen import ConversableAgent
from mcp.server import Server
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Mount, Route
import os

# functions file
from weather_functions import break_down_result, deduce_weather_result, generate_weather_data
import os
from dotenv import load_dotenv

load_dotenv()
########llm agent setup########
Model_type = 2 #use 1 for gemma3 or 2 for openai

if Model_type == 1:
    llm_config = {
        "api_type": "ollama",
        "model": "gemma3",
    }
elif Model_type == 2:
    llm_config = {
        "api_type": "openai",
        "model": "gpt-4o-mini",
        "api_key": os.environ.get("OPENAI_API_KEY"),
    }
else:
    print("No model has been selected in weather_server.py")

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
@mcp.tool(name="ObtainWeatherDetails")
def obtain_weather_details(prompt):
    try:
        current_date = datetime.now().date()

        agent_prompt = f"""
        Break down the following tasks into the latitude and longitude of the given location as well as the date you would expect to find the weather information.

        Tasks: {prompt}
        Current Date: {current_date}

        If the date requested is not clear assume they are talking about today for both the beginning and the end dates.
        Remember if the user requests for tomorrows weather add a day to the current date. Likewise if they specify a date use that for the start and end dates.
        Always keep the start date and end date the same for each task.
        If no time is provided use 12:00
        Directly and only answer with the follow format:
        Reading) 1
        Location) Ottawa
        Latitude) -10.6531
        Longitude) 14.2315
        Start date) yyyy-mm-dd
        End date) yyyy-mm-dd
        Time) 15:00

        Reading) 2
        Location) Rosedale
        Latitude) -20.2187
        Longitude) 27.9102
        Start date) yyyy-mm-dd
        End date) yyyy-mm-dd
        Time) 21:00
        """

        extracted_details = weather_agent.generate_reply(messages=[{"role": "user", "content": agent_prompt}])
        print("#####################################")
        print("Extracted location and date")
        print("#####################################")
        if Model_type == 1:
            LLM_details = extracted_details["content"]
            print(LLM_details)
        elif Model_type == 2:
            LLM_details = extracted_details
            print(LLM_details)
        else:
            print("Error within weather_server.py response collection")

        # This array will be used to store each/how many readings need to be looped through the function
        all_locations = []

        time = None
        for line in LLM_details.splitlines():
            if "Reading)" in line:
                reading = line.split(") ")[1].strip()
            elif "Location)" in line:
                location = line.split(") ")[1].strip()
            elif "Latitude)" in line:
                latitude = line.split(") ")[1].strip()
            elif "Longitude)" in line:
                longitude = line.split(") ")[1].strip()
            elif "Start date)" in line:
                start_date = line.split(") ")[1].strip()
            elif "End date)" in line:
                end_date = line.split(") ")[1].strip()
            elif "Time)" in line:
                time = line.split(") ")[1].strip()
            if time != None:  # if time is assigned a value save all data read so far and reset variables
                all_locations.append([reading, location, latitude, longitude, start_date, end_date, time])
                reading = None
                location = None
                latitude = None
                longitude = None
                start_date = None
                end_date = None
                time = None

        print(all_locations)
        combined_weather_data = []
        for locations in all_locations:
            print("\n\n\n")
            print("#####################################")
            print("Generated weather data")
            print("#####################################")
            weather_data = generate_weather_data(locations[2], locations[3], locations[4], locations[5])
            print(weather_data)
            print("\n\n\n")

            reformated_weather_data = break_down_result(weather_data, locations[6], locations[1])
            print(reformated_weather_data)

            ######could potentially remove this part and just use simple response to work it out maybe?#########
            resulting_weather_reading = deduce_weather_result(prompt, reformated_weather_data)
            combined_weather_data.append(resulting_weather_reading)
            # combined_weather_data.append(reformated_weather_data)#Option 2 just the raw data
        # print(combined_weather_data)
        result = ""
        for data in combined_weather_data:
            result = result + "\n\n" + data
        print("########Final Result########")
        print(result)
    except:
        result = "An error has occurred. make sure the date range is no more than 16 days past today. If this is not the issue than it will likely be somewhere in the system"  # temporary error catching

    return result


########## Weather agent tools ###############


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
