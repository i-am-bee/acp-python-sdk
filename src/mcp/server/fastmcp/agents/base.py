from typing import TYPE_CHECKING, Any, Awaitable, Callable, Type

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from mcp.server.fastmcp.server import Context


class Agent(BaseModel):
    """Internal agent info."""

    name: str = Field(description="Name of the agent")
    description: str | None = Field(description="Description of what the agent does")

    input: Type[BaseModel] = Field(description="Model for input")
    output: Type[BaseModel] = Field(description="Model for output")

    run_fn: Callable[[dict[str, Any], "Context"], Awaitable[dict[str, Any]]] = Field(
        exclude=True
    )
    destroy_fn: Callable[["Context"], Awaitable[None]] | None = Field(exclude=True)

    model_config = ConfigDict(extra="allow")
