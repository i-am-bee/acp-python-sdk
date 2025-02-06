from typing import Any, Awaitable, Callable, Type

from pydantic import BaseModel, Field

from mcp.server.fastmcp.agents.base import Agent
from mcp.server.fastmcp.server import Context


class AgentTemplate(BaseModel):
    """A template for creating agents."""

    name: str = Field(description="Name of the agent")
    description: str | None = Field(description="Description of what the agent does")

    config: Type[BaseModel] = Field(description="Model for config")
    input: Type[BaseModel] = Field(description="Model for run input")
    output: Type[BaseModel] = Field(description="Model for run output")

    create_fn: Callable[[dict[str, Any], Context], Awaitable[Agent]] = Field(
        exclude=True
    )
