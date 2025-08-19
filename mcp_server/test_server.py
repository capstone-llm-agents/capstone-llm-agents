"""The test server to connect to the LLM MAS client."""

import uvicorn
from mcp.server import Server
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Mount, Route
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
def document_creator(content: str, base_filename: str ="report") -> str:
    """
    Create a PDF travel plan document based on the template provided
    Template Structure:
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
        <h2>[Fill Title Here]</h2>
        <ol>
            [Create list items <li> for available dates here]
        </ol>
        <h3>Travel Details:</h3>
        <p><strong>Start Location:</strong> [Fill Start Location Here]</p>
        <p><strong>Destination: </strong> [Fill Destination Here]</p>
        <p><strong>Time Taken: </strong> [Fill Time Taken Here]</p>
        <p><strong>Transport Mode: </strong> [Fill Transport Mode Here]</p>
        <p><strong>Date&Time: </strong> [Fill Date & Time Here]</p>
    </body>
    </html>
    """
    print("📄 DOCUMENT_CREATOR TOOL CALLED")
    print(content[:100])  # Preview
    main_content = content
    print("being called")
    script_path = os.path.abspath(__file__)

    script_directory = os.path.dirname(script_path)
    print("script directory")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"{base_filename}_{timestamp}.pdf"
    print("filename")
    output_filepath = os.path.join(script_directory, output_filename)
    print("filepath")

    source_html = io.BytesIO(content.encode("utf-8"))
    print("sourcehtml")
    with open(output_filepath, "w+b") as output_pdf:
            pisa_status = pisa.CreatePDF(
                source_html,
                dest=output_pdf
            )
    print ("open pdf")        

    if not pisa_status.err:
        return 'Document Created'
    else:
        return 'Document not created'

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
