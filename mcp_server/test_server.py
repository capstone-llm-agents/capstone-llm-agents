"""The test server to connect to the LLM MAS client."""

import uvicorn
from mcp.server import Server
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Mount, Route
from jinja2 import Environment, BaseLoader
from datetime import datetime
from xhtml2pdf import pisa
import os
import io


# create the MCP server
mcp = FastMCP("SSE Example Server")


@mcp.tool()
def greet(name: str) -> str:
    """Greet a user by name."""
    return f"Hello, {name}! Welcome to the SSE server."


@mcp.tool()
def add(a: int, b: int) -> str:
    """Add two numbers and return the result."""
    return f"The sum of {a} and {b} is {a + b}."

@mcp.tool()
def create_travel_report(
    title: str = "Travel Report",
    dates: list[str] = ["Not specified"],
    start_location: str = "Not specified",
    destination: str = "Not specified",
    time_taken: str = "Not specified",
    transport_mode: str = "Not specified",
    date_time: str = "Not specified"
) -> str:
    """
    Creates a PDF travel report from structured data, using an embedded HTML template.

    Args:
        title (str): The title of the travel report.
        dates (list[str]): A list of available dates.
        start_location (str): The starting point of the journey.
        destination (str): The final destination.
        time_taken (str): The total duration of the trip.
        transport_mode (str): The primary mode of transportation.
        date_time (str): The specific date and time of the trip.

    Returns:
        str: A message indicating the success or failure of the PDF creation.
    """

    # Define the HTML template as a multi-line string
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <title>Agent Report</title>
    <style>
        body { font-family: serif; }
        h1 { color: green; }
        p { font-size: 12pt; margin-bottom: 5px;}
        h2, h3 { color: navy; margin-top: 20px; margin-bottom: 10px;}
        ul, ol { margin-bottom: 10px;}
        strong { font-weight: bold; }
    </style>
    </head>
    <body>
        <h2>{{ title }}</h2>
        <ol>
            {% for date in dates %}
                <li>{{ date }}</li>
            {% endfor %}
        </ol>
        <h3>Travel Details:</h3>
        <p><strong>Start Location:</strong> {{ start_location }}</p>
        <p><strong>Destination: </strong> {{ destination }}</p>
        <p><strong>Time Taken: </strong> {{ time_taken }}</p>
        <p><strong>Transport Mode: </strong> {{ transport_mode }}</p>
        <p><strong>Date&Time: </strong> {{ date_time }}</p>
    </body>
    </html>
    """

    # Use BaseLoader for an in-memory template
    env = Environment(loader=BaseLoader())
    template = env.from_string(html_template)

    # Render the template with the data provided by the agent
    data_for_template = {
        "title": title,
        "dates": dates,
        "start_location": start_location,
        "destination": destination,
        "time_taken": time_taken,
        "transport_mode": transport_mode,
        "date_time": date_time
    }
    html_content = template.render(data_for_template)
    
    # Set up PDF output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"travel_report_{timestamp}.pdf"
    # Get the directory of the current script
    script_directory = os.path.dirname(os.path.abspath(__file__))
    output_filepath = os.path.join(script_directory, output_filename)
    
    # Create the PDF from the generated HTML
    source_html = io.BytesIO(html_content.encode("utf-8"))
    
    try:
        with open(output_filepath, "w+b") as output_pdf:
            pisa_status = pisa.CreatePDF(
                source_html,
                dest=output_pdf
            )
    except Exception as e:
        return f"Document not created: An error occurred during PDF generation. Error: {e}"
    
    if pisa_status.err:
        return f"Document not created: pisa reported an error."
    else:
        return f"Document created successfully at: {output_filepath}"

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
