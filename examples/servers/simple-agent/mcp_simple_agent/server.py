from mcp.server.fastmcp.agents import Agent
from pydantic import BaseModel
import anyio
import click
import mcp.types as types
from mcp.server.fastmcp import FastMCP

class Input(BaseModel):
    prompt: str

class Output(BaseModel):
    text: str

@click.command()
@click.option("--port", default=8000, help="Port to listen on for SSE")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type",
)
def main(port: int, transport: str) -> int:
    server = FastMCP("mcp-agent")

    # Use agent decorator
    @server.agent('Someagent', 'This is just some agent', input=Input, output=Output)
    async def run_someagent(input: Input) -> Output:
        agent = 'someagent' # some framework agent
        return Output(
            text=f"{agent}: {input.prompt} + cont."
        )
    
    async def run_anotheragent(input: Input) -> Output:
        agent = 'anotheragent' # some framework agent
        return Output(
            text=f"{agent}: {input.prompt} + cont."
        )
    
    # Use add_agent
    server.add_agent(agent=Agent(
        name="Anotheragent",
        description='This is just another agent',
        input=Input,
        output=Output,
        run_fn=run_anotheragent
    ))

    if transport == "sse":
        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.routing import Mount, Route

        sse = SseServerTransport("/messages/")

        async def handle_sse(request):
            async with sse.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await server.run(
                    streams[0], streams[1], server.create_initialization_options()
                )

        starlette_app = Starlette(
            debug=True,
            routes=[
                Route("/sse", endpoint=handle_sse),
                Mount("/messages/", app=sse.handle_post_message),
            ],
        )

        import uvicorn

        uvicorn.run(starlette_app, host="0.0.0.0", port=port)
    else:
        from mcp.server.stdio import stdio_server

        async def arun():
            async with stdio_server() as streams:
                await server.run(
                    streams[0], streams[1], server.create_initialization_options()
                )

        anyio.run(arun)

    return 0
