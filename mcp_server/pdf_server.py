import functools
import logging
import os

# https://stackoverflow.com/questions/10112244/convert-plain-text-to-pdf-in-python
import textwrap
import traceback
import unicodedata
from collections.abc import Callable
from datetime import datetime
from typing import Any, TypeVar, cast

import uvicorn
from autogen import ConversableAgent
from calendar_functions import convert_ics_to_text, create_ics_file
from dotenv import load_dotenv
from fpdf import FPDF
from mcp.server import Server
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Mount, Route

load_dotenv()
from server_llm_config import Model_type, llm_config

print("Using this LLM model:")
print(llm_config["model"])

pdf_agent = ConversableAgent(
    name="pdf_agent",
    system_message="""Your Job is to assist the user with their tasks.
    """,
    llm_config=llm_config,
    human_input_mode="NEVER",
)
########llm agent setup########

# create the MCP server
mcp = FastMCP("SSE Example Server")


########## Weather agent tools ###############
@mcp.tool(name="create_pdf_file")
def create_pdf_file(prompt: str, file_name: str) -> str:
    try:
        #print(this_will_not_work)#test to try error catching
        print("Using create pdf function")
        # current_date = datetime.now().date()

        agent_prompt = f"""
        Tasks: {prompt}

        Based off what task you are provided you are to follow the following rules on how you will format your response to be created into a PDF file.
        Any time you create a new line it will also create a new line in the text.
        The first line you write will be the title.
        Always keep the title short and concise.
        Do not add any unesisary text such asl clarifications or thank youse only write what you want to add to the file.
        You may use dot points or paragraphs do what you think will look best.
        """

        extracted_details = pdf_agent.generate_reply(messages=[{"role": "user", "content": agent_prompt}])
        print("#####LLM response#####")
        if Model_type == 1:
            LLM_details = extracted_details["content"]
            # print(LLM_details)
        elif Model_type == 2:
            LLM_details = extracted_details
            # print(LLM_details)
        else:
            print("Error within weather_server.py response collection")

        # add .pdf if not included
        if not file_name.endswith(".pdf"):
            file_name = file_name + ".pdf"

        output_filename = f"./pdfs/{file_name}"
        test_text = "This is a test title\nHere is a test paragraph\n\n\nDone\n"
        LLM_details = LLM_details.encode("latin-1", "replace").decode(
            "latin-1"
        )  # fpdf module doesn't support other formats
        print(LLM_details)

        # mkdir pdf folder if it doesn't exist
        if not os.path.exists("./pdfs"):
            os.makedirs("./pdfs")

        def text_to_pdf(text, filename):
            a4_width_mm = 210
            pt_to_mm = 0.35
            fontsize_pt = 10
            fontsize_mm = fontsize_pt * pt_to_mm
            title_font_size = 50
            title_fontsize_mm = title_font_size * pt_to_mm
            margin_bottom_mm = 10
            character_width_mm = 7 * pt_to_mm
            width_text = a4_width_mm / character_width_mm

            pdf = FPDF(orientation="P", unit="mm", format="A4")
            pdf.set_auto_page_break(True, margin=margin_bottom_mm)
            pdf.add_page()
            pdf.set_font(family="Courier", size=fontsize_pt)
            splitted = text.split("\n")
            i = 0
            for line in splitted:
                # print("Am stuck here 1")
                lines = textwrap.wrap(line, width_text)

                if len(lines) == 0:
                    pdf.ln()

                for wrap in lines:
                    # print("Am stuck here 2")
                    if i == 0:
                        pdf.set_font(family="Courier", size=title_fontsize_mm, style="B")
                        pdf.cell(0, title_fontsize_mm, wrap, ln=1, align="C")
                        i = i + 1
                    else:
                        pdf.set_font(family="Courier", size=fontsize_pt)
                        pdf.cell(0, fontsize_mm, wrap, ln=1)
            # print("Am stuck here 3")
            pdf.output(filename, "F")
            # print("Am stuck here 4")

        text_to_pdf(LLM_details, output_filename)  # LLM details is the PDF agents output
        # print("Am stuck here 5")
        print("#####PDF file created")
        result = f"PDF file created: {output_filename}. It has the following content: {LLM_details}. You can confirm with the user that the file has been created."
    except Exception as e:
        print("###Error Reason###")
        print(str(e))
        error = "\n\n Short Error response: " + str(e)
        print("###Full Error###")
        print(traceback.format_exc())
        result = "An error has occurred within the PDF file creator. Please check pdf_server.py or the server terminal output to see what may be causing the issue." + error

    return result


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

    port = 8082

    # run the server using uvicorn
    uvicorn.run(starlette_app, host="localhost", port=port)
